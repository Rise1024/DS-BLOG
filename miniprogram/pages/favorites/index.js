const app = getApp();

Page({
  data: {
    isLoading: true,
    favorites: [],
    page: 1,
    pageSize: 20,
    hasMore: true,
    isEmpty: false
  },

  onLoad() {
    this.checkLogin();
  },

  onShow() {
    // 每次显示页面时刷新数据
    if (this.data.favorites.length > 0) {
      this.loadFavorites(true);
    }
  },

  // 检查登录状态
  checkLogin() {
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.showModal({
        title: '提示',
        content: '请先登录',
        showCancel: false,
        success: () => {
          wx.switchTab({
            url: '/pages/index/index'
          });
        }
      });
      return;
    }
    this.loadFavorites();
  },

  // 加载收藏列表
  loadFavorites(refresh = false) {
    if (refresh) {
      this.setData({
        page: 1,
        favorites: [],
        hasMore: true
      });
    }

    if (!this.data.hasMore && !refresh) {
      return;
    }

    this.setData({ isLoading: true });

    wx.request({
      url: `${app.globalData.serverUrl}/api/v1/question-bank/favorites`,
      method: 'GET',
      header: {
        'Authorization': wx.getStorageSync('token')
      },
      data: {
        page: this.data.page,
        page_size: this.data.pageSize
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          const newFavorites = res.data.data || [];
          const pagination = res.data.pagination || {};
          
          this.setData({
            favorites: refresh ? newFavorites : [...this.data.favorites, ...newFavorites],
            hasMore: pagination.page < pagination.total_pages,
            isEmpty: refresh && newFavorites.length === 0,
            page: this.data.page + 1,
            isLoading: false
          });
        } else {
          this.setData({ isLoading: false });
          wx.showToast({
            title: res.data?.error || '加载失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        this.setData({ isLoading: false });
        console.error('加载收藏失败:', err);
        if (err.statusCode === 401) {
          wx.showModal({
            title: '提示',
            content: '请先登录',
            showCancel: false,
            success: () => {
              wx.switchTab({
                url: '/pages/index/index'
              });
            }
          });
        } else {
          wx.showToast({
            title: '网络错误',
            icon: 'none'
          });
        }
      }
    });
  },

  // 跳转到题目详情
  goToQuestion(e) {
    const questionId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/question-bank/detail/index?id=${questionId}`
    });
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadFavorites(true);
    setTimeout(() => {
      wx.stopPullDownRefresh();
    }, 1000);
  },

  // 上拉加载更多
  onReachBottom() {
    if (this.data.hasMore && !this.data.isLoading) {
      this.loadFavorites();
    }
  }
});

