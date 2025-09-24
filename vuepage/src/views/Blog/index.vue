<template>
  <div class="blog-container">
    <!-- 面包屑导航 -->
    <Breadcrumb />

    <!-- 统计信息 -->
    <div class="stats-section">
      <div class="stats-container">
        <div class="stat-item">
          <span class="stat-value">{{ totalArticles }}</span>
          <span class="stat-label">篇文章</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ categories.length }}</span>
          <span class="stat-label">个分类</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ formatNumber(totalViews) }}</span>
          <span class="stat-label">总阅读</span>
        </div>
      </div>
    </div>

    <!-- 主题选择器 -->
    <div class="blog-content">
      <TopicSelector
        :topics="categories"
        :loading="loading"
        @topic-select="onTopicSelect"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import axios from 'axios';
import Breadcrumb from '@/components/Breadcrumb.vue';
import TopicSelector from '@/components/TopicSelector.vue';

const router = useRouter();
const store = useStore();

// 响应式数据
const categories = ref([]);
const loading = ref(false);

// 计算属性
const totalArticles = computed(() => {
  return categories.value.reduce((total, cat) => total + (cat.count || 0), 0);
});

const totalViews = computed(() => {
  return categories.value.reduce((total, cat) => total + (cat.views || 0), 0);
});

// 方法
const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num?.toString() || '0';
};

const loadCategories = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/blog/categories`);

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

// 生命周期
onMounted(() => {
  loadCategories();
});
</script>

<style scoped>
.blog-container {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--primary-25) 100%);
  position: relative;
}

/* 统计信息 - 右上角紧凑显示 */
.stats-section {
  position: absolute;
  top: 80px;
  right: var(--space-6);
  z-index: 10;
}

.stats-container {
  display: flex;
  gap: var(--space-3);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-xl);
  padding: var(--space-3) var(--space-4);
  border: 1px solid rgba(79, 140, 255, 0.1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.stat-item {
  text-align: center;
  padding: var(--space-1) var(--space-2);
  min-width: 50px;
}

.stat-value {
  display: block;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--primary-600);
  margin-bottom: var(--space-1);
  line-height: 1;
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  white-space: nowrap;
  line-height: 1;
}

.blog-content {
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: var(--space-6) var(--space-6) var(--space-8) var(--space-6);
  min-height: calc(100vh - 120px);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .stats-section {
    right: var(--space-4);
  }

  .stats-container {
    padding: var(--space-2) var(--space-3);
  }

  .stat-value {
    font-size: var(--font-size-base);
  }
}

@media (max-width: 768px) {
  .blog-content {
    padding: var(--space-4);
  }

  .stats-section {
    position: static;
    display: flex;
    justify-content: center;
    margin: var(--space-4) 0;
  }

  .stats-container {
    gap: var(--space-2);
    padding: var(--space-2);
  }

  .stat-item {
    padding: var(--space-1);
    min-width: 40px;
  }

  .stat-value {
    font-size: var(--font-size-sm);
  }

  .stat-label {
    font-size: 10px;
  }
}
</style>