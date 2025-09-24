App({
  globalData: {
    userInfo: null,
    serverUrl: 'http://localhost:5000'
  },
  towxml:require('/towxml/index'),

  onLaunch: function() {
    // 添加请求拦截器
    this.setupRequestInterceptor();

    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || [];
    logs.unshift(Date.now());
    wx.setStorage({
      key: 'logs',
      data: logs
    });

    // 获取本地存储的用户信息
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo) {
      this.globalData.userInfo = userInfo;
    }
  },

  setupRequestInterceptor: function() {
    // 拦截wx.request
    const originalRequest = wx.request;
    Object.defineProperty(wx, 'request', {
      configurable: true,
      enumerable: true,
      writable: true,
      value: this.createInterceptor(originalRequest)
    });

    // 拦截wx.uploadFile
    const originalUploadFile = wx.uploadFile;
    Object.defineProperty(wx, 'uploadFile', {
      configurable: true,
      enumerable: true,
      writable: true,
      value: this.createInterceptor(originalUploadFile)
    });
  },

  // 创建拦截器
  createInterceptor: function(originalFunction) {
    return function(options) {
      const token = wx.getStorageSync('token');
      const header = { ...options.header };
      
      if (token) {
        header['Authorization'] = `${token}`;
      }

      const originalSuccess = options.success;
      const originalFail = options.fail;

      const modifiedOptions = {
        ...options,
        header,
        success: (response) => {
          if (response.statusCode === 401) {
            // 清除登录信息
            wx.removeStorageSync('token');
            wx.removeStorageSync('userId');
            wx.removeStorageSync('userInfo');
            getApp().globalData.userInfo = null;
            
            // 获取当前页面实例
            const pages = getCurrentPages();
            const currentPage = pages[pages.length - 1];
            
            // 设置showLoginModal为true
            if (currentPage) {
              currentPage.setData({
                showLoginModal: true
              });
            }
            
            // 使用switchTab确保跳转到登录页面
            wx.switchTab({
              url: '/pages/index/index',
              fail: () => {
                // 如果switchTab失败（可能是因为页面不在tabBar中），则使用redirectTo
                wx.redirectTo({
                  url: '/pages/index/index'
                });
              }
            });
          } else if (originalSuccess) {
            originalSuccess(response);
          }
        },
        fail: function(error) {
          if (originalFail) {
            originalFail(error);
          }
        }
      };

      return originalFunction(modifiedOptions);
    };
  },

  // 检查登录状态
  checkLoginStatus: function() {
    const userInfo = this.globalData.userInfo;
    console.log('Current userInfo:', userInfo);
    if (!userInfo) {
      console.log('User not logged in, redirecting...');
      wx.redirectTo({
        url: '/pages/index/index',
        fail: (err) => {
          console.error('Redirect failed:', err);
          wx.switchTab({
            url: '/pages/index/index'
          });
        }
      });
      return false;
    }
    return true;
  }
});