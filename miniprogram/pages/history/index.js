Page({
  data: {
    historyList: [],
    loading: false,
    expandedIndex: -1
  },

  onLoad() {
    this.loadHistoryData();
  },

  toggleGroup(e) {
    const index = e.currentTarget.dataset.index;
    const historyList = this.data.historyList;
    historyList[index].isExpanded = !historyList[index].isExpanded;

    this.setData({
      historyList: historyList
    });
  },

  loadHistoryData() {
    const app = getApp();
    const token = wx.getStorageSync('token');

    this.setData({ loading: true });

    wx.request({
      url: `${app.globalData.serverUrl}/api/history`,
      method: 'POST',
      header: {
        'Authorization': `${token}`
      },
      data: {
        userId: wx.getStorageSync('userId')
      },
      success: (res) => {
        if (res.data.success) {
          this.setData({
            historyList: res.data.data
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

  previewImage(e) {
    const { urls, current } = e.currentTarget.dataset;
    wx.previewImage({
      urls: urls,
      current: current
    });
  },

  downloadImage(e) {
    const { url } = e.currentTarget.dataset;
    wx.showLoading({
      title: '下载中...'
    });

    wx.downloadFile({
      url: url,
      success: (res) => {
        if (res.statusCode === 200) {
          wx.saveImageToPhotosAlbum({
            filePath: res.tempFilePath,
            success: () => {
              wx.showToast({
                title: '保存成功',
                icon: 'success'
              });
            },
            fail: () => {
              wx.showToast({
                title: '保存失败',
                icon: 'none'
              });
            }
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '下载失败',
          icon: 'none'
        });
      },
      complete: () => {
        wx.hideLoading();
      }
    });
  },

  deleteHistory(e) {
    const { articleId } = e.currentTarget.dataset;
    const app = getApp();
    const token = wx.getStorageSync('token');

    wx.showModal({
      title: '确认删除',
      content: '确定要删除这条记录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.request({
            url: `${app.globalData.serverUrl}/api/history/${articleId}`,
            method: 'DELETE',
            header: {
              'Authorization': `${token}`
            },
            data: {
                userId: wx.getStorageSync('userId')
            },
            success: (res) => {
              if (res.data.success) {
                this.loadHistoryData();
                wx.showToast({
                  title: '删除成功',
                  icon: 'success'
                });
              } else {
                wx.showToast({
                  title: '删除失败',
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
      }
    });
  }
})