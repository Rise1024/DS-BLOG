<template>
  <div class="blog-container">
    <!-- 面包屑导航 -->
    <Breadcrumb />


    <!-- 主题选择器 -->
    <div class="blog-content">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="categories.length === 0" class="empty-state">
        <p>暂无分类</p>
      </div>

      <TreeView 
        v-else-if="treeData && (Array.isArray(treeData) || treeData.title)"
        :data="treeData"
        :on-node-click="handleNodeClick"
      />
      <div v-else class="empty-state">
        <p>数据格式错误，请检查控制台</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import axios from 'axios';
import Breadcrumb from '@/components/Breadcrumb.vue';
import TreeView from '@/components/TreeView.vue';

const router = useRouter();
const store = useStore();

// 响应式数据
const categories = ref([]);
const loading = ref(false);

const loadCategories = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/v1/blog/categories`);

    if (response.data?.success) {
      categories.value = response.data.data || [];
    } else {
      console.error('加载分类失败:', response.data?.error);
      categories.value = [];
    }
  } catch (error) {
    console.error('加载分类失败:', error);
    categories.value = [];
  } finally {
    loading.value = false;
  }
};

const onTopicSelect = (topic) => {
  const topicName = typeof topic === 'string' ? topic : topic.name;

  // 导航到 BlogReader 页面
  router.push({
    name: 'BlogReader',
    params: { category: encodeURIComponent(topicName) }
  });
};

// 转换为树形结构
const treeData = computed(() => {
  if (!categories.value || categories.value.length === 0) {
    return [];
  }

  // 递归转换分类为树形节点
  const convertCategory = (cat) => {
    if (!cat) return null;
    
    const node = {
      title: cat.name,
      name: cat.name,
      count: cat.count || 0
    };

    // 如果有子分类，转换为 children（递归处理）
    if (cat.children && cat.children.length > 0) {
      node.children = cat.children.map(convertCategory).filter(n => n !== null);
    }

    // 如果有文章，转换为 items（支持 items 或 articles 字段）
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

  // 直接返回所有根分类的数组，让 TreeView 直接渲染多个根节点
  const result = categories.value.map(convertCategory).filter(n => n !== null);
  console.log('博客转换后的 treeData:', result);
  return result;
});

const handleNodeClick = (node) => {
  // 如果是分类节点
  if (node.name && !node.id) {
    onTopicSelect(node);
  }
  // 如果是文章节点
  else if (node.id) {
    router.push({
      name: 'BlogArticle',
      params: { id: node.id }
    });
  }
};

// 生命周期
onMounted(() => {
  loadCategories();
});
</script>

<style scoped>
.blog-container {
  min-height: 100vh;
  background: transparent;
  position: relative;
}


.blog-content {
  max-width: 100%;
  margin: 0;
  padding: 0;
  min-height: calc(100vh - 120px);
}

:global(.dark) .blog-content {
  color: var(--color-text-primary);
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: var(--color-text-secondary);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border-primary);
  border-top: 3px solid var(--primary-600);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--space-4);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .blog-content {
    padding: var(--space-4);
  }
}
</style>