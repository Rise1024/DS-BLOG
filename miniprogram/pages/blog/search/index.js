const app = getApp();

Page({
  data: {
    searchKeyword: '',
    isLoading: false,
    isSearching: false,
    searchResults: [],
    searchHistory: []
  },

  onLoad(options) {
    // 从URL参数获取搜索关键词
    const { keyword } = options;
    if (keyword) {
      this.setData({ searchKeyword: keyword });
      this.performSearch(keyword);
    }
    
    // 加载搜索历史
    this.loadSearchHistory();
  },

  onPullDownRefresh() {
    if (this.data.searchKeyword) {
      this.performSearch(this.data.searchKeyword);
    }
    wx.stopPullDownRefresh();
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({ searchKeyword: e.detail.value });
  },

  // 执行搜索
  onSearch() {
    const keyword = this.data.searchKeyword.trim();
    if (!keyword) {
      wx.showToast({
        title: '请输入搜索关键词',
        icon: 'none'
      });
      return;
    }
    
    this.performSearch(keyword);
  },

  // 执行搜索请求
  performSearch(keyword) {
    this.setData({ 
      isLoading: true, 
      isSearching: true,
      searchResults: []
    });
    
    // 保存搜索历史
    this.saveSearchHistory(keyword);
    
    wx.request({
      url: `${app.globalData.serverUrl}/api/blog/search`,
      method: 'POST',
      data: { keyword },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          const results = res.data.data || [];
          this.setData({ 
            searchResults: results,
            isLoading: false 
          });
        } else {
          this.setData({ 
            isLoading: false,
            searchResults: []
          });
          wx.showToast({
            title: res.data?.error || '搜索失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        console.error('搜索失败:', error);
        this.setData({ 
          isLoading: false,
          searchResults: []
        });
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        });
      }
    });
  },

  // 选择历史关键词
  selectHistoryKeyword(e) {
    const keyword = e.currentTarget.dataset.keyword;
    this.setData({ searchKeyword: keyword });
    this.performSearch(keyword);
  },

  // 加载搜索历史
  loadSearchHistory() {
    const history = wx.getStorageSync('searchHistory') || [];
    this.setData({ searchHistory: history });
  },

  // 保存搜索历史
  saveSearchHistory(keyword) {
    let history = wx.getStorageSync('searchHistory') || [];
    
    // 移除重复项
    history = history.filter(item => item !== keyword);
    
    // 添加到开头
    history.unshift(keyword);
    
    // 限制历史记录数量
    if (history.length > 10) {
      history = history.slice(0, 10);
    }
    
    // 保存到本地存储
    wx.setStorageSync('searchHistory', history);
    this.setData({ searchHistory: history });
  },

  // 清空搜索历史
  clearHistory() {
    wx.showModal({
      title: '确认清空',
      content: '确定要清空搜索历史吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('searchHistory');
          this.setData({ searchHistory: [] });
        }
      }
    });
  },

  // 跳转到文章详情
  goToArticle(e) {
    const article = e.currentTarget.dataset.article;
    wx.navigateTo({
      url: `/pages/blog/article/index?id=${encodeURIComponent(article.id)}`
    });
  }
});
