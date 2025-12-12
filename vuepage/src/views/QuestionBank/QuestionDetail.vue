<template>
  <div class="question-detail-container">
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="!question" class="error-state">
      <p>题目不存在</p>
      <button @click="goBack" class="btn-primary">返回列表</button>
    </div>

    <div v-else class="question-content">
      <!-- 题目头部 -->
      <div class="question-header">
        <button @click="goBack" class="btn-back">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5"/>
            <path d="M12 19l-7-7 7-7"/>
          </svg>
          返回
        </button>
        
        <div class="question-meta">
          <span class="question-type">{{ question.type === 'short_answer' ? '简答题' : '编程题' }}</span>
          <span class="difficulty" :class="`difficulty-${question.difficulty}`">
            {{ '⭐'.repeat(question.difficulty) }}
          </span>
          <div class="question-tags">
            <span v-for="tag in question.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>
      </div>

      <!-- 题目内容 -->
      <div class="question-body">
        <h1 class="question-title">{{ question.title }}</h1>
        
        <div class="question-content-text">
          <div v-html="formatContent(question.content)" class="markdown-content"></div>
        </div>

        <!-- 答案区域 -->
        <div class="answer-section">
          <div class="answer-header">
            <h3>答案</h3>
            <button 
              @click="toggleAnswer"
              class="btn-toggle-answer"
            >
              {{ showAnswer ? '隐藏答案' : '显示答案' }}
            </button>
          </div>
          
          <div v-if="showAnswer" class="answer-content">
            <div v-html="formatContent(question.answer)" class="markdown-content"></div>
            
            <div v-if="question.explanation" class="explanation">
              <h4>解析</h4>
              <div v-html="formatContent(question.explanation)" class="markdown-content"></div>
            </div>
          </div>
        </div>

        <!-- 相关文章 -->
        <div v-if="question.related_articles && question.related_articles.length > 0" class="related-articles">
          <h3>相关文章</h3>
          <div class="articles-list">
            <router-link 
              v-for="article in question.related_articles" 
              :key="article.id"
              :to="`/blog/article/${article.id}`"
              class="article-link"
            >
              <span class="article-title">{{ article.title }}</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </router-link>
          </div>
        </div>
      </div>

      <!-- 操作栏 -->
      <div class="question-actions">
        <button 
          @click="goToQuestion(question.navigation.prev)"
          :disabled="!question.navigation.prev"
          class="btn-nav"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          上一题
        </button>

        <button 
          v-if="isLoggedIn"
          @click="toggleFavorite"
          class="btn-favorite"
          :class="{ 'favorited': isFavorited }"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
          </svg>
          {{ isFavorited ? '已收藏' : '收藏' }}
        </button>

        <button 
          @click="goToQuestion(question.navigation.next)"
          :disabled="!question.navigation.next"
          class="btn-nav"
        >
          下一题
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex';
import axios from 'axios';
import { marked } from 'marked';

const router = useRouter();
const route = useRoute();
const store = useStore();

const question = ref(null);
const loading = ref(false);
const showAnswer = ref(false);
const isFavorited = ref(false);

const isLoggedIn = computed(() => !!store.state.token);

const formatContent = (content) => {
  if (!content) return '';
  return marked(content);
};

const loadQuestion = async (showAnswerParam = false) => {
  loading.value = true;
  try {
    const response = await axios.get(
      `${store.state.serverUrl}/api/v1/question-bank/questions/${route.params.id}`,
      { params: { show_answer: showAnswerParam } }
    );
    
    if (response.data?.success) {
      question.value = response.data.data;
      showAnswer.value = showAnswerParam;
      
      // 检查收藏状态
      if (isLoggedIn.value) {
        checkFavorite();
      }
    } else {
      console.error('加载题目失败:', response.data?.error);
      question.value = null;
    }
  } catch (error) {
    console.error('加载题目失败:', error);
    question.value = null;
  } finally {
    loading.value = false;
  }
};

const checkFavorite = async () => {
  if (!isLoggedIn.value) return;
  
  try {
    const response = await axios.get(
      `${store.state.serverUrl}/api/v1/question-bank/questions/${route.params.id}/favorite`,
      {
        headers: {
          'Authorization': store.state.token
        }
      }
    );
    
    if (response.data?.success) {
      isFavorited.value = response.data.data.favorited;
    }
  } catch (error) {
    console.error('检查收藏状态失败:', error);
  }
};

