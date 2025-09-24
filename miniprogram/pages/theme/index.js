Page({
  data: {
    theme: 'light',
    loading: false
  },

  onLoad() {
    // 获取当前主题设置
    const theme = wx.getStorageSync('theme') || 'light';
    this.setData({ theme });
    this.applyTheme(theme);
  },

  // 切换主题
  toggleTheme() {
    const newTheme = this.data.theme === 'light' ? 'dark' : 'light';
    this.setData({ 
      loading: true,
      theme: newTheme 
    });

    // 保存主题设置
    wx.setStorageSync('theme', newTheme);
    
    // 应用主题
    this.applyTheme(newTheme);

    setTimeout(() => {
      this.setData({ loading: false });
      wx.showToast({
        title: '主题切换成功',
        icon: 'success'
      });
    }, 500);
  },

  // 应用主题
  applyTheme(theme) {
    if (theme === 'dark') {
      wx.setNavigationBarColor({
        frontColor: '#ffffff',
        backgroundColor: '#333333'
      });
    } else {
      wx.setNavigationBarColor({
        frontColor: '#000000',
        backgroundColor: '#ffffff'
      });
    }
  }
})