<template>
  <div class="topic-selector">
    <!-- 标题区域 -->
    <div class="selector-header">
      <h2 class="selector-title">选择技术主题</h2>
      <p class="selector-subtitle">探索不同领域的技术文章</p>
    </div>

    <!-- 搜索和筛选 -->
    <div class="selector-toolbar">
      <div class="search-section">
        <div class="search-box">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            v-model="searchQuery"
            placeholder="搜索主题..."
            class="search-input"
            @input="handleSearch"
          />
        </div>
      </div>

      <div class="filter-section">
        <button
          v-for="filter in filters"
          :key="filter.key"
          @click="setActiveFilter(filter.key)"
          :class="['filter-btn', { active: activeFilter === filter.key }]"
        >
          {{ filter.label }}
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载主题中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="filteredTopics.length === 0" class="empty-state">
      <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
      </svg>
      <h3 class="empty-title">没有找到主题</h3>
      <p class="empty-subtitle">尝试其他搜索关键词或筛选条件</p>
    </div>

    <!-- 主题卡片网格 -->
    <div v-else class="topics-grid">
      <div
        v-for="topic in filteredTopics"
        :key="topic.name"
        class="topic-card"
        :class="{
          featured: topic.featured,
          trending: topic.trending
        }"
        @click="selectTopic(topic)"
        @keydown.enter="selectTopic(topic)"
        tabindex="0"
      >
        <!-- 卡片装饰 -->
        <div class="card-decoration">
          <div v-if="topic.featured" class="badge featured-badge">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z"/>
            </svg>
            精选
          </div>
          <div v-if="topic.trending" class="badge trending-badge">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 3V12A9 9 0 1 0 21 12V3"/>
            </svg>
            热门
          </div>
        </div>

        <!-- 主题图标 -->
        <div class="topic-icon">
          <component :is="getTopicIcon(topic.name)" />
        </div>

        <!-- 卡片内容 -->
        <div class="card-content">
          <h3 class="topic-title">{{ topic.name }}</h3>
          <p class="topic-description">{{ topic.description || '深入了解这个技术领域' }}</p>

          <!-- 统计信息 -->
          <div class="topic-stats">
            <div class="stat-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
              </svg>
              <span>{{ topic.count || 0 }} 篇文章</span>
            </div>

            <div class="stat-item" v-if="topic.views">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12S5 4 12 4s11 8 11 8-4 8-11 8S1 12 1 12z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <span>{{ formatNumber(topic.views) }} 阅读</span>
            </div>

            <div class="stat-item" v-if="topic.lastUpdated">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12,6 12,12 16,14"/>
              </svg>
              <span>{{ formatRelativeTime(topic.lastUpdated) }}</span>
            </div>
          </div>

          <!-- 热门标签 -->
          <div class="topic-tags" v-if="topic.popularTags && topic.popularTags.length">
            <span
              v-for="tag in topic.popularTags.slice(0, 3)"
              :key="tag"
              class="topic-tag"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- 悬停效果 -->
        <div class="card-hover-effect">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14"/>
            <path d="M12 5l7 7-7 7"/>
          </svg>
          <span>开始阅读</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

