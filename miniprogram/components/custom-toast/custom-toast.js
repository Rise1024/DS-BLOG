Component({
  properties: {
    show: {
      type: Boolean,
      value: false
    },
    title: {
      type: String,
      value: ''
    },
    icon: {
      type: String,
      value: 'none' // none, success, error
    },
    duration: {
      type: Number,
      value: 1500
    }
  },

  data: {
    animationData: {}
  },

  observers: {
    'show': function(show) {
      if (show) {
        this.showToast();
      }
    }
  },

  methods: {
    showToast() {
      const animation = wx.createAnimation({
        duration: 200,
        timingFunction: 'ease-out'
      });

      // 初始位置设置在中心点稍微偏上
      animation.opacity(0).translateY(-10).step({ duration: 0 });
      this.setData({
        animationData: animation.export()
      });

      // 淡入动画
      setTimeout(() => {
        animation.opacity(1).translateY(0).step();
        this.setData({
          animationData: animation.export()
        });
      }, 100);

      // 设置定时器自动关闭
      setTimeout(() => {
        // 淡出动画
        animation.opacity(0).translateY(-10).step();
        this.setData({
          animationData: animation.export()
        });

        setTimeout(() => {
          this.triggerEvent('close');
        }, 200);
      }, this.data.duration);
    }
  }
})