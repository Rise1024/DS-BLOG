const app = getApp();

Page({
  data: {
    isLoading: true,
    error: '',
    article: null,
    articleContent: null,
    showOutline: false,
    currentHeading: null
  },

  onLoad(options) {
    const { id } = options;
    if (id) {
      this.loadArticle(decodeURIComponent(id));
    } else {
      this.setData({ 
        isLoading: false, 
        error: '文章ID不能为空' 
      });
    }
  },

  // 加载文章详情
  loadArticle(articleId) {
    console.log('开始加载文章:', articleId);
    
    const serverUrl = app.globalData.serverUrl || 'http://localhost:5000';
    const url = `${serverUrl}/api/blog/articles/${encodeURIComponent(articleId)}`;
    console.log('请求URL:', url);

    wx.request({
      url: url,
      method: 'GET',
      success: (res) => {
        console.log('文章API响应:', res);
        
        if (res.statusCode === 200 && res.data.success) {
          const article = res.data.data;
          console.log('文章数据:', article);
          console.log('HTML内容长度:', article.html_content ? article.html_content.length : 0);
          
          // 设置文章数据
          this.setData({ 
            article,
            isLoading: false 
          });
          
          // 设置导航栏标题
          wx.setNavigationBarTitle({
            title: article.title
          });
          
          // 使用towxml解析HTML内容
          if (article.html_content) {
            this.parseHtmlWithTowxml(article.html_content);
          }
        } else {
          console.error('API返回错误:', res.data);
          this.setData({ 
            isLoading: false, 
            error: res.data?.error || '加载文章失败' 
          });
        }
      },
      fail: (error) => {
        console.error('请求失败:', error);
        this.setData({ 
          isLoading: false, 
          error: '网络请求失败' 
        });
      }
    });
  },

  // 使用towxml解析HTML内容
  parseHtmlWithTowxml(htmlContent) {
    try {
      console.log('开始使用towxml解析HTML内容...');
      
      // 使用towxml解析HTML，使用更保守的配置
      const articleContent = app.towxml(htmlContent, 'html', {
        base: app.globalData.serverUrl,
        theme: 'light',
        // 简化配置，避免复杂功能
        events: {
          tap: (e) => {
            console.log('元素点击:', e);
          }
        }
      });
      
      console.log('towxml解析结果:', articleContent);
      
      if (articleContent && articleContent.children && articleContent.children.length > 0) {
        this.setData({
          articleContent
        });
        console.log('towxml解析成功，子元素数量:', articleContent.children.length);
      } else {
        console.log('towxml解析结果为空，尝试备用方案');
        this.fallbackToSimpleText(htmlContent);
      }
    } catch (error) {
      console.error('towxml解析失败:', error);
      console.log('使用备用方案');
      this.fallbackToSimpleText(htmlContent);
    }
  },

  // 备用方案：简单的文本提取
  fallbackToSimpleText(htmlContent) {
    try {
      // 移除HTML标签，保留文本内容
      const textContent = htmlContent.replace(/<[^>]*>/g, '');
      
      // 按段落分割
      const paragraphs = textContent.split('\n').filter(p => p.trim());
      
      // 创建简单的节点结构
      const simpleNodes = paragraphs.map(paragraph => ({
        name: 'view',
        attrs: {
          style: 'margin-bottom: 20rpx; line-height: 1.6; color: #333;'
        },
        children: [{
          type: 'text',
          text: paragraph.trim()
        }]
      }));
      
      this.setData({
        articleContent: simpleNodes
      });
      
      console.log('使用备用方案成功');
    } catch (error) {
      console.error('备用方案也失败了:', error);
    }
  },

  // 返回列表
  goBack() {
    wx.navigateBack();
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

    // 直接使用页面高度估算跳转
    this.scrollToHeadingByPageHeight(anchor, title);
  },

  // 通过页面高度估算跳转
  scrollToHeadingByPageHeight(anchor, title) {
    const headingsData = this.data.article.headings;
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
          // 假设标题在页面中均匀分布
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
    if (!this.data.article.headings || this.data.article.headings.length === 0) {
      return;
    }

    const scrollTop = e.scrollTop;
    const headings = this.data.article.headings;
    
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
});