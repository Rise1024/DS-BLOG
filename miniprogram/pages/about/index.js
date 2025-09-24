Page({
  data: {},

  navigateToFeedback() {
    const app = getApp();
    if (!app.checkLoginStatus()) {
      // 如果未登录，跳转到登录页面
      wx.switchTab({
        url: '/pages/index/index'
      });
      return;
    }
    wx.navigateTo({
      url: '/pages/feedback/index'
    });
  }
});