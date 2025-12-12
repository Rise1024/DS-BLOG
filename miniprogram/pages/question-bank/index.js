const app = getApp();

Page({
  data: {
    isLoading: true,
    categories: [],
    treeData: [],
    searchQuery: '',
    searchResults: {
      questions: [],
      tags: []
    },
    showSearchResults: false
  },

  onLoad(options) {
    if (options.search) {
      this.setData({ searchQuery: options.search, showSearchResults: true });
      this.searchQuestions(options.search);
    } else {
      this.loadCategories();
    }
  },

  onPullDownRefresh() {
    if (this.data.showSearchResults) {
      this.searchQuestions(this.data.searchQuery);
    } else {
      this.loadCategories();
    }
    wx.stopPullDownRefresh();
  },

  // 加载分类列表
  loadCategories() {
    this.setData({ isLoading: true });
    wx.request({
      url: `${app.globalData.serverUrl}/api/v1/question-bank/categories`,
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          const categories = res.data.data || [];
          // 转换为树形结构
          const treeData = this.convertToTreeData(categories);
          this.setData({
            treeData,
            categories: categories, // 保留原始数据用于其他功能
            isLoading: false,
            showSearchResults: false
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
        console.error('加载分类失败:', err);
        this.setData({ isLoading: false });
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  },

  // 转换为树形结构
  convertToTreeData(categories) {
    const convertCategory = (cat) => {
      if (!cat) return null;
      
      const node = {
        title: cat.name,
        name: cat.name,
        id: cat.id,
        count: cat.total_question_count || cat.question_count || 0
      };

      // 如果有子分类，递归转换
      if (cat.children && cat.children.length > 0) {
        node.children = cat.children.map(convertCategory).filter(n => n !== null);
      }

      // 如果有题目，转换为 items
      const questions = cat.items || [];
      if (questions.length > 0) {
        node.items = questions.map(question => ({
          title: question.title,
          id: question.id,
          name: question.title
        }));
      }

      return node;
    };

    return categories.map(convertCategory).filter(n => n !== null);
  },

  // 搜索题目
  searchQuestions(query) {
    if (!query || !query.trim()) {
      return;
    }
    
    this.setData({ isLoading: true });
    wx.request({
      url: `${app.globalData.serverUrl}/api/v1/question-bank/search`,
      data: { q: query },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          this.setData({
            searchResults: res.data.data || {},
            isLoading: false,
            showSearchResults: true
          });
        } else {
          this.setData({ isLoading: false });
          wx.showToast({
            title: '搜索失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('搜索失败:', err);
        this.setData({ isLoading: false });
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  },

  // 节点点击事件（分类）
  onNodeClick(e) {
    const { node } = e.detail;
    // 只有当节点是叶子节点（没有子节点也没有项目）时，才跳转到分类列表页面
    // 如果有子节点或项目，说明可以展开查看，不需要跳转
    const hasChildren = node.children && node.children.length > 0;
    const hasItems = node.items && node.items.length > 0;
    
    if (node.id && !hasChildren && !hasItems) {
      // 叶子分类节点，跳转到题目列表
      wx.navigateTo({
        url: `/pages/question-bank/list/index?categoryId=${node.id}`
      });
    }
    // 如果有子节点或项目，只展开/折叠，不跳转（由 tree-node 组件处理）
  },

  // 项目点击事件（题目）
  onItemClick(e) {
    const { item } = e.detail;
    if (item.id) {
      wx.navigateTo({
        url: `/pages/question-bank/detail/index?id=${item.id}`
      });
    }
  },

  // 跳转到分类题目列表（保留兼容性）
  goToCategory(e) {
    const categoryId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/question-bank/list/index?categoryId=${categoryId}`
    });
  },

  // 跳转到题目详情（保留兼容性）
  goToQuestion(e) {
    const questionId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/question-bank/detail/index?id=${questionId}`
    });
  },

  // 跳转到标签
  goToTag(e) {
    const tagName = e.currentTarget.dataset.name;
    wx.navigateTo({
      url: `/pages/question-bank/index?tag=${tagName}`
    });
  },

  // 搜索输入
  onSearchInput(e) {
    const query = e.detail.value;
    this.setData({ searchQuery: query });
    if (!query || !query.trim()) {
      this.setData({ showSearchResults: false });
      this.loadCategories();
    }
  },

  // 搜索确认
  onSearchConfirm(e) {
    const query = e.detail.value || this.data.searchQuery;
    if (query && query.trim()) {
      this.searchQuestions(query.trim());
    }
  },

  // 清除搜索
  clearSearch() {
    this.setData({
      searchQuery: '',
      showSearchResults: false,
      searchResults: { questions: [], tags: [] }
    });
    this.loadCategories();
  }
});


