Component({
  properties: {
    node: {
      type: Object,
      value: {}
    },
    path: {
      type: String,
      value: ''
    },
    isRoot: {
      type: Boolean,
      value: false
    }
  },

  data: {
    expanded: false,
    hasChildren: false,
    hasItems: false,
    nodeCount: ''
  },

  lifetimes: {
    attached() {
      // 初始化展开状态和计算属性
      this.updateNodeState();
    }
  },

  observers: {
    'node': function(node) {
      this.updateNodeState();
    }
  },

  methods: {
    // 更新节点状态
    updateNodeState() {
      const { node, isRoot } = this.properties;
      const hasChildren = node.children && node.children.length > 0;
      const hasItems = node.items && node.items.length > 0;
      
      let nodeCount = '';
      if (node.count !== undefined && node.count !== null) {
        nodeCount = `${node.count} 篇`;
      } else if (node.total_question_count !== undefined) {
        nodeCount = `${node.total_question_count} 题`;
      } else if (node.question_count !== undefined) {
        nodeCount = `${node.question_count} 题`;
      }

      this.setData({
        expanded: isRoot,
        hasChildren,
        hasItems,
        nodeCount
      });
    },

    // 切换展开/折叠
    toggleNode() {
      this.setData({
        expanded: !this.data.expanded
      });
    },

    // 点击节点
    onNodeClick() {
      const { node } = this.properties;
      // 如果有子节点或项目，切换展开状态
      if (this.data.hasChildren || this.data.hasItems) {
        this.toggleNode();
      }
      // 触发父组件事件
      this.triggerEvent('nodeclick', { node });
    },

    // 点击项目（文章/题目）
    onItemClick(e) {
      const item = e.currentTarget.dataset.item;
      this.triggerEvent('itemclick', { item });
    },

    // 子节点点击事件
    onChildNodeClick(e) {
      this.triggerEvent('nodeclick', e.detail);
    },

    // 子节点项目点击事件
    onChildItemClick(e) {
      this.triggerEvent('itemclick', e.detail);
    }
  }
});

