<template>
  <div class="question-bank-container">
    <!-- 搜索区域 -->
    <div v-if="searchQuery" class="search-results-section">
      <div class="search-header">
        <h2>搜索结果：{{ searchQuery }}</h2>
        <button @click="clearSearch" class="btn-clear">清除搜索</button>
      </div>
      
      <!-- 题目搜索结果 -->
      <div v-if="searchResults.questions && searchResults.questions.length > 0" class="search-results">
        <h3>题目 ({{ searchResults.pagination.total }})</h3>
        <div class="question-grid">
          <div 
            v-for="question in searchResults.questions" 
            :key="question.id"
            class="question-card"
            @click="goToQuestion(question.id)"
          >
            <div class="question-header">
              <span class="question-type">{{ question.type === 'short_answer' ? '简答题' : '编程题' }}</span>
              <span class="difficulty" :class="`difficulty-${question.difficulty}`">
                {{ '⭐'.repeat(question.difficulty) }}
              </span>
            </div>
            <h4 class="question-title">{{ question.title }}</h4>
            <div class="question-tags">
              <span v-for="tag in question.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 标签搜索结果 -->
      <div v-if="searchResults.tags && searchResults.tags.length > 0" class="search-results">
        <h3>标签</h3>
        <div class="tag-list">
          <span 
            v-for="tag in searchResults.tags" 
            :key="tag.id"
            class="tag tag-clickable"
            @click="goToTag(tag.name)"
          >
            {{ tag.name }} ({{ tag.count }})
          </span>
        </div>
      </div>
      
      <div v-if="!searchResults.questions?.length && !searchResults.tags?.length" class="no-results">
        <p>没有找到相关结果</p>
      </div>
    </div>

    <!-- 分类展示 -->
    <div v-else class="categories-section">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="categories.length === 0" class="empty-state">
        <p>暂无分类</p>
      </div>

      <TreeView 
        v-else-if="treeData && (treeData.title || Array.isArray(treeData))"
        :data="treeData"
        :on-node-click="handleNodeClick"
      />
      <div v-else class="empty-state">
        <p>数据格式错误，请检查控制台</p>
        <p style="font-size: 12px; color: #999; margin-top: 8px;">treeData: {{ JSON.stringify(treeData) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex';
import axios from 'axios';
import TreeView from '@/components/TreeView.vue';

const router = useRouter();
const route = useRoute();
const store = useStore();

const categories = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const searchResults = ref({ questions: [], tags: [], pagination: {} });

const loadCategories = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/v1/question-bank/categories`);
    console.log('分类API响应:', response.data);
    if (response.data?.success) {
      categories.value = response.data.data || [];
      console.log('加载的分类数据:', categories.value);
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

const searchQuestions = async (query) => {
  loading.value = true;
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/v1/question-bank/search`, {
      params: { q: query }
    });
    if (response.data?.success) {
      searchResults.value = response.data.data || {};
    } else {
      console.error('搜索失败:', response.data?.error);
      searchResults.value = {};
    }
  } catch (error) {
    console.error('搜索失败:', error);
    searchResults.value = {};
  } finally {
    loading.value = false;
  }
};

const goToCategory = (categoryId) => {
  router.push(`/question-bank/category/${categoryId}`);
};

const goToQuestion = (questionId) => {
  router.push(`/question-bank/question/${questionId}`);
};

const goToTag = (tagName) => {
  router.push({
    path: '/question-bank',
    query: { tag: tagName }
  });
};

const clearSearch = () => {
  searchQuery.value = '';
  searchResults.value = {};
  router.push('/question-bank');
};

// 转换为树形结构
const treeData = computed(() => {
  if (!categories.value || categories.value.length === 0) {
    return [];
  }

  // 递归转换分类为树形节点
  const convertCategory = (cat) => {
    const node = {
      title: cat.name,
      id: cat.id,
      total_question_count: cat.total_question_count || cat.question_count || 0,
      question_count: cat.question_count || 0
    };

    // 如果有子分类，转换子分类
    if (cat.children && cat.children.length > 0) {
      node.children = cat.children.map(convertCategory);
    }

    // 如果有题目列表（items），转换为 items 格式
    if (cat.items && cat.items.length > 0) {
      node.items = cat.items.map(item => ({
        title: item.title,
        id: item.id,
        type: item.type,
        difficulty: item.difficulty
      }));
    }

    return node;
  };

  // 直接返回所有根分类的数组，让 TreeView 直接渲染多个根节点
  return categories.value.map(convertCategory);
});

const handleNodeClick = (node) => {
  // 如果 node 有 id 和 title，但没有 children 属性，说明是题目项
  // 题目项通常是从 items 数组中点击的
  if (node.id && node.title && !node.hasOwnProperty('children') && !node.hasOwnProperty('total_question_count')) {
    goToQuestion(node.id);
  }
  // 如果是分类节点（有 children 或 total_question_count），跳转到分类页面
  else if (node.id && (node.children || node.total_question_count !== undefined)) {
    goToCategory(node.id);
  }
};

// 监听路由查询参数
watch(() => route.query, (newQuery) => {
  if (newQuery.search) {
    searchQuery.value = newQuery.search;
    searchQuestions(newQuery.search);
  } else if (newQuery.tag) {
    // 可以在这里处理标签筛选
    searchQuery.value = '';
    searchResults.value = {};
  } else {
    searchQuery.value = '';
    searchResults.value = {};
  }
}, { immediate: true });

onMounted(() => {
  if (route.query.search) {
    searchQuery.value = route.query.search;
    searchQuestions(route.query.search);
  } else {
    loadCategories();
  }
});
</script>

<style scoped>
.question-bank-container {
  min-height: calc(100vh - 64px);
  background: transparent;
  padding: 0;
}

.section-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.section-header h1 {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.section-description {
  color: var(--color-text-secondary);
  font-size: var(--font-size-lg);
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

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-6);
  max-width: var(--container-max-width);
  margin: 0 auto;
}

.category-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-300);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.category-name {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.question-count {
  background: var(--primary-100);
  color: var(--primary-700);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.category-description {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-4);
  line-height: 1.6;
}

.subcategories {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-border-primary);
}

.subcategory-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) 0;
  cursor: pointer;
  transition: color var(--transition-normal);
}

.subcategory-item:hover {
  color: var(--primary-600);
}

.subcategory-name {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.subcategory-count {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

/* 搜索结果显示 */
.search-results-section {
  max-width: var(--container-max-width);
  margin: 0 auto;
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.search-header h2 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.btn-clear {
  padding: var(--space-2) var(--space-4);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.btn-clear:hover {
  background: var(--color-bg-muted);
  color: var(--color-text-primary);
}

.search-results {
  margin-bottom: var(--space-8);
}

.search-results h3 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-4);
}

.question-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-4);
}

.question-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.question-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary-300);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.question-type {
  background: var(--primary-100);
  color: var(--primary-700);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.difficulty {
  font-size: var(--font-size-sm);
}

.question-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-3) 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.question-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.tag {
  background: var(--color-bg-muted);
  color: var(--color-text-secondary);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
}

.tag-clickable {
  cursor: pointer;
  transition: all var(--transition-normal);
}

.tag-clickable:hover {
  background: var(--primary-100);
  color: var(--primary-700);
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.no-results {
  text-align: center;
  padding: var(--space-8);
  color: var(--color-text-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .question-bank-container {
    padding: var(--space-4);
  }

  .categories-grid {
    grid-template-columns: 1fr;
  }

  .question-grid {
    grid-template-columns: 1fr;
  }
}
</style>


