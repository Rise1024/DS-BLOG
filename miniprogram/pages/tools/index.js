//获取应用实例
const app = getApp();
Page({
	data: {
		isLoading: true,
		article: {},
		rssList: [],
		selectedRssName: '',
		selectedRssIndex: 0,
    rawMarkdown: '',
    showOutline: false,
    currentHeading: null,
    headings: []
	},
	onLoad: function () {
    const that = this;
    this.setData({ isLoading: true });

    // 先获取RSS配置列表
    wx.request({
      url: `${app.globalData.serverUrl}/rss`,
      success(res) {
        if (res.statusCode === 200 && res.data) {
          that.setData({
            rssList: res.data,
            selectedRssName: res.data[0]?.name || ''
          });
          that.loadRssData();
        }
      },
      fail(err) {
        console.error('获取配置失败', err);
        that.setData({ isLoading: false });
      }
    });
  },

  loadRssData: function() {
    const that = this;
    wx.request({
      url: `${app.globalData.serverUrl}/rss/${this.data.selectedRssName}`,
      success(res) {
        if (res.statusCode === 200 && res.data) {
          const result = app.towxml(res.data, 'markdown', {
            theme: 'light',
            events: { tap: (e) => { console.log('tap', e); } }
          });
          
          // 从markdown内容提取标题
          const headings = that.extractHeadingsFromMarkdown(res.data);
          
          // 保存原始markdown内容
          that.setData({ 
            article: result, 
            isLoading: false,
            rawMarkdown: res.data,
            headings: headings
          });
        }
      },
      fail(err) {
        console.error('请求失败', err);
        that.setData({ isLoading: false });
      }
    });
  },
  handleRssChange: function(e) {
    this.setData({
      selectedRssName: this.data.rssList[e.detail.value].name,
      selectedRssIndex: e.detail.value,
      isLoading: true
    });
    this.loadRssData();
  },
  // 新增分享按钮事件处理
  handleShareImage: function() {
    if (!this.data.rawMarkdown) {
      wx.showToast({ title: '请先加载内容', icon: 'none' });
      return;
    }
    
    // 检查登录状态
    if (!app.checkLoginStatus()) {
      // 如果未登录，跳转到登录页面
      wx.switchTab({
        url: '/pages/index/index'
      });
      return;
    }
    
    wx.navigateTo({
      url: `/pages/convert/index?markdown=${encodeURIComponent(this.data.rawMarkdown)}`
    });
  },

  // 从markdown内容提取标题
  extractHeadingsFromMarkdown(markdown) {
    const headings = [];
    const lines = markdown.split('\n');
    
    lines.forEach((line, index) => {
      const trimmedLine = line.trim();
      
      // 1. 匹配markdown标题格式 # ## ### #### ##### ######
      const headingMatch = trimmedLine.match(/^(#{1,6})\s+(.+)$/);
      if (headingMatch) {
        const level = headingMatch[1].length;
        const title = headingMatch[2].trim();
        const anchor = `heading-${headings.length}`;
        
        headings.push({
          level: level,
          title: title,
          anchor: anchor,
          line: index
        });
        return;
      }
      
      // 2. 匹配数字列表项 1. 2. 3.
      const numberedListMatch = trimmedLine.match(/^(\s*)(\d+\.)\s+(.+)$/);
      if (numberedListMatch) {
        const indent = numberedListMatch[1].length;
        const title = numberedListMatch[3].trim();
        
        // 根据缩进确定层级（每2个空格为一级）
        const level = Math.min(6, Math.floor(indent / 2) + 4);
        
        if (title.length > 0) {
          const anchor = `heading-${headings.length}`;
          
          headings.push({
            level: level,
            title: `${numberedListMatch[2]} ${title}`,
            anchor: anchor,
            line: index
          });
        }
        return;
      }
      
      // 3. 匹配中文序号 一、 二、 三、 四、 五、 六、 七、 八、 九、 十、
      const chineseNumberMatch = trimmedLine.match(/^(\s*)([一二三四五六七八九十]+)、\s*(.+)$/);
      if (chineseNumberMatch) {
        const indent = chineseNumberMatch[1].length;
        const title = chineseNumberMatch[3].trim();
        
        // 根据缩进确定层级（每2个空格为一级）
        const level = Math.min(6, Math.floor(indent / 2) + 4);
        
        if (title.length > 0) {
          const anchor = `heading-${headings.length}`;
          
          headings.push({
            level: level,
            title: `${chineseNumberMatch[2]}、${title}`,
            anchor: anchor,
            line: index
          });
        }
        return;
      }
    });
    
    return headings;
  },

  // 切换大纲显示状态
  toggleOutline() {
    this.setData({
      showOutline: !this.data.showOutline
    });
  },

  // 关闭大纲
  closeOutline() {
    this.setData({
      showOutline: false
    });
  },

  // 滚动到指定标题
  scrollToHeading(e) {
    const anchor = e.currentTarget.dataset.anchor;
    const title = e.currentTarget.dataset.title;
    if (!anchor || !title) return;

    // 关闭大纲
    this.setData({
      showOutline: false
    });

    // 使用页面高度估算跳转
    this.scrollToHeadingByPageHeight(anchor, title);
  },

  // 通过页面高度估算跳转
  scrollToHeadingByPageHeight(anchor, title) {
    const headingsData = this.data.headings;
    const targetHeading = headingsData.find(h => h.anchor === anchor);
    
    if (targetHeading) {
      const targetIndex = headingsData.indexOf(targetHeading);
      const totalHeadings = headingsData.length;
      
      // 获取页面总高度
      const query = wx.createSelectorQuery();
      query.selectViewport().scrollOffset();
      query.exec((res) => {
        if (res[0]) {
          const scrollHeight = res[0].scrollHeight;
          
          // 根据标题索引估算位置
          const estimatedScrollTop = Math.floor((targetIndex / totalHeadings) * scrollHeight);
          
          console.log('使用页面高度估算 - 目标索引:', targetIndex, '总标题数:', totalHeadings, '页面高度:', scrollHeight, '估算位置:', estimatedScrollTop);
          
          // 平滑滚动到估算位置
          wx.pageScrollTo({
            scrollTop: estimatedScrollTop,
            duration: 500
          });

          // 更新当前阅读位置
          this.setData({
            currentHeading: anchor
          });
          
          console.log('页面高度估算跳转成功:', targetHeading.title);
        } else {
          // 最后的备用方案：滚动到页面中间
          wx.pageScrollTo({
            scrollTop: 500,
            duration: 300
          });
          wx.showToast({
            title: '跳转到页面中部',
            icon: 'none'
          });
        }
      });
    } else {
      wx.showToast({
        title: '跳转失败',
        icon: 'none'
      });
    }
  },

  // 监听页面滚动，更新当前阅读位置
  onPageScroll(e) {
    if (!this.data.headings || this.data.headings.length === 0) {
      return;
    }

    const scrollTop = e.scrollTop;
    const headings = this.data.headings;
    
    // 查找当前应该高亮的标题
    let currentHeading = null;
    for (let i = headings.length - 1; i >= 0; i--) {
      const heading = headings[i];
      const query = wx.createSelectorQuery();
      query.select(`#${heading.anchor}`).boundingClientRect();
      query.exec((res) => {
        if (res[0] && res[0].top <= 150) {
          if (heading.anchor !== this.data.currentHeading) {
            this.setData({
              currentHeading: heading.anchor
            });
          }
          return;
        }
      });
    }
  }
  
})