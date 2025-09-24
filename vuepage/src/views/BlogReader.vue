<template>
  <div class="blog-reader">
    <!-- 面包屑导航 -->
    <Breadcrumb />

    <!-- 三栏布局容器 -->
    <div class="reader-layout" :class="{
      'sidebar-collapsed': leftSidebarCollapsed,
      'outline-collapsed': rightSidebarCollapsed
    }">

      <!-- 左侧文档目录 -->
      <aside class="left-sidebar" :class="{ 'collapsed': leftSidebarCollapsed }">
        <div class="sidebar-header">
          <div class="category-info">
            <div class="category-icon">
              <component :is="getCategoryIcon(currentCategory)" />
            </div>
            <div class="category-details">
              <h3 class="category-title">{{ currentCategory }}</h3>
              <span class="article-count">{{ articles.length }} 篇文章</span>
            </div>
          </div>

          <button @click="toggleLeftSidebar" class="collapse-btn" :title="leftSidebarCollapsed ? '展开目录' : '收起目录'">
            <svg class="collapse-icon" :class="{ 'rotated': leftSidebarCollapsed }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 18l-6-6 6-6"/>
            </svg>
          </button>
        </div>

        <div class="sidebar-content" v-if="!leftSidebarCollapsed">
          <!-- 搜索框 -->
          <div class="search-section">
            <div class="search-box">
              <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/>
                <path d="m21 21-4.35-4.35"/>
              </svg>
              <input
                v-model="searchQuery"
                placeholder="搜索文章..."
                class="search-input"
              />
            </div>
          </div>

          <!-- 文章列表 -->
          <nav class="articles-nav">
            <div
              v-for="article in filteredArticles"
              :key="article.id"
              class="article-nav-item"
              :class="{
                'active': currentArticle?.id === article.id,
                'reading': isReading(article.id)
              }"
              @click="selectArticle(article)"
            >
              <div class="article-nav-content">
                <h4 class="article-nav-title">{{ article.title }}</h4>
                <p class="article-nav-excerpt">{{ article.description || '暂无描述' }}</p>

                <div class="article-nav-meta">
                  <span class="article-date">{{ formatDate(article.createdAt) }}</span>

                  <div class="article-indicators">
                    <span class="reading-time" v-if="article.reading_time">
                      {{ article.reading_time }}min
                    </span>

                    <div class="article-status">
                      <svg v-if="isReading(article.id)" class="status-icon reading" viewBox="0 0 24 24" fill="currentColor">
                        <circle cx="12" cy="12" r="10"/>
                      </svg>

                      <svg v-else-if="isCompleted(article.id)" class="status-icon completed" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                        <polyline points="22,4 12,14.01 9,11.01"/>
                      </svg>
                    </div>
                  </div>
                </div>

                <!-- 标签 -->
                <div class="article-nav-tags" v-if="article.tags && article.tags.length">
                  <span
                    v-for="tag in article.tags.slice(0, 2)"
                    :key="tag"
                    class="article-nav-tag"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>

              <!-- 进度指示器 -->
              <div class="reading-progress" v-if="getReadingProgress(article.id)">
                <div class="progress-bar" :style="{ width: getReadingProgress(article.id) + '%' }"></div>
              </div>
            </div>
          </nav>
        </div>

        <!-- 折叠状态的快捷操作 -->
        <div v-else class="sidebar-collapsed-content">
          <button @click="toggleLeftSidebar" class="expand-btn" title="展开文档目录">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M3 12h18M3 18h18"/>
            </svg>
          </button>
        </div>
      </aside>

      <!-- 中间文章内容区 -->
      <main class="main-content">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>

        <div v-else-if="!currentArticle" class="empty-state">
          <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
          <h3 class="empty-title">选择一篇文章开始阅读</h3>
          <p class="empty-subtitle">从左侧目录中选择您感兴趣的文章</p>
        </div>

        <article v-else class="article-reader">
          <!-- 文章头部 -->
          <header class="article-header">
            <div class="article-meta">
              <span class="article-date">{{ formatDate(currentArticle.createdAt) }}</span>
              <span class="reading-time">{{ currentArticle.reading_time || 5 }}分钟阅读</span>
              <span class="word-count">{{ currentArticle.word_count || 0 }}字</span>
            </div>

            <h1 class="article-title">{{ currentArticle.title }}</h1>

            <div class="article-tags" v-if="currentArticle.tags && currentArticle.tags.length">
              <span
                v-for="tag in currentArticle.tags"
                :key="tag"
                class="article-tag"
              >
                {{ tag }}
              </span>
            </div>

            <!-- 文章操作 -->
            <div class="article-actions">
              <button @click="toggleBookmark" class="action-btn" :class="{ 'active': isBookmarked }">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M19 21L12 16L5 21V5C5 3.9 5.9 3 7 3H17C18.1 3 19 3.9 19 5V21Z"/>
                </svg>
                {{ isBookmarked ? '已收藏' : '收藏' }}
              </button>

              <button @click="shareArticle" class="action-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="18" cy="5" r="3"/>
                  <circle cx="6" cy="12" r="3"/>
                  <circle cx="18" cy="19" r="3"/>
                  <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
                  <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
                </svg>
                分享
              </button>

              <button @click="printArticle" class="action-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="6,9 6,2 18,2 18,9"/>
                  <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
                  <rect x="6" y="14" width="12" height="8"/>
                </svg>
                打印
              </button>
            </div>
          </header>

          <!-- 文章正文 -->
          <div class="article-body">
            <div v-html="currentArticle.html_content" class="markdown-content"></div>
          </div>

          <!-- 文章导航 -->
          <footer class="article-footer">
            <div class="article-navigation">
              <button
                v-if="previousArticle"
                @click="selectArticle(previousArticle)"
                class="nav-btn nav-prev"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M15 18l-6-6 6-6"/>
                </svg>
                <div class="nav-info">
                  <span class="nav-label">上一篇</span>
                  <span class="nav-title">{{ previousArticle.title }}</span>
                </div>
              </button>

              <button
                v-if="nextArticle"
                @click="selectArticle(nextArticle)"
                class="nav-btn nav-next"
              >
                <div class="nav-info">
                  <span class="nav-label">下一篇</span>
                  <span class="nav-title">{{ nextArticle.title }}</span>
                </div>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 18l6-6-6-6"/>
                </svg>
              </button>
            </div>
          </footer>
        </article>
      </main>

      <!-- 右侧文章大纲 -->
      <aside class="right-sidebar" :class="{ 'collapsed': rightSidebarCollapsed }" v-if="currentArticle && currentArticle.headings && currentArticle.headings.length">
        <div class="outline-header">
          <h4 class="outline-title">文章大纲</h4>
          <button @click="toggleRightSidebar" class="collapse-btn" :title="rightSidebarCollapsed ? '展开大纲' : '收起大纲'">
            <svg class="collapse-icon" :class="{ 'rotated': rightSidebarCollapsed }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </button>
        </div>

        <nav class="outline-nav" v-if="!rightSidebarCollapsed">
          <ul class="outline-list">
            <li
              v-for="heading in currentArticle.headings"
              :key="heading.anchor"
              class="outline-item"
              :class="[
                `outline-level-${heading.level}`,
                { 'outline-active': activeHeading === heading.anchor }
              ]"
            >
              <a
                :href="`#${heading.anchor}`"
                @click="scrollToHeading(heading.anchor, $event)"
                class="outline-link"
              >
                {{ heading.title }}
              </a>
            </li>
          </ul>

          <!-- 阅读进度 -->
          <div class="reading-progress-section">
            <div class="progress-label">阅读进度</div>
            <div class="progress-circle">
              <svg class="progress-ring" width="60" height="60">
                <circle
                  class="progress-ring-bg"
                  cx="30"
                  cy="30"
                  r="26"
                  fill="transparent"
                  stroke="var(--color-border-primary)"
                  stroke-width="4"
                />
                <circle
                  class="progress-ring-fill"
                  cx="30"
                  cy="30"
                  r="26"
                  fill="transparent"
                  stroke="var(--primary-600)"
                  stroke-width="4"
                  :stroke-dasharray="circleCircumference"
                  :stroke-dashoffset="circleOffset"
                />
              </svg>
              <div class="progress-text">{{ Math.round(readingProgress) }}%</div>
            </div>
          </div>
        </nav>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import axios from 'axios'
