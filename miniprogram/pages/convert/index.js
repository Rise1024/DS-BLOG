const app = getApp()
Page({
  data: {
    markdownContent: '',
    previewImages: [],
    isConverting: false,
    isSavingAll: false,
    selectedStyle: 'carbon',
    watermarkText: '',
    enableWatermark: false,
    previewImage: '', // 添加预览图片URL
    articleId: '', // 添加文章标识
    progress: 0,
    showProgress: false,// 控制进度条的显示
    stylePresets: [
      { id: 'carbon', name: 'Carbon风格' },
      { id: 'xiaohongshu', name: '小红书风格' },
      { id: 'notion', name: 'Notion风格' }
    ]
  },

  onLoad(options) {
    // 页面加载时生成新的文章标识
    this.setData({
    })
    
    // 新增参数接收
    if (options.markdown) {
      this.setData({
        markdownContent: decodeURIComponent(options.markdown)
      });
    }
  },

  // 处理样式切换
  handleStyleChange(e) {
    this.setData({
      selectedStyle: e.detail.value
    });
  },

  // 切换水印启用状态
  toggleWatermark() {
    this.setData({
      enableWatermark: !this.data.enableWatermark
    });
  },

  // 处理水印文本输入
  handleWatermarkInput(e) {
    this.setData({
      watermarkText: e.detail.value
    });
  },

  // 更新预览图片
  // 进度条动画
  startProgressAnimation() {
    let progress = 0
    const animationInterval = setInterval(() => {
      if ((this.data.isConverting || this.data.isPreviewing) && progress < 90) {
        progress += Math.round(Math.random() * 3 + 1) // 更平滑的进度增长（取整避免小数）
        this.setData({
          progress: Math.round(Math.min(progress, 90)), // 确保显示整数百分比
          showProgress: true // 显示进度条
        })
      } else {
        clearInterval(animationInterval)
        if (!this.data.isConverting && !this.data.isPreviewing) {
          this.setData({
            showProgress: false // 隐藏进度条
          })
        }
      }
    }, 150) // 缩短间隔使动画更流畅
  },

  async updatePreview() {
    const app = getApp();
    this.setData({ 
      isPreviewing: true,
      showProgress: true,
      progress: 0
    });
    
    // 启动进度条动画
    this.startProgressAnimation();
    try {
      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.serverUrl}/preview`,
          method: 'POST',
          header: {
            'Authorization': wx.getStorageSync('token')
          },
          data: {
            content: this.data.markdownContent || '# 预览示例\n这是一段示例文本，用于预览当前选择的样式效果。',  // 使用用户输入的内容，如果为空则使用示例
            style: this.data.selectedStyle,
            watermark: this.data.enableWatermark ? this.data.watermarkText : '',
            user_id: wx.getStorageSync('userId') || 'anonymous',
            article_id: new Date().getTime().toString()
          },
          success: resolve,
          fail: reject
        });
      });

      if (response.data && response.data.success && response.data.images.length > 0) {
        // 为每个图片URL添加时间戳参数
        const timestamp = new Date().getTime();
        const updatedImages = response.data.images.map(url => `${url}?t=${timestamp}`);
        
        this.setData({
          previewImage: updatedImages[0],
          previewImages: [],
          progress: 100
        });
      } else {
        throw new Error(response.data ? response.data.error : '预览失败');
      }
    } catch (error) {
      console.error('预览更新失败:', error);
      wx.showToast({
        title: '网络开小差了,再来一次',
        icon: 'none'
      });
    } finally {
      this.setData({ 
        isPreviewing: false,
        showProgress: false
      });
    }
  },

  // 处理Markdown内容输入
  handleInput(e) {
    this.setData({
      markdownContent: e.detail.value
    })
  },

  // 转换Markdown为图片
  async convertToImages() {
    // 检查登录状态
    if (!app.checkLoginStatus()) {
      wx.switchTab({
        url: '/pages/index/index'
      });
      return;
    }
    
    if (!this.data.markdownContent.trim()) {
      wx.showToast({
        title: '请输入Markdown内容',
        icon: 'none'
      })
      return
    }

    this.setData({ 
      isConverting: true,
      showProgress: true,
      progress: 0
    })

    // 启动进度条动画
    this.startProgressAnimation()

    try {
      const app = getApp()
      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.serverUrl}/convert`,
          method: 'POST',
          header: {
            'Authorization': wx.getStorageSync('token')
          },
          data: {
            content: this.data.markdownContent,
            style: this.data.selectedStyle,
            watermark: this.data.enableWatermark ? this.data.watermarkText : '',  // 只在启用水印时发送水印文本
            user_id: wx.getStorageSync('userId') || 'anonymous',
            article_id: new Date().getTime().toString()
          },
          success: resolve,
          fail: reject
        })
      })

      if (response.data && response.data.success) {
        this.setData({
          previewImages: response.data.images,
          progress: 100
        })
      } else {
        throw new Error(response.data ? response.data.error : '网络开小差了,再来一次')
      }
    } catch (error) {
      wx.showToast({
        title: '网络开小差了,再来一次',
        icon: 'none'
      })
    } finally {
      this.setData({ 
        isConverting: false,
        showProgress: false
      })
    }
  },

  // 预览图片
  previewImage(e) {
    const current = e.currentTarget.dataset.src
    wx.previewImage({
      current,
      urls: this.data.previewImages
    })
  },

  // 下载单张图片到相册
  async downloadImage(e) {
    const imageSrc = e.currentTarget.dataset.src
    await this.saveImageToAlbum(imageSrc)
  },

  // 批量下载所有图片
  async downloadAllImages() {
    if (this.data.isSavingAll || !this.data.previewImages.length) return

    this.setData({ isSavingAll: true })
    const totalImages = this.data.previewImages.length

    try {
      // 检查相册权限
      const auth = await wx.getSetting()
      if (!auth.authSetting['scope.writePhotosAlbum']) {
        await wx.authorize({
          scope: 'scope.writePhotosAlbum'
        })
      }

      // 使用Promise.all并行处理图片保存
      wx.showLoading({
        title: '正在批量保存图片',
        mask: true
      })

      const savePromises = this.data.previewImages.map((imageSrc, index) => 
        new Promise(async (resolve, reject) => {
          try {
            await this.saveImageToAlbum(imageSrc, false)
            // 更新进度
            wx.showLoading({
              title: `已保存 ${index + 1}/${totalImages}`,
              mask: true
            })
            resolve()
          } catch (error) {
            reject(error)
          }
          // 添加短暂延时，避免请求过于密集
          await new Promise(r => setTimeout(r, 500))
        })
      )

      await Promise.all(savePromises)

      wx.hideLoading()
      wx.showToast({
        title: `已成功保存${totalImages}张图片`,
        icon: 'success',
        duration: 2000
      })
    } catch (error) {
      wx.hideLoading()
      if (error.errMsg && error.errMsg.includes('authorize:fail')) {
        wx.showModal({
          title: '提示',
          content: '需要您授权保存到相册',
          success: (res) => {
            if (res.confirm) {
              wx.openSetting()
            }
          }
        })
      } else {
        wx.showToast({
          title: '保存失败，请重试',
          icon: 'none'
        })
        console.error('保存图片失败:', error)
      }
    } finally {
      this.setData({ isSavingAll: false })
    }
  },

  // 保存单张图片到相册的通用方法
  async saveImageToAlbum(imageSrc, showToast = true) {
    try {
      // 下载图片
      const tempFilePath = await new Promise((resolve, reject) => {
        wx.downloadFile({
          url: imageSrc,
          success: res => resolve(res.tempFilePath),
          fail: reject
        })
      })

      // 保存到相册
      await wx.saveImageToPhotosAlbum({
        filePath: tempFilePath
      })

      if (showToast) {
        wx.showToast({
          title: '保存成功',
          icon: 'success'
        })
      }
    } catch (error) {
      throw error
    }
  }
})