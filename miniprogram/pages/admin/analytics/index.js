Page({
  data: {
    totalGenerations: 0,
    totalImages: 0,
    activeUsers: 0,
    avgGenerationTime: 0,
    generationTrend: 0,
    imageTrend: 0,
    userTrend: 0,
    timeRange: 'week',
    usageData: [],
    chartData: []
  },

  onLoad() {
    this.checkAdminStatus();
    this.loadAnalytics();
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

  loadAnalytics() {
    const app = getApp();
    const token = wx.getStorageSync('token');

    wx.request({
      url: `${app.globalData.serverUrl}/api/analytics?timeRange=${this.data.timeRange}`,
      method: 'GET',
      header: {
        'Authorization': token
      },
      success: (res) => {
        if (res.data.success) {
          const data = res.data;
          this.setData({
            totalGenerations: data.totalGenerations,
            totalImages: data.totalImages,
            activeUsers: data.activeUsers,
            avgGenerationTime: data.avgGenerationTime.toFixed(1),
            generationTrend: data.generationTrend,
            imageTrend: data.imageTrend,
            userTrend: data.userTrend,
            usageData: data.usageData,
            chartData: data.chartData
          });
          this.drawChart();
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
      }
    });
  },

  setTimeRange(e) {
    const range = e.currentTarget.dataset.range;
    this.setData({ timeRange: range });
    this.loadAnalytics();
  },

  drawChart() {
    const ctx = wx.createCanvasContext('trendChart');
    const data = this.data.chartData;
    const width = 300;
    const height = 200;
    const padding = 30;

    // 清空画布
    ctx.clearRect(0, 0, width, height);

    // 绘制坐标轴
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(padding, padding);
    ctx.setStrokeStyle('#999');
    ctx.stroke();

    if (data.length > 0) {
      // 计算比例
      const maxValue = Math.max(...data.map(item => item.value));
      const xStep = (width - 2 * padding) / (data.length - 1);
      const yStep = (height - 2 * padding) / maxValue;

      // 绘制折线
      ctx.beginPath();
      ctx.moveTo(padding, height - padding - data[0].value * yStep);
      data.forEach((item, index) => {
        const x = padding + index * xStep;
        const y = height - padding - item.value * yStep;
        ctx.lineTo(x, y);
      });
      ctx.setStrokeStyle('#1a237e');
      ctx.stroke();

      // 绘制数据点
      data.forEach((item, index) => {
        const x = padding + index * xStep;
        const y = height - padding - item.value * yStep;
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, 2 * Math.PI);
        ctx.setFillStyle('#1a237e');
        ctx.fill();
      });
    }

    ctx.draw();
  }
});