const app = getApp();

Page({
  data: {
    isLoading: true,
    category: null,
    questions: [],
    selectedDifficulty: '',
    selectedType: '',
    pagination: {
      page: 1,
      page_size: 20,
      total: 0,
      total_pages: 0
    }
  },

  onLoad(options) {
    const categoryId = options.categoryId;
    if (categoryId) {
      this.loadCategory(categoryId);
      this.loadQuestions(categoryId);
    }
  },

  onPullDownRefresh() {
    const categoryId = this.data.category?.id;
    if (categoryId) {
      this.setData({
        'pagination.page': 1
      });
      this.loadQuestions(categoryId);
    }
    wx.stopPullDownRefresh();
  },

  onReachBottom() {
    if (this.data.pagination.page < this.data.pagination.total_pages) {
      this.setData({
        'pagination.page': this.data.pagination.page + 1
      });
      this.loadMoreQuestions();
    }
  },

  // 加载分类信息
  loadCategory(categoryId) {
    wx.request({
      url: `${app.globalData.serverUrl}/api/v1/question-bank/categories`,
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          const categories = res.data.data || [];
          const findCategory = (cats, id) => {
            for (const cat of cats) {
              if (cat.id === parseInt(id)) return cat;
              if (cat.children) {
                const found = findCategory(cat.children, id);
                if (found) return found;
              }
            }
            return null;
          };
          const category = findCategory(categories, categoryId);
          if (category) {
            this.setData({ category });
            wx.setNavigationBarTitle({
              title: category.name
            });
          }
        }
      }
    });
  },

  // 加载题目列表
  loadQuestions(categoryId, append = false) {
    this.setData({ isLoading: true });
    
    const params = {
      category_id: categoryId,
      page: this.data.pagination.page,
      page_size: this.data.pagination.page_size
    };
    
    if (this.data.selectedDifficulty) {
      params.difficulty = parseInt(this.data.selectedDifficulty);
    }
    if (this.data.selectedType) {
      params.type = this.data.selectedType;
    }
    
    wx.request({
      url: `${app.globalData.serverUrl}/api/v1/question-bank/questions`,
      data: params,
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          const questions = res.data.data || [];
          this.setData({
            questions: append ? [...this.data.questions, ...questions] : questions,
            pagination: res.data.pagination || this.data.pagination,
            isLoading: false
          });
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

  // 加载更多题目
  loadMoreQuestions() {
    const categoryId = this.data.category?.id;
    if (categoryId) {
      this.loadQuestions(categoryId, true);
    }
  },

  // 筛选难度
  onDifficultyChange(e) {
    const index = parseInt(e.detail.value);
    const difficultyMap = ['', '1', '2', '3', '4', '5'];
    const difficulty = difficultyMap[index] || '';
    this.setData({
      selectedDifficulty: difficulty,
      'pagination.page': 1
    });
    this.loadQuestions(this.data.category.id);
  },

  // 筛选类型
  onTypeChange(e) {
    const index = parseInt(e.detail.value);
    const typeMap = ['', 'short_answer', 'programming'];
    const type = typeMap[index] || '';
    this.setData({
      selectedType: type,
      'pagination.page': 1
    });
    this.loadQuestions(this.data.category.id);
  },

  // 跳转到题目详情
  goToQuestion(e) {
    const questionId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/question-bank/detail/index?id=${questionId}`
    });
  }
});

