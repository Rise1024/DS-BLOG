<template>
  <div class="admin-tree-node" :class="{ 'is-root': isRoot }">
    <div 
      class="node-header"
      :class="{ 'has-children': hasChildren || hasItems, 'clickable': hasChildren || hasItems || onNodeClick }"
      @click="handleClick"
    >
      <span v-if="hasChildren || hasItems" class="toggle-icon">
        <svg v-if="isExpanded" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
        <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      </span>
      <span v-if="!hasChildren && !hasItems" class="leaf-icon">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
        </svg>
      </span>
      <span class="node-title">{{ nodeTitle }}</span>
      <span v-if="nodeCount !== undefined && nodeCount !== null" class="node-count">
        {{ nodeCount }}
      </span>
      
      <!-- 操作按钮 -->
      <div class="node-actions" @click.stop>
        <!-- 分类节点显示新建题目/文章按钮 -->
        <button 
          v-if="isCategoryNode && onCreate" 
          @click="handleCreate"
          class="action-btn create-btn"
          title="新建"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        </button>
        <!-- 分类节点显示新建子分类按钮 -->
        <button 
          v-if="onCreateCategory && isCategoryNode" 
          @click="handleCreateCategory"
          class="action-btn create-btn"
          title="新建子分类"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
        </button>
        <!-- 分类节点显示编辑按钮 -->
        <button 
          v-if="isCategoryNode && onEditCategory && node.id" 
          @click="handleEditCategory"
          class="action-btn edit-btn"
          title="编辑"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
        <!-- 分类节点显示删除按钮 -->
        <button 
          v-if="isCategoryNode && onDeleteCategory && node.id" 
          @click="handleDeleteCategory"
          class="action-btn delete-btn"
          title="删除"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
        </button>
        <!-- 题目/文章节点编辑 -->
        <button 
          v-if="!isCategoryNode && onEdit && node.id" 
          @click="handleEdit"
          class="action-btn edit-btn"
          title="编辑"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
        <!-- 题目/文章节点删除 -->
        <button 
          v-if="!isCategoryNode && onDelete && node.id" 
          @click="handleDelete"
          class="action-btn delete-btn"
          title="删除"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
        </button>
      </div>
    </div>
    
    <div v-if="isExpanded && hasChildren" class="node-children">
      <AdminTreeNode 
        v-for="(child, index) in node.children" 
        :key="getChildKey(child, index)"
        :node="{
          ...child,
          expanded: node.expanded,
          toggleNode: node.toggleNode
        }"
        :path="currentPath"
        :on-node-click="onNodeClick"
        :on-edit="onEdit"
        :on-delete="onDelete"
        :on-create="onCreate"
        :on-create-category="onCreateCategory"
        :on-edit-category="onEditCategory"
        :on-delete-category="onDeleteCategory"
        :is-root="false"
      />
    </div>
    
    <div v-if="isExpanded && hasItems" class="node-items">
      <div 
        v-for="(item, index) in node.items" 
        :key="index"
        class="item"
        @click.stop="handleItemClick(item)"
      >
        <svg class="item-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
        </svg>
        <span class="item-title">{{ getItemTitle(item) }}</span>
        <!-- 题目/文章项的操作按钮 -->
        <div class="item-actions" @click.stop>
          <button 
            v-if="onEdit && item.id" 
            @click="handleItemEdit(item)"
            class="action-btn edit-btn"
            title="编辑"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </button>
          <button 
            v-if="onDelete && item.id" 
            @click="handleItemDelete(item)"
            class="action-btn delete-btn"
            title="删除"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  node: {
    type: Object,
    required: true
  },
  path: {
    type: String,
    default: ''
  },
  onNodeClick: {
    type: Function,
    default: null
  },
  onEdit: {
    type: Function,
    default: null
  },
  onDelete: {
    type: Function,
    default: null
  },
  onCreate: {
    type: Function,
    default: null
  },
  onCreateCategory: {
    type: Function,
    default: null
  },
  onEditCategory: {
    type: Function,
    default: null
  },
  onDeleteCategory: {
    type: Function,
    default: null
  },
  isRoot: {
    type: Boolean,
    default: false
  }
});

const currentPath = computed(() => {
  return props.path ? `${props.path}.${getNodeTitle(props.node)}` : getNodeTitle(props.node);
});

const isExpanded = computed(() => {
  if (!props.node.expanded || !props.node.toggleNode) {
    return false;
  }
  
  // expanded 可能是 ref 对象，需要访问 .value
  let expandedObj = props.node.expanded;
  if (expandedObj && typeof expandedObj === 'object' && 'value' in expandedObj) {
    expandedObj = expandedObj.value;
  }
  
  if (expandedObj && typeof expandedObj === 'object') {
    return expandedObj[currentPath.value] === true;
  }
  
  return false;
});

const hasChildren = computed(() => {
  return props.node.children && props.node.children.length > 0;
});

const hasItems = computed(() => {
  return props.node.items && props.node.items.length > 0;
});

// 判断是否分类节点（有子分类/题目列表，或具备分类相关字段）
const isCategoryNode = computed(() => {
  // 优先使用明确的 isCategory 标记
  if (props.node.isCategory !== undefined) {
    return props.node.isCategory;
  }
  // 如果有 category_id 字段，说明是文章节点
  if (props.node.category_id !== undefined) {
    return false;
  }
  // 其他判断条件
  return (
    hasChildren.value ||
    hasItems.value ||
    props.node.parent_id !== undefined ||
    props.node.total_question_count !== undefined ||
    props.node.question_count !== undefined ||
    props.node.order !== undefined
  );
});

