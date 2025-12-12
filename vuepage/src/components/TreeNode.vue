<template>
  <div class="tree-node" :class="{ 'is-root': isRoot }">
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
    </div>
    
    <div v-if="isExpanded && hasChildren" class="node-children">
      <TreeNode 
        v-for="(child, index) in node.children" 
        :key="getChildKey(child, index)"
        :node="{
          ...child,
          expanded: node.expanded,
          toggleNode: node.toggleNode
        }"
        :path="currentPath"
        :on-node-click="onNodeClick"
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
    // 传递完整的 item 对象，包括 id
    props.onNodeClick(item);
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
.tree-node {
  margin-left: 0;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-primary);
  border-radius: 8px;
  margin-bottom: 8px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.tree-node.is-root {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-primary);
}

.node-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  transition: all 0.2s;
  user-select: none;
}

.node-header.has-children.clickable,
.node-header.clickable {
  cursor: pointer;
}

.node-header:hover.has-children,
.node-header:hover.clickable {
  background: var(--color-bg-secondary);
}

.tree-node.is-root > .node-header {
  color: var(--color-text-primary);
}

.tree-node.is-root > .node-header .node-title {
  color: var(--color-text-primary);
  font-size: 24px;
  font-weight: 700;
}

.tree-node.is-root > .node-header .toggle-icon {
  color: var(--primary-600);
}

:global(.dark) .tree-node.is-root > .node-header .toggle-icon {
  color: var(--primary-400);
}

.tree-node.is-root > .node-header .node-count {
  color: var(--color-text-secondary);
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
  color: #6b7280;
  margin-left: 8px;
  background: rgba(107, 114, 128, 0.1);
  padding: 2px 8px;
  border-radius: 12px;
}

:global(.dark) .node-count {
  color: rgba(148, 163, 184, 0.9);
  background: rgba(148, 163, 184, 0.15);
}

.node-children {
  padding: 0 0 8px 24px;
  background: #fafbfc;
}

:global(.dark) .node-children {
  background: rgba(15, 23, 42, 0.6);
}

.tree-node.is-root > .node-children {
  background: var(--color-bg-secondary);
  padding: 16px;
}

.node-items {
  padding: 12px 16px 12px 48px;
  background: #f8f9fa;
  border-top: 1px solid #e5e7eb;
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

@media (max-width: 768px) {
  .node-title {
    font-size: 14px;
  }
  
  .item {
    font-size: 13px;
    padding: 8px 10px;
  }
  
  .item-icon {
    width: 12px;
    height: 12px;
    margin-right: 8px;
  }

  .tree-node.is-root > .node-header .node-title {
    font-size: 20px;
  }
}
</style>