import dayjs from 'dayjs'
import Breadcrumb from '@/components/Breadcrumb.vue'

const router = useRouter()
const route = useRoute()
const store = useStore()

// 响应式数据
const articles = ref([])
const currentArticle = ref(null)
const currentCategory = ref('')
const loading = ref(false)
const searchQuery = ref('')
const leftSidebarCollapsed = ref(false)
const rightSidebarCollapsed = ref(false)
const activeHeading = ref('')
const readingProgress = ref(0)
const isBookmarked = ref(false)

// 阅读状态
const readingStatus = ref({}) // { articleId: 'reading' | 'completed' }
const readingProgressMap = ref({}) // { articleId: percentage }

// 计算属性
const filteredArticles = computed(() => {
  const articlesList = articles.value || []

  if (!searchQuery.value || !searchQuery.value.trim()) return articlesList

  const query = searchQuery.value.toLowerCase().trim()
  return articlesList.filter(article =>
    (article.title && article.title.toLowerCase().includes(query)) ||
    (article.description && article.description.toLowerCase().includes(query)) ||
    (article.tags && Array.isArray(article.tags) &&
      article.tags.some(tag => tag && tag.toLowerCase().includes(query)))
  )
})

const currentArticleIndex = computed(() => {
  if (!currentArticle.value) return -1
  return articles.value.findIndex(article => article.id === currentArticle.value.id)
})

