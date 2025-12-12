<template>
  <div class="tree-view">
    <!-- 如果 data 是数组，遍历渲染多个根节点 -->
    <template v-if="Array.isArray(rootNodes)">
      <TreeNode 
        v-for="(node, index) in rootNodes" 
        :key="getNodeKey(node, index)"
        :node="node" 
        :path="''"
        :on-node-click="onNodeClick"
        :is-root="true"
      />
    </template>
    <!-- 如果 data 是对象，渲染单个根节点 -->
    <TreeNode 
      v-else
      :node="rootNode" 
      :path="''"
      :on-node-click="onNodeClick"
      :is-root="true"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import TreeNode from './TreeNode.vue';

const props = defineProps({
  data: {
    type: [Object, Array],
    required: true
  },
  onNodeClick: {
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
  
  // 如果是数组，返回 null（使用 rootNodes）
  if (Array.isArray(props.data)) {
    return null;
  }
  
  // 如果是对象，返回处理后的节点
  return {
    ...props.data,
    expanded: expanded,
    toggleNode: toggleNode
  };
});
</script>

<style scoped>
.tree-view {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
  background: var(--color-bg-primary);
  min-height: 100vh;
}

@media (max-width: 768px) {
  .tree-view {
    padding: 16px;
  }
}
</style>

