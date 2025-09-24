Component({
  properties: {
    show: {
      type: Boolean,
      value: false
    }
  },

  methods: {
    onClose() {
      this.triggerEvent('close');
    },

    onLogin() {
      wx.getUserProfile({
        desc: '用于完善会员资料',
        success: (res) => {
          this.triggerEvent('login', res);
        },
        fail: () => {
          wx.showToast({
            title: '请授权登录',
            icon: 'none',
            duration: 2000
          });
        }
      });
    }
  }
})