const app = getApp();

Page({
  data: {
    isLoading: true,
    error: '',
    treeData: [],
    searchKeyword: ''
  },

  onLoad() {
    this.loadCategories();
  },

  onPullDownRefresh() {
    this.loadCategories();
    wx.stopPullDownRefresh();
  },

  // 加载分类数据（包含文章）
  loadCategories() {
    this.setData({ isLoading: true, error: '' });
    
    wx.request({
      url: `${app.globalData.serverUrl}/api/v1/blog/categories`,
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          const categories = res.data.data || [];
          // 转换为树形结构
          const treeData = this.convertToTreeData(categories);
          this.setData({ 
            treeData,
            isLoading: false
          });
        } else {
          this.setData({ 
            isLoading: false, 
            error: '获取分类失败' 
          });
        }
      },
      fail: (error) => {
        console.error('加载分类失败:', error);
        this.setData({ 
          isLoading: false, 
          error: '加载失败，请重试' 
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
        count: cat.count || 0
      };

      // 如果有子分类，递归转换
      if (cat.children && cat.children.length > 0) {
        node.children = cat.children.map(convertCategory).filter(n => n !== null);
      }

      // 如果有文章，转换为 items
      const articles = cat.items || cat.articles || [];
      if (articles.length > 0) {
        node.items = articles.map(article => ({
          title: article.title,
          id: article.id,
          name: article.title
        }));
      }

      return node;
    };

    return categories.map(convertCategory).filter(n => n !== null);
  },

  // 节点点击事件（分类）
  onNodeClick(e) {
    const { node } = e.detail;
    // 博客页面的分类节点只用于展开/折叠查看文章，不需要跳转
    // 展开/折叠逻辑由 tree-node 组件内部处理
  },

  // 项目点击事件（文章）
  onItemClick(e) {
    const { item } = e.detail;
    if (item.id) {
      wx.navigateTo({
        url: `/pages/blog/article/index?id=${item.id}`
      });
    }
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({ searchKeyword: e.detail.value });
  },

  // 执行搜索
  onSearch() {
    const keyword = this.data.searchKeyword.trim();
    if (!keyword) {
      return;
    }

    // 跳转到搜索页面
    wx.navigateTo({
      url: `/pages/blog/search/index?keyword=${encodeURIComponent(keyword)}`
    });
  }
});