const nodeTitle = computed(() => {
  return getNodeTitle(props.node);
});

const nodeCount = computed(() => {
  if (props.node.total_question_count !== undefined) {
    return `${props.node.total_question_count} 题`;
  }
  if (props.node.question_count !== undefined) {
    return `${props.node.question_count} 题`;
  }
  if (props.node.count !== undefined) {
    return `${props.node.count} 篇`;
  }
  return null;
});

const handleClick = () => {
  if (hasChildren.value || hasItems.value) {
    if (props.node.toggleNode) {
      props.node.toggleNode(currentPath.value);
    }
  } else if (props.onNodeClick) {
    props.onNodeClick(props.node);
  }
};

const handleItemClick = (item) => {
  if (props.onNodeClick) {
    props.onNodeClick(item);
  }
};

const handleEdit = () => {
  if (props.onEdit && props.node.id) {
    props.onEdit(props.node);
  }
};

const handleDelete = () => {
  if (props.onDelete && props.node.id) {
    props.onDelete(props.node);
  }
};

const handleCreate = () => {
  if (props.onCreate) {
    props.onCreate(props.node);
  }
};

const handleCreateCategory = () => {
  if (props.onCreateCategory) {
    props.onCreateCategory(props.node);
  }
};

const handleEditCategory = () => {
  if (props.onEditCategory && props.node.id) {
    props.onEditCategory(props.node);
  }
};

const handleDeleteCategory = () => {
  if (props.onDeleteCategory && props.node.id) {
    props.onDeleteCategory(props.node);
  }
};

const handleItemEdit = (item) => {
  if (props.onEdit && item.id) {
    props.onEdit(item);
  }
};

const handleItemDelete = (item) => {
  if (props.onDelete && item.id) {
    props.onDelete(item);
  }
};

const getNodeTitle = (node) => {
  if (typeof node === 'string') return node;
  return node.title || node.name || '';
};

const getItemTitle = (item) => {
  if (typeof item === 'string') return item;
  return item.title || item.name || '';
};

const getChildKey = (child, index) => {
  if (child.id) return child.id;
  if (child.name) return child.name;
  return index;
};
</script>

<style scoped>
.admin-tree-node {
  margin-left: 0;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-primary);
  border-radius: 8px;
  margin-bottom: 8px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.node-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  transition: all 0.2s;
  user-select: none;
  position: relative;
}

.node-header.has-children.clickable,
.node-header.clickable {
  cursor: pointer;
}

.node-header:hover.has-children,
.node-header:hover.clickable {
  background: var(--color-bg-secondary);
}

.toggle-icon {
  display: flex;
  align-items: center;
  margin-right: 8px;
  color: var(--primary-600);
  transition: transform 0.2s;
}

:global(.dark) .toggle-icon {
  color: var(--primary-400);
}

.leaf-icon {
  display: flex;
  align-items: center;
  margin-right: 8px;
  color: var(--success-500);
}

:global(.dark) .leaf-icon {
  color: var(--success-600);
}

.node-title {
  font-weight: 600;
  color: var(--color-text-primary);
  font-size: 15px;
  flex: 1;
}

.node-count {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-left: 8px;
  background: rgba(107, 114, 128, 0.1);
  padding: 2px 8px;
  border-radius: 12px;
}

:global(.dark) .node-count {
  color: rgba(148, 163, 184, 0.9);
  background: rgba(148, 163, 184, 0.15);
}

.node-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.node-header:hover .node-actions {
  opacity: 1;
}

.action-btn {
  padding: 4px 6px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: transparent;
  color: var(--color-text-secondary);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background: var(--color-bg-secondary);
}

.edit-btn:hover {
  color: var(--primary-600);
  background: var(--primary-50);
}

.delete-btn:hover {
  color: #dc2626;
  background: #fee2e2;
}

.create-btn:hover {
  color: var(--success-600);
  background: var(--success-50);
}

.node-children {
  padding: 0 0 8px 24px;
  background: var(--color-bg-secondary);
}

:global(.dark) .node-children {
  background: rgba(15, 23, 42, 0.6);
}

.node-items {
  padding: 12px 16px 12px 48px;
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border-primary);
}

:global(.dark) .node-items {
  background: rgba(30, 41, 59, 0.7);
  border-top-color: rgba(148, 163, 184, 0.2);
}

.item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  margin: 4px 0;
  color: var(--color-text-primary);
  font-size: 14px;
  line-height: 1.5;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
  background: transparent;
  position: relative;
}

:global(.dark) .item {
  color: rgba(226, 232, 240, 0.9);
}

.item:hover {
  color: var(--primary-600);
  background: rgba(37, 99, 235, 0.08);
  transform: translateX(2px);
}

:global(.dark) .item:hover {
  color: var(--primary-400);
  background: rgba(96, 165, 250, 0.12);
}

.item-icon {
  flex-shrink: 0;
  margin-right: 10px;
  color: var(--primary-500);
  opacity: 0.7;
  transition: all 0.2s ease;
}

:global(.dark) .item-icon {
  color: var(--primary-400);
}

.item:hover .item-icon {
  opacity: 1;
  color: var(--primary-600);
}

:global(.dark) .item:hover .item-icon {
  color: var(--primary-400);
}

.item-title {
  flex: 1;
  font-weight: 500;
  word-break: break-word;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.item:hover .item-actions {
  opacity: 1;
}


@media (max-width: 768px) {
  .node-title {
    font-size: 14px;
  }
  
  .item {
    font-size: 13px;
  }
}
</style>

