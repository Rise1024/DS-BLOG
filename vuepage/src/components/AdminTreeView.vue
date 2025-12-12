<template>
  <div class="admin-tree-view">
    <!-- 如果 data 是数组，遍历渲染多个根节点 -->
    <template v-if="Array.isArray(rootNodes)">
      <AdminTreeNode 
        v-for="(node, index) in rootNodes" 
        :key="getNodeKey(node, index)"
        :node="node" 
        :path="''"
        :on-node-click="onNodeClick"
        :on-edit="onEdit"
        :on-delete="onDelete"
        :on-create="onCreate"
        :on-create-category="onCreateCategory"
        :on-edit-category="onEditCategory"
        :on-delete-category="onDeleteCategory"
        :is-root="true"
      />
    </template>
    <!-- 如果 data 是对象，渲染单个根节点 -->
    <AdminTreeNode 
      v-else
      :node="rootNode" 
      :path="''"
      :on-node-click="onNodeClick"
      :on-edit="onEdit"
      :on-delete="onDelete"
      :on-create="onCreate"
      :on-create-category="onCreateCategory"
      :on-edit-category="onEditCategory"
      :on-delete-category="onDeleteCategory"
      :is-root="true"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import AdminTreeNode from './AdminTreeNode.vue';

const props = defineProps({
  data: {
    type: [Object, Array],
    required: true
  },
  // 指定一个节点 id，初始时自动展开到该节点
  defaultExpandNodeId: {
    type: [String, Number],
    default: null
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
  }
});

const expanded = ref({});

const toggleNode = (path) => {
  expanded.value = {
    ...expanded.value,
    [path]: !expanded.value[path]
  };
};

// 根据节点 id 查找路径（以 node title 为片段）
const getNodeTitle = (node) => node?.title || node?.name || '';

const findPathById = (nodes, targetId, prefix = '') => {
  if (!nodes || !targetId) return null;
  const arr = Array.isArray(nodes) ? nodes : [nodes];
  for (const node of arr) {
    const title = getNodeTitle(node);
    const currentPath = prefix ? `${prefix}.${title}` : title;
    // 支持按 id 或标题/name 匹配（将 targetId 转换为数字进行比较）
    const nodeId = node.id != null ? String(node.id) : null;
    const targetIdStr = String(targetId);
    if (nodeId === targetIdStr || title === targetIdStr) {
      return [currentPath];
    }
    if (node.children && node.children.length > 0) {
      const childPath = findPathById(node.children, targetId, currentPath);
      if (childPath) {
        return [currentPath, ...childPath];
      }
    }
  }
  return null;
};

// 自动展开到指定节点
const expandToNode = () => {
  if (!props.defaultExpandNodeId || !props.data) return;
  const pathList = findPathById(props.data, props.defaultExpandNodeId);
  if (pathList && pathList.length > 0) {
    const next = { ...expanded.value };
    pathList.forEach((p) => {
      next[p] = true;
    });
    expanded.value = next;
  }
};

// 监听 data 变化
watch(
  () => props.data,
  () => {
    expandToNode();
  },
  { immediate: true, deep: true }
);

// 监听 defaultExpandNodeId 变化（路由参数变化时）
watch(
  () => props.defaultExpandNodeId,
  () => {
    expandToNode();
  },
  { immediate: true }
);

const getNodeKey = (node, index) => {
  if (node && node.id) return node.id;
  if (node && node.title) return node.title;
  return index;
};

// 处理数组数据（多个根分类）
const rootNodes = computed(() => {
  if (!props.data) {
    return [];
  }
  
  if (Array.isArray(props.data)) {
    return props.data.map(node => ({
      ...node,
      expanded: expanded,
      toggleNode: toggleNode
    }));
  }
  
  return null;
});

// 处理单个对象数据
const rootNode = computed(() => {
  if (!props.data) {
    return {
      title: '加载中...',
      children: [],
      expanded: expanded,
      toggleNode: toggleNode
    };
  }
  
  if (Array.isArray(props.data)) {
    return null;
  }
  
  return {
    ...props.data,
    expanded: expanded,
    toggleNode: toggleNode
  };
});
</script>

<style scoped>
.admin-tree-view {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  background: var(--color-bg-primary);
  min-height: calc(100vh - 200px);
}
</style>

