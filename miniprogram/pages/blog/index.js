const app = getApp();

Page({
  data: {
    isLoading: true,
    error: '',
    categories: [],
    articles: [],
    selectedCategory: '',
    searchKeyword: '',
    allArticles: [] // 存储所有文章，用于搜索
  },

  onLoad() {
    this.loadBlogData();
  },

  onPullDownRefresh() {
    this.loadBlogData();
    wx.stopPullDownRefresh();
  },

  // 加载博客数据
  loadBlogData() {
    this.setData({ isLoading: true, error: '' });
    
    // 并行加载分类和文章数据
    Promise.all([
      this.loadCategories(),
      this.loadArticles()
    ]).then(() => {
      this.setData({ isLoading: false });
    }).catch((error) => {
      console.error('加载博客数据失败:', error);
      this.setData({ 
        isLoading: false, 
        error: '加载失败，请重试' 
      });
    });
  },

  // 加载分类数据
  loadCategories() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.serverUrl}/api/blog/categories`,
        success: (res) => {
          if (res.statusCode === 200 && res.data.success) {
            const categories = res.data.data || [];
            this.setData({ 
              categories,
              selectedCategory: categories[0]?.name || ''
            });
            resolve();
          } else {
            reject(new Error('获取分类失败'));
          }
        },
        fail: (error) => {
          reject(error);
        }
      });
    });
  },

  // 加载文章数据
  loadArticles() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.serverUrl}/api/blog/articles`,
        success: (res) => {
          if (res.statusCode === 200 && res.data.success) {
            const articles = res.data.data || [];
            this.setData({ 
              articles,
              allArticles: articles
            });
            resolve();
          } else {
            reject(new Error('获取文章失败'));
          }
        },
        fail: (error) => {
          reject(error);
        }
      });
    });
  },

  // 选择分类
  selectCategory(e) {
    const category = e.currentTarget.dataset.category;
    this.setData({ selectedCategory: category });
    this.filterArticlesByCategory(category);
  },

  // 根据分类筛选文章
  filterArticlesByCategory(category) {
    if (!category) {
      this.setData({ articles: this.data.allArticles });
      return;
    }
    
    const filteredArticles = this.data.allArticles.filter(article => 
      article.category === category
    );
    this.setData({ articles: filteredArticles });
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({ searchKeyword: e.detail.value });
  },

  // 执行搜索
  onSearch() {
    const keyword = this.data.searchKeyword.trim();
    if (!keyword) {
      this.filterArticlesByCategory(this.data.selectedCategory);
      return;
    }

    // 跳转到搜索页面
    wx.navigateTo({
      url: `/pages/blog/search/index?keyword=${encodeURIComponent(keyword)}`
    });
  },

  // 跳转到文章详情
  goToArticle(e) {
    const article = e.currentTarget.dataset.article;
    wx.navigateTo({
      url: `/pages/blog/article/index?id=${encodeURIComponent(article.id)}`
    });
  }
});
