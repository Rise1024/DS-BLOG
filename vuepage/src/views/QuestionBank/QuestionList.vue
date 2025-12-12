<template>
  <div class="question-list-container">
    <div class="list-header">
      <button @click="goBack" class="btn-back">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5"/>
          <path d="M12 19l-7-7 7-7"/>
        </svg>
        返回
      </button>
      <h1 v-if="category">{{ category.name }}</h1>
      <p v-if="category && category.description" class="category-desc">{{ category.description }}</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else class="questions-section">
      <!-- 筛选栏 -->
      <div class="filters">
        <div class="filter-group">
          <label>难度：</label>
          <select v-model="selectedDifficulty" @change="loadQuestions" class="filter-select">
            <option value="">全部</option>
            <option value="1">⭐ 简单</option>
            <option value="2">⭐⭐ 较易</option>
            <option value="3">⭐⭐⭐ 中等</option>
            <option value="4">⭐⭐⭐⭐ 较难</option>
            <option value="5">⭐⭐⭐⭐⭐ 困难</option>
          </select>
        </div>
        <div class="filter-group">
          <label>类型：</label>
          <select v-model="selectedType" @change="loadQuestions" class="filter-select">
            <option value="">全部</option>
            <option value="short_answer">简答题</option>
            <option value="programming">编程题</option>
          </select>
        </div>
      </div>

      <!-- 题目列表 -->
      <div v-if="questions.length > 0" class="questions-list">
        <div 
          v-for="question in questions" 
          :key="question.id"
          class="question-item"
          @click="goToQuestion(question.id)"
        >
          <div class="question-item-header">
            <span class="question-type">{{ question.type === 'short_answer' ? '简答题' : '编程题' }}</span>
            <span class="difficulty" :class="`difficulty-${question.difficulty}`">
              {{ '⭐'.repeat(question.difficulty) }}
            </span>
          </div>
          <h3 class="question-item-title">{{ question.title }}</h3>
          <div class="question-item-tags">
            <span v-for="tag in question.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <p>暂无题目</p>
      </div>

      <!-- 分页 -->
      <div v-if="pagination.total_pages > 1" class="pagination">
        <button 
          @click="changePage(pagination.page - 1)"
          :disabled="pagination.page <= 1"
          class="page-btn"
        >
          上一页
        </button>
        <span class="page-info">
          第 {{ pagination.page }} / {{ pagination.total_pages }} 页
          (共 {{ pagination.total }} 题)
        </span>
        <button 
          @click="changePage(pagination.page + 1)"
          :disabled="pagination.page >= pagination.total_pages"
          class="page-btn"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex';
import axios from 'axios';

const router = useRouter();
const route = useRoute();
const store = useStore();

const category = ref(null);
const questions = ref([]);
const loading = ref(false);
const selectedDifficulty = ref('');
const selectedType = ref('');
const pagination = ref({
  page: 1,
  page_size: 20,
  total: 0,
  total_pages: 0
});

const loadCategory = async () => {
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/v1/question-bank/categories`);
    if (response.data?.success) {
      const categories = response.data.data || [];
      const findCategory = (cats, id) => {
        for (const cat of cats) {
          if (cat.id === parseInt(id)) return cat;
          if (cat.children) {
            const found = findCategory(cat.children, id);
            if (found) return found;
          }
        }
        return null;
      };
      category.value = findCategory(categories, route.params.categoryId);
    }
  } catch (error) {
    console.error('加载分类失败:', error);
  }
};

const loadQuestions = async () => {
  loading.value = true;
  try {
    const params = {
      category_id: route.params.categoryId,
      page: pagination.value.page,
      page_size: pagination.value.page_size
    };
    
    if (selectedDifficulty.value) {
      params.difficulty = parseInt(selectedDifficulty.value);
    }
    if (selectedType.value) {
      params.type = selectedType.value;
    }
    
    const response = await axios.get(`${store.state.serverUrl}/api/v1/question-bank/questions`, { params });
    
    if (response.data?.success) {
      questions.value = response.data.data || [];
      pagination.value = response.data.pagination || pagination.value;
    } else {
      console.error('加载题目失败:', response.data?.error);
      questions.value = [];
    }
  } catch (error) {
    console.error('加载题目失败:', error);
    questions.value = [];
  } finally {
    loading.value = false;
  }
};

const changePage = (page) => {
  pagination.value.page = page;
  loadQuestions();
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const goToQuestion = (questionId) => {
  router.push(`/question-bank/question/${questionId}`);
};

const goBack = () => {
  router.push('/question-bank');
};

onMounted(() => {
  loadCategory();
  loadQuestions();
});

watch(() => route.params.categoryId, () => {
  loadCategory();
  pagination.value.page = 1;
  loadQuestions();
});
</script>

<style scoped>
.question-list-container {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--primary-25) 100%);
  padding: var(--space-6);
  max-width: var(--container-max-width);
  margin: 0 auto;
}

.list-header {
  margin-bottom: var(--space-6);
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-normal);
  margin-bottom: var(--space-4);
}

.btn-back:hover {
  background: var(--color-bg-muted);
  color: var(--color-text-primary);
}

.btn-back svg {
  width: 18px;
  height: 18px;
}

.list-header h1 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-2) 0;
}

.category-desc {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
}

.loading-state {
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

.filters {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  padding: var(--space-4);
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-primary);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.filter-group label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.filter-select {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.filter-select:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.question-item {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.question-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary-300);
}

.question-item-header {
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
  color: var(--color-text-secondary);
}

.question-item-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-3) 0;
  line-height: 1.5;
}

.question-item-tags {
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

.empty-state {
  text-align: center;
  padding: var(--space-8);
  color: var(--color-text-secondary);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-4);
  margin-top: var(--space-8);
  padding: var(--space-4);
}

.page-btn {
  padding: var(--space-2) var(--space-4);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.page-btn:hover:not(:disabled) {
  background: var(--primary-100);
  border-color: var(--primary-300);
  color: var(--primary-700);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

@media (max-width: 768px) {
  .question-list-container {
    padding: var(--space-4);
  }

  .filters {
    flex-direction: column;
    gap: var(--space-3);
  }

  .filter-group {
    width: 100%;
  }

  .filter-select {
    flex: 1;
  }

  .pagination {
    flex-direction: column;
    gap: var(--space-2);
  }
}
</style>