const previousArticle = computed(() => {
  const index = currentArticleIndex.value
  return index > 0 ? articles.value[index - 1] : null
})

const nextArticle = computed(() => {
  const index = currentArticleIndex.value
  return index >= 0 && index < articles.value.length - 1 ? articles.value[index + 1] : null
})

// 圆形进度条计算
const circleCircumference = computed(() => 2 * Math.PI * 26)
const circleOffset = computed(() => {
  const progress = readingProgress.value / 100
  return circleCircumference.value * (1 - progress)
})

// 方法
const getCategoryIcon = (categoryName) => {
  const icons = {
    'Spring': {
      template: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21.8537 1.4158c-.4644-.2122-.8934-.0619-1.133.3608L18.0323 6.3784c-.2396.4227.0159.9668.5107 1.0834l2.4134.5691c.4947.1166.8097-.1543.7901-.6803l-.0986-2.6415c-.0196-.5259-.2929-.8485-.7942-.2943z"/></svg>`
    },
    'default': {
      template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>`
    }
  }
  return icons[categoryName] || icons['default']
}

const loadCategoryArticles = async (category) => {
  loading.value = true
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/blog/articles?category=${encodeURIComponent(category)}`)

    if (response.data?.success) {
      articles.value = response.data.data || []

      // 默认选择第一篇文章
      if (articles.value.length > 0 && !currentArticle.value) {
        await selectArticle(articles.value[0])
      }
    }
  } catch (error) {
    console.error('加载文章失败:', error)
  } finally {
    loading.value = false
  }
}

