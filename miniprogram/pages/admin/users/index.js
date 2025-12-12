Page({
    data: {
        users: [],
        roles: ['user', 'admin'],
        loading: true
    },

    onLoad() {
        this.checkAdminStatus();
        this.loadUsers();
    },

    checkAdminStatus() {
        const token = wx.getStorageSync('role');
        // 根据用户角色进行页面跳转
        if (token === 'user') {
            wx.redirectTo({
                url: '/pages/index/index'
            });
        }
    },

    loadUsers() {
        const app = getApp();
        const token = wx.getStorageSync('token');

        wx.request({
            url: `${app.globalData.serverUrl}/api/v1/admin/users?user_type=wechat`,
            method: 'GET',
            header: {
                'Authorization': token
            },
            success: (res) => {
                if (res.data.success) {
                    this.setData({
                        users: res.data.users,
                        loading: false
                    });
                } else {
                    wx.showToast({
                        title: '加载失败',
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
                this.setData({ loading: false });
            }
        });
    },

    handleRoleChange(e) {
        const userId = e.currentTarget.dataset.userid;
        const roleIndex = e.detail.value;
        const newRole = this.data.roles[roleIndex];
        const app = getApp();
        const token = wx.getStorageSync('token');

        wx.request({
            url: `${app.globalData.serverUrl}/api/v1/admin/users/${userId}/role`,
            method: 'PUT',
            header: {
                'Authorization': token
            },
            data: {
                userId: userId,
                role: newRole
            },
            success: (res) => {
                if (res.data.success) {
                    wx.showToast({
                        title: '更新成功',
                        icon: 'success'
                    });
                    this.loadUsers(); // 重新加载用户列表
                } else {
                    wx.showToast({
                        title: '更新失败',
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
    }
});