const toggleFavorite = async () => {
  if (!isLoggedIn.value) {
    // 可以在这里提示用户登录
    alert('请先登录');
    return;
  }
  
  try {
    const response = await axios.post(
      `${store.state.serverUrl}/api/v1/question-bank/questions/${route.params.id}/favorite`,
      {},
      {
        headers: {
          'Authorization': store.state.token
        }
      }
    );
    
    if (response.data?.success) {
      isFavorited.value = response.data.data.favorited;
    }
  } catch (error) {
    console.error('收藏操作失败:', error);
    if (error.response?.status === 401) {
      alert('请先登录');
    }
  }
};

const toggleAnswer = () => {
  showAnswer.value = !showAnswer.value;
  if (showAnswer.value && !question.value.answer) {
    // 如果答案未加载，重新加载
    loadQuestion(true);
  }
};

const goToQuestion = (questionId) => {
  if (!questionId) return;
  router.push(`/question-bank/question/${questionId}`);
};

const goBack = () => {
  router.back();
};

onMounted(() => {
  loadQuestion();
});

watch(() => route.params.id, () => {
  loadQuestion();
  showAnswer.value = false;
  isFavorited.value = false;
});
</script>

<style scoped>
.question-detail-container {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--primary-25) 100%);
  padding: var(--space-6);
}

.loading-state,
.error-state {
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

.question-content {
  max-width: 900px;
  margin: 0 auto;
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.question-header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border-primary);
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--gray-50) 100%);
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

.question-meta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.question-type {
  background: var(--primary-100);
  color: var(--primary-700);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.difficulty {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
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

.question-body {
  padding: var(--space-8);
}

.question-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-6) 0;
  line-height: 1.4;
}

.question-content-text {
  margin-bottom: var(--space-8);
  line-height: 1.8;
}

.answer-section {
  margin-top: var(--space-8);
  padding-top: var(--space-8);
  border-top: 2px solid var(--color-border-primary);
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.answer-header h3 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.btn-toggle-answer {
  padding: var(--space-2) var(--space-4);
  background: var(--primary-600);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-normal);
}

.btn-toggle-answer:hover {
  background: var(--primary-700);
}

.answer-content {
  margin-top: var(--space-4);
  padding: var(--space-6);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  border-left: 4px solid var(--primary-500);
}

.explanation {
  margin-top: var(--space-6);
  padding-top: var(--space-6);
  border-top: 1px solid var(--color-border-primary);
}

.explanation h4 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-4) 0;
}

.markdown-content {
  line-height: 1.8;
  color: var(--color-text-primary);
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  margin-top: var(--space-6);
  margin-bottom: var(--space-4);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.markdown-content :deep(pre) {
  background: var(--color-bg-muted);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  overflow-x: auto;
  margin: var(--space-4) 0;
}

.markdown-content :deep(code) {
  background: var(--color-bg-muted);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-mono);
}

.related-articles {
  margin-top: var(--space-8);
  padding-top: var(--space-8);
  border-top: 1px solid var(--color-border-primary);
}

.related-articles h3 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-4) 0;
}

.articles-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.article-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--color-text-primary);
  transition: all var(--transition-normal);
}

.article-link:hover {
  background: var(--primary-50);
  color: var(--primary-700);
}

.article-link svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.question-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-6);
  border-top: 1px solid var(--color-border-primary);
  background: var(--color-bg-secondary);
}

.btn-nav {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  color: var(--color-text-primary);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-normal);
}

.btn-nav:hover:not(:disabled) {
  background: var(--primary-100);
  border-color: var(--primary-300);
  color: var(--primary-700);
}

.btn-nav:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-nav svg {
  width: 18px;
  height: 18px;
}

.btn-favorite {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-normal);
}

.btn-favorite:hover {
  background: var(--primary-50);
  border-color: var(--primary-300);
  color: var(--primary-700);
}

.btn-favorite.favorited {
  background: var(--primary-100);
  border-color: var(--primary-300);
  color: var(--primary-700);
}

.btn-favorite svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

@media (max-width: 768px) {
  .question-detail-container {
    padding: var(--space-4);
  }

  .question-body {
    padding: var(--space-6);
  }

  .question-actions {
    flex-direction: column;
    gap: var(--space-3);
  }

  .btn-nav,
  .btn-favorite {
    width: 100%;
    justify-content: center;
  }
}
</style>


