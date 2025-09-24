Page({
  data: {
    content: '',
    contact: '',
    submitting: false,
    showLoginModal: false
  },

  handleContentInput(e) {
    this.setData({
      content: e.detail.value
    });
  },

  handleContactInput(e) {
    this.setData({
      contact: e.detail.value
    });
  },

  submitFeedback() {
    if (!this.data.content.trim()) {
      this.selectComponent('#customToast').setData({
        show: true,
        title: '请输入反馈内容',
        icon: 'error'
      });
      return;
    }

    const token = wx.getStorageSync('token');
    if (!token) {
      this.setData({ showLoginModal: true });
      return;
    }

    this.setData({ submitting: true });

    const app = getApp();

    wx.request({
      url: `${app.globalData.serverUrl}/api/feedback`,
      method: 'POST',
      header: {
        'Authorization': `${token}`
      },
      data: {
        userId: wx.getStorageSync('userId'),
        content: this.data.content,
        contact: this.data.contact
      },
      success: (res) => {
        if (res.data.success) {
          wx.showToast({
            title: '提交成功',
            icon: 'success'
          });
          // 清空输入
          this.setData({
            userId: '',
            content: '',
            contact: ''
          });
        } else {
          wx.showToast({
            title: '提交失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      },
      complete: () => {
        this.setData({ submitting: false });
      }
    });
  },

  onLoginModalClose() {
    this.setData({ showLoginModal: false });
  },

  onLogin(e) {
    const app = getApp();
    app.globalData.userInfo = e.detail.userInfo;
    this.setData({ showLoginModal: false });
    this.submitFeedback();
  }
})