const selectArticle = async (article) => {
  loading.value = true
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/blog/articles/${encodeURIComponent(article.id)}`)

    if (response.data?.success) {
      currentArticle.value = response.data.data

      // 更新阅读状态
      setReadingStatus(article.id, 'reading')

      // 检查收藏状态
      checkBookmarkStatus()

      // 延迟生成锚点和滚动监听
      await nextTick(() => {
        generateAnchors()
        updateActiveHeading()
      })

      // 更新URL但不导航
      const newUrl = `/blog/reader/${encodeURIComponent(currentCategory.value)}?article=${encodeURIComponent(article.id)}`
      window.history.replaceState(null, '', newUrl)
    }
  } catch (error) {
    console.error('加载文章详情失败:', error)
  } finally {
    loading.value = false
  }
}

const generateAnchors = () => {
  if (!currentArticle.value?.headings) return

  currentArticle.value.headings.forEach(heading => {
    const element = document.getElementById(heading.anchor)
    if (element) {
      element.scrollMarginTop = '80px'
    }
  })
}

const updateActiveHeading = () => {
  if (!currentArticle.value?.headings) return

  const headings = currentArticle.value.headings
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop

  for (let i = headings.length - 1; i >= 0; i--) {
    const heading = headings[i]
    const element = document.getElementById(heading.anchor)
    if (element) {
      const rect = element.getBoundingClientRect()
      if (rect.top <= 100) {
        activeHeading.value = heading.anchor
        return
      }
    }
  }

  if (headings.length > 0) {
    activeHeading.value = headings[0].anchor
  }
}

const updateReadingProgress = () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  const scrollHeight = document.documentElement.scrollHeight - window.innerHeight
  const progress = Math.min((scrollTop / scrollHeight) * 100, 100)

  readingProgress.value = progress

  if (currentArticle.value) {
    readingProgressMap.value[currentArticle.value.id] = progress

    // 如果阅读进度超过90%，标记为已完成
    if (progress > 90) {
      setReadingStatus(currentArticle.value.id, 'completed')
    }
  }
}

const scrollToHeading = (anchor, event) => {
  event.preventDefault()
  const element = document.getElementById(anchor)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    activeHeading.value = anchor
  }
}

const toggleLeftSidebar = () => {
  leftSidebarCollapsed.value = !leftSidebarCollapsed.value
  localStorage.setItem('blog-left-sidebar-collapsed', JSON.stringify(leftSidebarCollapsed.value))
}

const toggleRightSidebar = () => {
  rightSidebarCollapsed.value = !rightSidebarCollapsed.value
  localStorage.setItem('blog-right-sidebar-collapsed', JSON.stringify(rightSidebarCollapsed.value))
}

const toggleBookmark = () => {
  if (!currentArticle.value) return

  const bookmarks = JSON.parse(localStorage.getItem('bookmarked-articles') || '[]')
  const articleId = currentArticle.value.id

  if (isBookmarked.value) {
    const index = bookmarks.indexOf(articleId)
    if (index > -1) {
      bookmarks.splice(index, 1)
    }
  } else {
    bookmarks.push(articleId)
  }

  localStorage.setItem('bookmarked-articles', JSON.stringify(bookmarks))
  isBookmarked.value = !isBookmarked.value
}

const checkBookmarkStatus = () => {
  if (!currentArticle.value) return

  const bookmarks = JSON.parse(localStorage.getItem('bookmarked-articles') || '[]')
  isBookmarked.value = bookmarks.includes(currentArticle.value.id)
}

const shareArticle = () => {
  if (!currentArticle.value) return

  if (navigator.share) {
    navigator.share({
      title: currentArticle.value.title,
      url: window.location.href
    })
  } else {
    navigator.clipboard.writeText(window.location.href).then(() => {
      // 可以添加提示
      console.log('链接已复制到剪贴板')
    })
  }
}

const printArticle = () => {
  window.print()
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY年MM月DD日')
}

const isReading = (articleId) => {
  return readingStatus.value[articleId] === 'reading'
}

const isCompleted = (articleId) => {
  return readingStatus.value[articleId] === 'completed'
}

const getReadingProgress = (articleId) => {
  return readingProgressMap.value[articleId] || 0
}

const setReadingStatus = (articleId, status) => {
  readingStatus.value[articleId] = status
  localStorage.setItem('reading-status', JSON.stringify(readingStatus.value))
}


// 监听滚动事件
const handleScroll = () => {
  updateActiveHeading()
  updateReadingProgress()
}

// 生命周期
onMounted(() => {
  // 恢复侧边栏状态
  const savedLeftCollapsed = localStorage.getItem('blog-left-sidebar-collapsed')
  if (savedLeftCollapsed) {
    leftSidebarCollapsed.value = JSON.parse(savedLeftCollapsed)
  }

  const savedRightCollapsed = localStorage.getItem('blog-right-sidebar-collapsed')
  if (savedRightCollapsed) {
    rightSidebarCollapsed.value = JSON.parse(savedRightCollapsed)
  }

  // 恢复阅读状态
  const savedReadingStatus = localStorage.getItem('reading-status')
  if (savedReadingStatus) {
    readingStatus.value = JSON.parse(savedReadingStatus)
  }

  // 获取分类
  currentCategory.value = route.params.category

  // 加载文章
  loadCategoryArticles(currentCategory.value)

  // 监听滚动
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

// 监听路由变化
watch(() => route.query.article, async (newArticleId) => {
  if (newArticleId && articles.value.length > 0) {
    const article = articles.value.find(a => a.id === newArticleId)
    if (article) {
      await selectArticle(article)
    }
  }
})
</script>

<style scoped>
.blog-reader {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--primary-25) 100%);
}

/* 三栏布局 */
.reader-layout {
  display: flex;
  max-width: 100vw;
  min-height: calc(100vh - 60px);
  transition: all var(--transition-smooth);
}

/* 左侧边栏 */
.left-sidebar {
  width: 320px;
  background: var(--color-bg-primary);
  border-right: 1px solid var(--color-border-primary);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  transition: all var(--transition-smooth);
  z-index: 10;
}

.left-sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  border-bottom: 1px solid var(--color-border-primary);
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--color-bg-primary) 100%);
}

.category-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
  flex: 1;
}

.category-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--primary-600);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.category-icon svg {
  width: 20px;
  height: 20px;
}

.category-details {
  min-width: 0;
  flex: 1;
}

.category-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1) 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.article-count {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.collapse-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-2);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  transition: all var(--transition-normal);
  flex-shrink: 0;
}

.collapse-btn:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.collapse-icon {
  width: 18px;
  height: 18px;
  transition: transform var(--transition-normal);
}

.collapse-icon.rotated {
  transform: rotate(180deg);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* 搜索 */
.search-section {
  flex-shrink: 0;
}

.search-box {
  position: relative;
}

.search-icon {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--color-text-muted);
}

.search-input {
  width: 100%;
  padding: var(--space-3) var(--space-3) var(--space-3) var(--space-10);
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

/* 文章导航 */
.articles-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.article-nav-item {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.article-nav-item:hover {
  background: var(--color-bg-primary);
  border-color: var(--primary-300);
  transform: translateX(4px);
}

.article-nav-item.active {
  background: linear-gradient(135deg, var(--primary-100) 0%, var(--primary-50) 100%);
  border-color: var(--primary-500);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.article-nav-item.reading {
  border-left: 4px solid var(--warning-500);
}

.article-nav-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.article-nav-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-nav-excerpt {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-nav-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-xs);
}

.article-date {
  color: var(--color-text-muted);
}

.article-indicators {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.reading-time {
  color: var(--color-text-muted);
}

.status-icon {
  width: 12px;
  height: 12px;
}

.status-icon.reading {
  color: var(--warning-500);
}

.status-icon.completed {
  color: var(--success-500);
}

.article-nav-tags {
  display: flex;
  gap: var(--space-1);
  flex-wrap: wrap;
}

.article-nav-tag {
  background: var(--color-bg-muted);
  color: var(--color-text-secondary);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: 10px;
  font-weight: var(--font-weight-medium);
}

.reading-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--color-border-primary);
}

.progress-bar {
  height: 100%;
  background: var(--primary-600);
  transition: width var(--transition-normal);
}

/* 折叠状态 */
.sidebar-collapsed-content {
  padding: var(--space-4);
  display: flex;
  justify-content: center;
}

.expand-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  transition: all var(--transition-normal);
}

.expand-btn:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.expand-btn svg {
  width: 20px;
  height: 20px;
}

/* 主内容区 */
.main-content {
  flex: 1;
  min-width: 0;
  background: var(--color-bg-primary);
  transition: all var(--transition-smooth);
}

.reader-layout.sidebar-collapsed .main-content {
  margin-left: 0;
}

.reader-layout.outline-collapsed .main-content {
  margin-right: 0;
}

/* 加载和空状态 */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  color: var(--color-text-secondary);
  text-align: center;
  padding: var(--space-8);
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

.empty-icon {
  width: 64px;
  height: 64px;
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

/* 文章阅读器 */
.article-reader {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--space-8);
}

.article-header {
  margin-bottom: var(--space-8);
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--color-border-primary);
}

.article-meta {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  flex-wrap: wrap;
}

.article-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  line-height: 1.3;
  margin: 0 0 var(--space-6) 0;
}

.article-tags {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  margin-bottom: var(--space-6);
}

.article-tag {
  background: var(--color-bg-muted);
  color: var(--color-text-secondary);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.article-actions {
  display: flex;
  gap: var(--space-3);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-2) var(--space-4);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.action-btn:hover {
  background: var(--primary-50);
  border-color: var(--primary-300);
  color: var(--color-text-primary);
}

.action-btn.active {
  background: var(--primary-600);
  border-color: var(--primary-600);
  color: white;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.article-body {
  margin-bottom: var(--space-8);
  line-height: 1.8;
}

/* Markdown内容样式 */
.markdown-content {
  font-family: var(--font-family-sans);
  line-height: 1.8;
  color: var(--color-text-primary);
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: var(--space-6) 0 var(--space-3) 0;
  line-height: 1.3;
}

.markdown-content :deep(h1) { font-size: var(--font-size-2xl); }
.markdown-content :deep(h2) { font-size: var(--font-size-xl); }
.markdown-content :deep(h3) { font-size: var(--font-size-lg); }

.markdown-content :deep(p) {
  margin: var(--space-4) 0;
}

.markdown-content :deep(code) {
  background: var(--color-bg-muted);
  color: var(--primary-700);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-mono);
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  background: var(--color-bg-muted);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  margin: var(--space-6) 0;
  overflow-x: auto;
  font-family: var(--font-family-mono);
}

.markdown-content :deep(pre code) {
  background: none;
  padding: 0;
  color: var(--color-text-primary);
}

/* 文章导航 */
.article-footer {
  border-top: 1px solid var(--color-border-primary);
  padding-top: var(--space-6);
}

.article-navigation {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  cursor: pointer;
  transition: all var(--transition-normal);
  max-width: 300px;
  flex: 1;
}

.nav-btn:hover {
  background: var(--primary-50);
  border-color: var(--primary-300);
  transform: translateY(-2px);
}

.nav-btn svg {
  width: 20px;
  height: 20px;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.nav-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 0;
}

.nav-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
}

.nav-title {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.nav-next {
  text-align: right;
}

.nav-next .nav-info {
  align-items: flex-end;
}

/* 右侧边栏 */
.right-sidebar {
  width: 280px;
  background: var(--color-bg-primary);
  border-left: 1px solid var(--color-border-primary);
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  transition: all var(--transition-smooth);
}

.right-sidebar.collapsed {
  width: 60px;
}

.outline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  border-bottom: 1px solid var(--color-border-primary);
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--color-bg-primary) 100%);
}

.outline-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.outline-nav {
  padding: var(--space-4);
}

.outline-list {
  list-style: none;
  padding: 0;
  margin: 0;
  margin-bottom: var(--space-6);
}

.outline-item {
  margin: 0;
}

.outline-link {
  display: block;
  padding: var(--space-2) var(--space-3);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  line-height: 1.4;
  transition: all var(--transition-normal);
  border-left: 2px solid transparent;
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}

.outline-link:hover {
  color: var(--primary-600);
  background: var(--primary-50);
}

.outline-item.outline-active .outline-link {
  color: var(--primary-700);
  background: var(--primary-100);
  border-left-color: var(--primary-500);
  font-weight: var(--font-weight-medium);
}

/* 不同级别的缩进 */
.outline-level-1 .outline-link { padding-left: var(--space-3); }
.outline-level-2 .outline-link { padding-left: var(--space-6); }
.outline-level-3 .outline-link { padding-left: var(--space-9); }
.outline-level-4 .outline-link { padding-left: var(--space-12); }

/* 阅读进度 */
.reading-progress-section {
  text-align: center;
  padding: var(--space-4);
  border-top: 1px solid var(--color-border-primary);
}

.progress-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-3);
  font-weight: var(--font-weight-medium);
}

.progress-circle {
  position: relative;
  display: inline-block;
}

.progress-ring {
  transform: rotate(-90deg);
}

.progress-ring-fill {
  transition: stroke-dashoffset 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  color: var(--primary-600);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .right-sidebar {
    position: fixed;
    right: 0;
    top: 0;
    z-index: 1000;
    transform: translateX(100%);
  }

  .right-sidebar:not(.collapsed) {
    transform: translateX(0);
    box-shadow: -4px 0 24px rgba(0, 0, 0, 0.1);
  }
}

@media (max-width: 768px) {
  .reader-layout {
    flex-direction: column;
  }

  .left-sidebar {
    position: static;
    width: 100%;
    height: auto;
    max-height: 300px;
  }

  .left-sidebar.collapsed {
    height: 60px;
    max-height: 60px;
  }

  .main-content {
    order: 2;
  }

  .right-sidebar {
    position: static;
    width: 100%;
    height: auto;
    max-height: 200px;
    order: 3;
  }

  .article-reader {
    padding: var(--space-4);
  }

  .article-title {
    font-size: var(--font-size-2xl);
  }

  .article-navigation {
    flex-direction: column;
  }

  .nav-btn {
    max-width: none;
  }
}

/* 滚动条样式 */
.sidebar-content::-webkit-scrollbar,
.right-sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track,
.right-sidebar::-webkit-scrollbar-track {
  background: var(--color-bg-secondary);
}

.sidebar-content::-webkit-scrollbar-thumb,
.right-sidebar::-webkit-scrollbar-thumb {
  background: var(--color-border-primary);
  border-radius: 3px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover,
.right-sidebar::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-muted);
}
</style>