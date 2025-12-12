Page({
  data: {
    userInfo: null,
    showLoginModal: false
  },

  onShow() {
    // 检查本地存储中是否有用户信息
    const userInfo = wx.getStorageSync('userInfo')
    const role = wx.getStorageSync('role')
    
    // 如果是管理员角色，每次进入页面都跳转到管理员页面
    if (userInfo && role === 'admin') {
      wx.redirectTo({
        url: '/pages/admin/index'
      })
      return
    }
    
    // 普通用户或未登录用户的处理逻辑
    if (userInfo) {
      this.setData({
        userInfo: userInfo
      })
    }
    // 取消自动显示登录弹窗，改为用户主动点击登录按钮
  },

  // 处理用户信息获取
  handleShowLoginModal() {
    this.setData({
      showLoginModal: true
    });
  },

  handleCloseLoginModal() {
    this.setData({
      showLoginModal: false
    });
  },

  handleGetUserInfo(e) {
    if (e.detail.userInfo) {
      // 先获取临时登录凭证code
      wx.login({
        success: (res) => {
          if (res.code) {
            const app = getApp();
            // 发送code到开发者服务器
            wx.request({
              url: `${app.globalData.serverUrl}/api/v1/login`,
              method: 'POST',
              data: {
                code: res.code,
                userInfo: e.detail.userInfo
              },
              success: (response) => {
                if (response.data.success) {
                  // 保存服务器返回的登录态信息
                  wx.setStorageSync('token', response.data.token);
                  wx.setStorageSync('userId', response.data.userId);
                  wx.setStorageSync('userInfo', e.detail.userInfo);
                  wx.setStorageSync('role', response.data.role);

                  // 更新页面数据和全局数据
                  this.setData({
                    userInfo: e.detail.userInfo,
                    showLoginModal: false  // 关闭登录弹窗
                  });
                  app.globalData.userInfo = e.detail.userInfo;

                  // 根据用户角色进行页面跳转
                  if (response.data.role === 'admin') {
                    wx.redirectTo({
                      url: '/pages/admin/index'
                    });
                  }

                  wx.showToast({
                    title: '登录成功',
                    icon: 'success',
                    duration: 2000
                  });
                } else {
                  wx.showToast({
                    title: '登录失败',
                    icon: 'none',
                    duration: 2000
                  });
                }
              },
              fail: () => {
                wx.showToast({
                  title: '服务器连接失败',
                  icon: 'none',
                  duration: 2000
                });
              }
            });
          } else {
            wx.showToast({
              title: '获取登录凭证失败',
              icon: 'none',
              duration: 2000
            });
          }
        }
      });
    } else {
      wx.showToast({
        title: '请授权登录',
        icon: 'none',
        duration: 2000
      });
    }
  },

  // 处理退出登录
  handleLogout() {
    // 清除所有登录相关的存储信息
    wx.removeStorageSync('userInfo');
    wx.removeStorageSync('token');
    wx.removeStorageSync('userId');
    wx.removeStorageSync('role');
    
    // 清除页面数据
    this.setData({
      userInfo: null
    });
    
    // 清除全局数据
    const app = getApp();
    app.globalData.userInfo = null;

    wx.showToast({
      title: '已退出登录',
      icon: 'success',
      duration: 2000
    });
  },
  // 导航到我的收藏页面
  navigateToFavorites() {
    if (!this.data.userInfo) {
      this.handleShowLoginModal();
      return;
    }
    wx.navigateTo({
      url: '/pages/favorites/index'
    });
  },

  // 导航到意见反馈页面
  navigateToFeedback() {
    if (!this.data.userInfo) {
      this.handleShowLoginModal();
      return;
    }
    wx.navigateTo({
      url: '/pages/feedback/index'
    });
  },

  // 导航到关于我们页面
  navigateToAbout() {
    wx.navigateTo({
      url: '/pages/about/index'
    });
  }
})