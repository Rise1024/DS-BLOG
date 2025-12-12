const app = getApp();

Page({
  data: {
    isLoading: true,
    feedbacks: [],
    statusFilter: 'all', // all, pending, processed, closed
    pagination: {
      page: 1,
      page_size: 20,
      total: 0,
      total_pages: 0
    },
    hasMore: true
  },

  onLoad() {
    this.checkAdminStatus();
    this.loadFeedbacks();
  },

  onPullDownRefresh() {
    this.setData({
      'pagination.page': 1,
      feedbacks: [],
      hasMore: true
    });
    this.loadFeedbacks();
    wx.stopPullDownRefresh();
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.isLoading) {
      this.loadMoreFeedbacks();
    }
  },

  checkAdminStatus() {
    const role = wx.getStorageSync('role');
    if (role !== 'admin') {
      wx.showToast({
        title: '无权限访问',
        icon: 'none'
      });
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    }
  },

  // 加载反馈列表
  loadFeedbacks() {
    this.setData({ isLoading: true });
    
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      this.setData({ isLoading: false });
      return;
    }

    const { page, page_size } = this.data.pagination;
    const { statusFilter } = this.data;
    
    let url = `${app.globalData.serverUrl}/api/v1/admin/feedbacks?page=${page}&page_size=${page_size}`;
    if (statusFilter !== 'all') {
      url += `&status=${statusFilter}`;
    }

    wx.request({
      url: url,
      method: 'GET',
      header: {
        'Authorization': token
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          const { data, pagination } = res.data;
          // 格式化时间
          const formattedData = data.map(item => ({
            ...item,
            created_at: this.formatTime(item.created_at),
            processed_at: item.processed_at ? this.formatTime(item.processed_at) : null
          }));
          this.setData({
            feedbacks: formattedData,
            pagination: pagination,
            hasMore: pagination.page < pagination.total_pages,
            isLoading: false
          });
        } else {
          wx.showToast({
            title: res.data.error || '加载失败',
            icon: 'none'
          });
          this.setData({ isLoading: false });
        }
      },
      fail: (err) => {
        console.error('加载反馈列表失败:', err);
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
        this.setData({ isLoading: false });
      }
    });
  },

  // 加载更多
  loadMoreFeedbacks() {
    if (!this.data.hasMore || this.data.isLoading) {
      return;
    }

    const nextPage = this.data.pagination.page + 1;
    this.setData({
      'pagination.page': nextPage,
      isLoading: true
    });

    const token = wx.getStorageSync('token');
    const { page, page_size } = this.data.pagination;
    const { statusFilter } = this.data;
    
    let url = `${app.globalData.serverUrl}/api/v1/admin/feedbacks?page=${nextPage}&page_size=${page_size}`;
    if (statusFilter !== 'all') {
      url += `&status=${statusFilter}`;
    }

    wx.request({
      url: url,
      method: 'GET',
      header: {
        'Authorization': token
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          const { data, pagination } = res.data;
          // 格式化时间
          const formattedData = data.map(item => ({
            ...item,
            created_at: this.formatTime(item.created_at),
            processed_at: item.processed_at ? this.formatTime(item.processed_at) : null
          }));
          this.setData({
            feedbacks: [...this.data.feedbacks, ...formattedData],
            pagination: pagination,
            hasMore: pagination.page < pagination.total_pages,
            isLoading: false
          });
        } else {
          this.setData({ isLoading: false });
        }
      },
      fail: () => {
        this.setData({ isLoading: false });
      }
    });
  },

  // 切换状态筛选
  onStatusFilterChange(e) {
    const status = e.currentTarget.dataset.status;
    this.setData({
      statusFilter: status,
      'pagination.page': 1,
      feedbacks: [],
      hasMore: true
    });
    this.loadFeedbacks();
  },

  // 更新反馈状态
  updateFeedbackStatus(feedbackId, status) {
    const token = wx.getStorageSync('token');
    
    wx.request({
      url: `${app.globalData.serverUrl}/api/v1/admin/feedbacks/${feedbackId}`,
      method: 'PUT',
      header: {
        'Authorization': token,
        'Content-Type': 'application/json'
      },
      data: {
        status: status
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          wx.showToast({
            title: '更新成功',
            icon: 'success'
          });
          // 重新加载列表
          this.setData({
            'pagination.page': 1,
            feedbacks: [],
            hasMore: true
          });
          this.loadFeedbacks();
        } else {
          wx.showToast({
            title: res.data.error || '更新失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  },

  // 标记为已处理
  markAsProcessed(e) {
    const feedbackId = e.currentTarget.dataset.id;
    this.updateFeedbackStatus(feedbackId, 'processed');
  },

  // 标记为已关闭
  markAsClosed(e) {
    const feedbackId = e.currentTarget.dataset.id;
    this.updateFeedbackStatus(feedbackId, 'closed');
  },

  // 格式化时间
  formatTime(timeStr) {
    if (!timeStr) return '';
    try {
      // 处理 ISO 格式时间字符串
      const date = new Date(timeStr);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hour = String(date.getHours()).padStart(2, '0');
      const minute = String(date.getMinutes()).padStart(2, '0');
      return `${year}-${month}-${day} ${hour}:${minute}`;
    } catch (e) {
      return timeStr;
    }
  },

  // 获取状态文本
  getStatusText(status) {
    const statusMap = {
      'pending': '待处理',
      'processed': '已处理',
      'closed': '已关闭'
    };
    return statusMap[status] || status;
  },

  // 获取状态颜色
  getStatusColor(status) {
    const colorMap = {
      'pending': '#ff9800',
      'processed': '#4caf50',
      'closed': '#9e9e9e'
    };
    return colorMap[status] || '#666';
  }
});

