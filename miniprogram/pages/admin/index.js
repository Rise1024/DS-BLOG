Page({
    data: {
        isAdmin: false,
        userInfo: null
    },

    onLoad() {
        this.checkAdminStatus();
    },

    onShow() {
        this.checkAdminStatus();
    },

    checkAdminStatus() {
        const token = wx.getStorageSync('role');
        // 根据用户角色进行页面跳转
        if (token === 'user') {
            wx.redirectTo({
                url: '/pages/index/index'
            });
        }
    }
});