const props = defineProps({
  topics: {
    type: Array,
    required: true,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['topic-select'])

// 响应式数据
const searchQuery = ref('')
const activeFilter = ref('all')

// 筛选选项
const filters = ref([
  { key: 'all', label: '全部' },
  { key: 'featured', label: '精选' },
  { key: 'trending', label: '热门' },
  { key: 'recent', label: '最新' }
])

// 计算属性
const filteredTopics = computed(() => {
  let filtered = props.topics || []

  // 搜索过滤
  if (searchQuery.value && searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(topic =>
      (topic.name && topic.name.toLowerCase().includes(query)) ||
      (topic.description && topic.description.toLowerCase().includes(query)) ||
      (topic.popularTags && Array.isArray(topic.popularTags) &&
        topic.popularTags.some(tag => tag && tag.toLowerCase().includes(query)))
    )
  }

  // 分类过滤
  switch (activeFilter.value) {
    case 'featured':
      filtered = filtered.filter(topic => topic.featured)
      break
    case 'trending':
      filtered = filtered.filter(topic => topic.trending || topic.views > 1000)
      break
    case 'recent':
      // 使用后端配置的 latest 标签
      filtered = filtered.filter(topic => topic.latest === true)
      break
  }

  // 排序：精选在前，然后按文章数量
  return filtered.sort((a, b) => {
    if (a.featured && !b.featured) return -1
    if (!a.featured && b.featured) return 1
    return (b.count || 0) - (a.count || 0)
  })
})

// 方法
const getTopicIcon = (topicName) => {
  const icons = {
    'Spring': {
      template: `<svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M21.8537 1.4158c-.4644-.2122-.8934-.0619-1.133.3608L18.0323 6.3784c-.2396.4227.0159.9668.5107 1.0834l2.4134.5691c.4947.1166.8097-.1543.7901-.6803l-.0986-2.6415c-.0196-.5259-.2929-.8485-.7942-.2943z"/>
        <path d="M.1463 22.5842c.4644.2122.8934.0619 1.133-.3608L3.9677 17.6216c.2396-.4227-.0159-.9668-.5107-1.0834L.9436 15.947c-.4947-.1166-.8097.1543-.7901.6803l.0986 2.6415c.0196.5259.2929.8485.7942.2943z"/>
        <path d="M12 0C5.3726 0 0 5.3726 0 12s5.3726 12 12 12 12-5.3726 12-12S18.6274 0 12 0zm0 21.6c-5.3019 0-9.6-4.2981-9.6-9.6S6.6981 2.4 12 2.4s9.6 4.2981 9.6 9.6-4.2981 9.6-9.6 9.6z"/>
      </svg>`
    },
    'Vue': {
      template: `<svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M12,2.2467A10.00042,10.00042,0,0,0,8.83752,21.73419c.5376.11971.73623-.23347.73623-.51879,0-.25506-.01242-1.33958-.01242-2.42633A5.76874,5.76874,0,0,1,8.33752,16.73419c-.5376-.11971-.73623.23347-.73623.51879,0,.25506.01242,1.33958.01242,2.42633A5.76874,5.76874,0,0,1,12,21.7534a9.99116,9.99116,0,0,0,0-19.5067Z"/>
      </svg>`
    },
    'React': {
      template: `<svg viewBox="0 0 24 24" fill="currentColor">
        <circle cx="12" cy="12" r="2"/>
        <path d="M20.2,15.7A3.1,3.1,0,0,0,22,18a3,3,0,0,0-3,3c-.7-.6-1.2-1.5-1.2-2.5s.5-1.9,1.2-2.5A5,5,0,0,1,20.2,15.7Z"/>
        <path d="M3.8,8.3A3.1,3.1,0,0,0,2,6,3,3,0,0,0,5,3c.7.6,1.2,1.5,1.2,2.5S5.7,7.4,5,8A5,5,0,0,1,3.8,8.3Z"/>
        <ellipse cx="12" cy="12" rx="9" ry="4" fill="none" stroke="currentColor" stroke-width="1"/>
        <ellipse cx="12" cy="12" rx="4" ry="9" fill="none" stroke="currentColor" stroke-width="1" transform="rotate(60 12 12)"/>
        <ellipse cx="12" cy="12" rx="4" ry="9" fill="none" stroke="currentColor" stroke-width="1" transform="rotate(-60 12 12)"/>
      </svg>`
    },
    'Python': {
      template: `<svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M11.75,0C7.92,0,8.27.13,8.27,2.92v1.87H12V6H4.89C2.1,6,0,7.48,0,12s2.1,6,4.89,6h2.38V15.59c0-2.16,1.87-4,4-4h4.24c1.75,0,3.16-1.42,3.16-3.17V2.92C18.67.13,16.83,0,11.75,0ZM9,2.08a.79.79,0,1,1-.79.79A.79.79,0,0,1,9,2.08Z"/>
        <path d="M19.11,18H16.73V20.41c0,2.16-1.87,4-4,4H8.49c-1.75,0-3.16,1.42-3.16,3.17V21.08c0-2.79,1.84-2.92,6.92-2.92V16.13H16v1.18h5.11C23.9,18,24,16.52,24,12s-.1-6-2.89-6H19.11ZM15,21.92a.79.79,0,1,1,.79-.79A.79.79,0,0,1,15,21.92Z"/>
      </svg>`
    },
    'default': {
      template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
      </svg>`
    }
  }
  return icons[topicName] || icons['default']
}

const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num?.toString() || '0'
}

const formatRelativeTime = (dateString) => {
  return dayjs(dateString).fromNow()
}

const selectTopic = (topic) => {
  emit('topic-select', topic)
}

const setActiveFilter = (filterKey) => {
  activeFilter.value = filterKey
}

const handleSearch = () => {
  // 搜索时重置过滤器为全部
  activeFilter.value = 'all'
}
</script>

<style scoped>
.topic-selector {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-6);
}

/* 标题区域 */
.selector-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.selector-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-3);
  background: linear-gradient(135deg, var(--primary-600) 0%, var(--purple-600) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.selector-subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  margin: 0;
}

/* 工具栏 */
.selector-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-8);
  padding: var(--space-4);
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border-primary);
  box-shadow: var(--shadow-sm);
}

.search-section {
  flex: 1;
  max-width: 400px;
}

.search-box {
  position: relative;
}

.search-icon {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: var(--color-text-muted);
}

.search-input {
  width: 100%;
  padding: var(--space-3) var(--space-3) var(--space-3) var(--space-12);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-sm);
  background-color: var(--color-bg-secondary);
  transition: all var(--transition-normal);
}

.search-input:focus {
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  background-color: var(--color-bg-primary);
}

.filter-section {
  display: flex;
  gap: var(--space-2);
}

.filter-btn {
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  background-color: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.filter-btn:hover {
  background-color: var(--primary-50);
  border-color: var(--primary-300);
  color: var(--color-text-primary);
}

.filter-btn.active {
  background-color: var(--primary-600);
  border-color: var(--primary-600);
  color: white;
}

/* 状态显示 */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-16);
  color: var(--color-text-secondary);
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-border-primary);
  border-top: 4px solid var(--primary-600);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--space-4);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  width: 80px;
  height: 80px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-4);
}

.empty-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.empty-subtitle {
  color: var(--color-text-secondary);
}

/* 主题卡片网格 - 超紧凑布局 */
.topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--space-3);
}

/* 主题卡片 - 超紧凑优化 */
.topic-card {
  position: relative;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  cursor: pointer;
  transition: all var(--transition-smooth);
  overflow: hidden;
  min-height: 130px;
  max-height: 150px;
}

.topic-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  border-color: var(--primary-300);
}

.topic-card.featured {
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--color-bg-primary) 100%);
  border-color: var(--primary-200);
}

.topic-card.trending {
  background: linear-gradient(135deg, var(--orange-50) 0%, var(--color-bg-primary) 100%);
  border-color: var(--orange-200);
}

/* 卡片装饰 */
.card-decoration {
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  display: flex;
  gap: var(--space-2);
}

.badge {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.badge svg {
  width: 12px;
  height: 12px;
}

.featured-badge {
  background: linear-gradient(135deg, var(--yellow-400) 0%, var(--orange-500) 100%);
  color: white;
}

.trending-badge {
  background: linear-gradient(135deg, var(--red-500) 0%, var(--pink-500) 100%);
  color: white;
}

/* 主题图标 - 超紧凑优化 */
.topic-icon {
  width: 32px;
  height: 32px;
  margin: 0 auto var(--space-2) auto;
  padding: var(--space-1);
  background: linear-gradient(135deg, var(--primary-600) 0%, var(--purple-600) 100%);
  border-radius: var(--radius-md);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
}

.topic-icon svg {
  width: 100%;
  height: 100%;
}

/* 卡片内容 */
.card-content {
  text-align: center;
}

.topic-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1) 0;
  line-height: 1.1;
}

.topic-description {
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-2) 0;
  line-height: 1.3;
  font-size: var(--font-size-xs);
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 统计信息 - 超紧凑优化 */
.topic-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: var(--space-2);
  padding: var(--space-1);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-sm);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 10px;
  color: var(--color-text-muted);
}

.stat-item svg {
  width: 10px;
  height: 10px;
}

/* 热门标签 */
.topic-tags {
  display: flex;
  justify-content: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.topic-tag {
  background-color: var(--color-bg-muted);
  color: var(--color-text-secondary);
  padding: 2px var(--space-1);
  border-radius: var(--radius-sm);
  font-size: 9px;
  font-weight: var(--font-weight-medium);
}

/* 悬停效果 */
.card-hover-effect {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
  color: white;
  padding: var(--space-3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-weight: var(--font-weight-medium);
  transform: translateY(100%);
  transition: transform var(--transition-smooth);
}

.card-hover-effect svg {
  width: 18px;
  height: 18px;
}

.topic-card:hover .card-hover-effect {
  transform: translateY(0);
}

:global(.dark) .topic-selector {
  background: transparent;
}

:global(.dark) .selector-subtitle {
  color: rgba(226, 232, 240, 0.7);
}

:global(.dark) .selector-toolbar {
  background: rgba(15, 23, 42, 0.85);
  border-color: rgba(148, 163, 184, 0.2);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
}

:global(.dark) .search-input {
  background-color: rgba(30, 41, 59, 0.9);
  border-color: rgba(148, 163, 184, 0.3);
  color: rgba(226, 232, 240, 0.95);
}

:global(.dark) .search-input::placeholder {
  color: rgba(148, 163, 184, 0.8);
}

:global(.dark) .search-input:focus {
  background-color: rgba(15, 23, 42, 0.95);
  border-color: rgba(96, 165, 250, 0.6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
}

:global(.dark) .filter-btn {
  background-color: rgba(30, 41, 59, 0.85);
  border-color: rgba(148, 163, 184, 0.2);
  color: rgba(226, 232, 240, 0.8);
}

:global(.dark) .filter-btn:hover {
  background-color: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.4);
  color: rgba(255, 255, 255, 0.95);
}

:global(.dark) .filter-btn.active {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-color: transparent;
}

:global(.dark) .topic-card {
  background: rgba(15, 23, 42, 0.9);
  border-color: rgba(148, 163, 184, 0.2);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45);
}

:global(.dark) .topic-card.featured {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(15, 23, 42, 0.9));
  border-color: rgba(59, 130, 246, 0.4);
}

:global(.dark) .topic-card.trending {
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.2), rgba(15, 23, 42, 0.9));
  border-color: rgba(251, 146, 60, 0.4);
}

:global(.dark) .topic-description {
  color: rgba(226, 232, 240, 0.7);
}

:global(.dark) .topic-stats {
  background: rgba(30, 41, 59, 0.9);
}

:global(.dark) .stat-item {
  color: rgba(148, 163, 184, 0.85);
}

:global(.dark) .topic-tag {
  background-color: rgba(30, 41, 59, 0.9);
  color: rgba(191, 219, 254, 0.9);
}

:global(.dark) .card-hover-effect {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

/* 响应式设计 - 超紧凑优化 */
@media (max-width: 1200px) {
  .topics-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: var(--space-3);
  }

  .topic-card {
    min-height: 120px;
    max-height: 140px;
    padding: var(--space-2);
  }
}

@media (max-width: 768px) {
  .topic-selector {
    padding: var(--space-4);
  }

  .selector-title {
    font-size: var(--font-size-2xl);
  }

  .selector-toolbar {
    flex-direction: column;
    gap: var(--space-4);
    align-items: stretch;
  }

  .search-section {
    max-width: none;
  }

  .topics-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: var(--space-2);
  }

  .topic-card {
    min-height: 110px;
    max-height: 130px;
    padding: var(--space-2);
  }

  .topic-icon {
    width: 28px;
    height: 28px;
    margin-bottom: var(--space-1);
  }

  .topic-title {
    font-size: var(--font-size-sm);
  }

  .topic-stats {
    flex-direction: column;
    gap: 1px;
    padding: var(--space-1);
  }
}

@media (max-width: 480px) {
  .topics-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: var(--space-2);
  }

  .topic-card {
    min-height: 100px;
    max-height: 120px;
    padding: var(--space-2);
  }

  .topic-icon {
    width: 24px;
    height: 24px;
  }

  .topic-title {
    font-size: var(--font-size-xs);
  }

  .topic-description {
    font-size: 9px;
    -webkit-line-clamp: 1;
  }

  .stat-item {
    font-size: 8px;
  }

  .stat-item svg {
    width: 8px;
    height: 8px;
  }
}
</style>