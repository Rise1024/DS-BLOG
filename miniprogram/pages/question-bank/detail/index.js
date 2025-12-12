const app = getApp();

Page({
  data: {
    isLoading: true,
    question: null,
    showAnswer: false,
    isFavorited: false,
    isLoggedIn: false
  },

  onLoad(options) {
    const questionId = options.id;
    if (questionId) {
      this.checkLoginStatus();
      this.loadQuestion(questionId);
    }
  },

  // 转换Markdown为towxml格式
  convertMarkdown(markdown) {
    if (!markdown) return null;
    try {
      return app.towxml(markdown, 'markdown', {
        theme: 'light',
        events: {
          tap: (e) => {
            console.log('元素点击:', e);
          }
        }
      });
    } catch (error) {
      console.error('Markdown转换失败:', error);
      return null;
    }
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token');
    this.setData({ isLoggedIn: !!token });
  },

  // 加载题目详情
  loadQuestion(questionId) {
    this.setData({ isLoading: true });
    wx.request({
      url: `${app.globalData.serverUrl}/api/v1/question-bank/questions/${questionId}`,
      data: { show_answer: this.data.showAnswer },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          const question = res.data.data;
          
          // 转换Markdown内容为towxml格式
          if (question.content) {
            question.contentNodes = this.convertMarkdown(question.content);
          }
          if (question.answer) {
            question.answerNodes = this.convertMarkdown(question.answer);
          }
          if (question.explanation) {
            question.explanationNodes = this.convertMarkdown(question.explanation);
          }
          
          this.setData({
            question: question,
            isLoading: false
          });
          
          // 如果已登录，检查收藏状态
          if (this.data.isLoggedIn) {
            this.checkFavorite();
          }
        } else {
          this.setData({ isLoading: false });
          wx.showToast({
            title: '加载失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('加载题目失败:', err);
        this.setData({ isLoading: false });
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  },

  // 检查收藏状态
  checkFavorite() {
    if (!this.data.isLoggedIn) return;
    
    const questionId = this.data.question?.id;
    if (!questionId) return;
    
    wx.request({
      url: `${app.globalData.serverUrl}/api/v1/question-bank/questions/${questionId}/favorite`,
      header: {
        'Authorization': wx.getStorageSync('token')
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          this.setData({
            isFavorited: res.data.data.favorited
          });
        }
      }
    });
  },

  // 切换显示答案
  toggleAnswer() {
    const showAnswer = !this.data.showAnswer;
    this.setData({ showAnswer });
    
    // 如果显示答案但答案未加载，重新加载
    if (showAnswer && !this.data.question.answer) {
      this.loadQuestion(this.data.question.id);
    }
  },

  // 切换收藏
  toggleFavorite() {
    if (!this.data.isLoggedIn) {
      wx.showModal({
        title: '提示',
        content: '请先登录',
        showCancel: false
      });
      return;
    }
    
    const questionId = this.data.question?.id;
    if (!questionId) return;
    
    wx.request({
      url: `${app.globalData.serverUrl}/api/v1/question-bank/questions/${questionId}/favorite`,
      method: 'POST',
      header: {
        'Authorization': wx.getStorageSync('token')
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          this.setData({
            isFavorited: res.data.data.favorited
          });
          wx.showToast({
            title: res.data.data.favorited ? '已收藏' : '已取消收藏',
            icon: 'success'
          });
        }
      },
      fail: (err) => {
        console.error('收藏操作失败:', err);
        if (err.statusCode === 401) {
          wx.showModal({
            title: '提示',
            content: '请先登录',
            showCancel: false
          });
        }
      }
    });
  },

  // 上一题
  goToPrev() {
    const prevId = this.data.question?.navigation?.prev;
    if (prevId) {
      this.setData({ showAnswer: false });
      this.loadQuestion(prevId);
      wx.pageScrollTo({
        scrollTop: 0,
        duration: 300
      });
    }
  },

  // 下一题
  goToNext() {
    const nextId = this.data.question?.navigation?.next;
    if (nextId) {
      this.setData({ showAnswer: false });
      this.loadQuestion(nextId);
      wx.pageScrollTo({
        scrollTop: 0,
        duration: 300
      });
    }
  },

  // 跳转到相关文章
  goToArticle(e) {
    const articleId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/blog/article/index?id=${articleId}`
    });
  }
});

