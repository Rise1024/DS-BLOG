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
          <nav class="articles-nav">
            <div v-if="articles.length === 0 && !loading" class="empty-articles-state" style="padding: 2rem; text-align: center; color: #666;">
              <div class="empty-icon" style="font-size: 3rem; margin-bottom: 1rem;">📂</div>
              <h3>暂无文章</h3>
              <p>该分类下还没有文章内容</p>
            </div>

            <div class="list-view compact-list">
              <div
                v-for="group in groupedArticles"
                :key="group.name"
                class="folder-group"
              >
                <div
                  v-if="!group.isDirectArticles"
                  class="folder-header"
                  :class="{ 'expanded': group.expanded }"
                  @click="toggleFolderGroup(group)"
                >
                  <div class="folder-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                    </svg>
                  </div>
                  <div class="folder-info">
                    <div class="folder-name">{{ group.name }}</div>
                    <div class="folder-count">{{ group.articles.length }} 篇文章</div>
                  </div>
                  <div class="folder-toggle">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M9 18l6-6-6-6"/>
                    </svg>
                  </div>
                </div>

                <div v-if="group.expanded" class="folder-articles" :class="{ 'direct-articles': group.isDirectArticles }">
                  <div
                    v-for="article in group.articles"
                    :key="article.id"
                    class="doc-title"
                    :class="{
                      'active': currentArticle?.id === article.id,
                      'reading': isReading(article.id)
                    }"
                    @click="selectArticle(article)"
                  >
                    <svg class="doc-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14,2 14,8 20,8"/>
                      <line x1="16" y1="13" x2="8" y2="13"/>
                      <line x1="16" y1="17" x2="8" y2="17"/>
                      <polyline points="10,9 9,9 8,9"/>
                    </svg>
                    <span class="doc-text">{{ article.title }}</span>
                  </div>
                </div>
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
import { ref, computed, onMounted, onUnmounted, nextTick, watch, defineComponent, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import axios from 'axios'
import dayjs from 'dayjs'
import Breadcrumb from '@/components/Breadcrumb.vue'

// 递归树节点组件
const TreeNode = defineComponent({
  name: 'TreeNode',
  props: {
    item: Object,
    currentArticle: Object
  },
  emits: ['select-article', 'toggle-folder'],
  setup(props, { emit }) {
    const isReading = (articleId) => {
      const readingStatus = JSON.parse(localStorage.getItem('reading-status') || '{}')
      return readingStatus[articleId] === 'reading'
    }

    const handleSelectArticle = (article) => {
      emit('select-article', article)
    }

    const handleToggleFolder = (folder) => {
      emit('toggle-folder', folder)
    }

    return {
      isReading,
      handleSelectArticle,
      handleToggleFolder
    }
  },
  render() {
    const { item, currentArticle, handleSelectArticle, handleToggleFolder, isReading } = this

    if (item.type === 'folder') {
      return h('div', {
        class: ['tree-folder', { expanded: item.expanded }]
      }, [
        h('div', {
          class: 'tree-folder-header',
          onClick: () => handleToggleFolder(item)
        }, [
          h('svg', {
            class: 'tree-folder-icon',
            viewBox: '0 0 24 24',
            fill: 'none',
            stroke: 'currentColor',
            'stroke-width': '2'
          }, [
            h('path', { d: 'M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z' })
          ]),
          h('span', { class: 'tree-folder-name' }, item.name),
          h('span', { class: 'tree-folder-count' }, `(${item.children?.length || 0})`)
        ]),
        item.expanded && item.children?.length ? h('div', { class: 'tree-children' },
          item.children.map(child =>
            h(TreeNode, {
              key: child.id || child.path,
              item: child,
              currentArticle: currentArticle,
              'onSelect-article': handleSelectArticle,
              'onToggle-folder': handleToggleFolder
            })
          )
        ) : null
      ])
    } else {
      return h('div', {
        class: ['tree-file', {
          'active': currentArticle?.id === item.id,
          'reading': isReading(item.id)
        }],
        onClick: () => handleSelectArticle(item)
      }, [
        h('div', { class: 'tree-file-content' }, [
          h('svg', {
            class: 'tree-file-icon',
            viewBox: '0 0 24 24',
            fill: 'none',
            stroke: 'currentColor',
            'stroke-width': '2'
          }, [
            h('path', { d: 'M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z' })
          ]),
          h('span', { class: 'tree-file-name' }, item.title || item.name)
        ])
      ])
    }
  }
})

const router = useRouter()
const route = useRoute()
const store = useStore()

// 响应式数据
const articles = ref([])
const currentArticle = ref(null)
const currentCategory = ref('')
const loading = ref(false)
const leftSidebarCollapsed = ref(false)
const rightSidebarCollapsed = ref(false)
const activeHeading = ref('')
const readingProgress = ref(0)
const isBookmarked = ref(false)

// 阅读状态
const readingStatus = ref({}) // { articleId: 'reading' | 'completed' }
const readingProgressMap = ref({}) // { articleId: percentage }

const folderExpandState = ref({}) // { folderName: boolean }

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

// 按子目录分组的文章
const groupedArticles = computed(() => {
  const articlesList = articles.value || []
  
  if (!articlesList.length) return []

  // 按子目录分组
  const groups = new Map()
  const articlesWithoutSubcategory = []
  
  articlesList.forEach(article => {
    if (article.subcategory) {
      const folderName = article.subcategory
      
      if (!groups.has(folderName)) {
        groups.set(folderName, {
          name: folderName,
          articles: [],
          expanded: folderExpandState.value[folderName] ?? true
        })
      }
      
      groups.get(folderName).articles.push(article)
    } else {
      // 没有子目录的文章直接添加到列表中
      articlesWithoutSubcategory.push(article)
    }
  })

  // 按文件夹名称排序
  const sortedGroups = Array.from(groups.values()).sort((a, b) => {
    return a.name.localeCompare(b.name)
  })

  // 如果有没有子目录的文章，创建一个特殊的组来显示它们
  if (articlesWithoutSubcategory.length > 0) {
    return [
      ...sortedGroups,
      {
        name: 'articles',
        articles: articlesWithoutSubcategory,
        expanded: true,
        isDirectArticles: true
      }
    ]
  }

  return sortedGroups
})

// 文章树结构 - 基于真实文件路径和子分类
const articleTree = computed(() => {
  if (!articles.value || articles.value.length === 0) {
    return []
  }

  const tree = []
  const folderMap = new Map()

  articles.value.forEach(article => {
    // 直接使用后端返回的 subcategory 字段来判断
    if (!article.subcategory) {
      // 没有子分类，放在根级别
      tree.push({
        ...article,
        type: 'file',
        path: article.path || article.id,
        name: article.title || '未命名文章'
      })
      return
    }

    // 有子分类，创建目录结构
    const folderName = article.subcategory
    const currentPath = folderName

    let folder = tree.find(item => item.type === 'folder' && item.name === folderName)

    if (!folder) {
      folder = {
        type: 'folder',
        name: folderName,
        path: currentPath,
        children: [],
        expanded: folderExpandState.value[currentPath] ?? true
      }
      tree.push(folder)
      folderMap.set(currentPath, folder)
    }

    // 添加文章到对应目录
    folder.children.push({
      ...article,
      type: 'file',
      path: article.path || article.id,
      name: article.title || '未命名文章'
    })
  })

  return tree
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
    'Spring': () => h('svg', {
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', { d: 'M21.8537 1.4158c-.4644-.2122-.8934-.0619-1.133.3608L18.0323 6.3784c-.2396.4227.0159.9668.5107 1.0834l2.4134.5691c.4947.1166.8097-.1543.7901-.6803l-.0986-2.6415c-.0196-.5259-.2929-.8485-.7942-.2943z' })
    ]),
    'default': () => h('svg', {
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2'
    }, [
      h('path', { d: 'M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z' })
    ])
  }
  const iconFunc = icons[categoryName] || icons['default']
  return iconFunc()
}

const loadCategoryArticles = async (category) => {
  loading.value = true
  try {
    const encodedCategory = encodeURIComponent(category)
    const url = `${store.state.serverUrl}/api/v1/blog/articles?category=${encodedCategory}`

    const response = await axios.get(url)

    if (response.data?.success) {
      articles.value = response.data.data || []

      // 后端如果不支持 includeSubcategories 参数，尝试基于文件路径增强数据
      articles.value = articles.value.map(article => {
        if (!article.subcategory && article.file_path) {
          // 从文件路径提取子分类信息
          const pathParts = article.file_path.replace(/.*\/blog\//, '').split('/')
          if (pathParts.length > 2) {
            const subcategory = pathParts[pathParts.length - 2]
            return {
              ...article,
              subcategory: subcategory !== pathParts[0] ? subcategory : null,
              path: pathParts.slice(0, -1).join('/')
            }
          }
        }
        return article
      })

      // 默认选择第一篇文章
      if (articles.value.length > 0 && !currentArticle.value) {
        await selectArticle(articles.value[0])
      }
    } else {
      articles.value = []
    }
  } catch (error) {
    console.error('加载文章失败:', error)
    articles.value = []
  } finally {
    loading.value = false
  }
}

const selectArticle = async (article) => {
  loading.value = true
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/v1/blog/articles/${article.id}`)

    if (response.data?.success) {
      currentArticle.value = response.data.data

      // 更新阅读状态
      setReadingStatus(article.id, 'reading')

      // 检查收藏状态
      checkBookmarkStatus()

      // 更新URL但不导航
      const newUrl = `/blog/reader/${encodeURIComponent(currentCategory.value)}?article=${encodeURIComponent(article.id)}`
      window.history.replaceState(null, '', newUrl)
    }
  } catch (error) {
    console.error('加载文章详情失败:', error)
  } finally {
    loading.value = false
    
    // 等待 loading 状态更新后再处理文章内容
    await nextTick(async () => {
      // 再等待一次确保 DOM 完全更新
      await nextTick(async () => {
        generateAnchors()
        updateActiveHeading()
        // 修正图片路径（添加 serverUrl 前缀）
        fixImagePaths()
        // 渲染 Mermaid 图表
        await renderMermaid()
        // 设置内部文章链接的点击事件
        setupInternalLinks()
        // 图片加载后自动补偿
        document.querySelectorAll('.markdown-content img').forEach(img => {
          img.onload = () => {
            if (window.location.hash) {
              const anchor = window.location.hash.replace('#', '');
              scrollToHeading(anchor, { preventDefault: () => {} });
            }
          };
        });
        // 文章切换后如有hash自动滚动
        if (window.location.hash) {
          const anchor = window.location.hash.replace('#', '');
          scrollToHeading(anchor, { preventDefault: () => {} });
        }
      })
    })
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

const HEADER_OFFSET = 80; // 吸顶header高度

const scrollToHeading = (anchor, event) => {
  if (event && event.preventDefault) event.preventDefault();
  // 更新URL hash（不会刷新页面）
  if (window.location.hash !== '#' + anchor) {
    history.replaceState(null, '', '#' + anchor);
  }
  // 精确滚动
  const element = document.getElementById(anchor);
  if (element) {
    const top = element.getBoundingClientRect().top + window.scrollY - HEADER_OFFSET;
    window.scrollTo({ top, behavior: 'smooth' });
    activeHeading.value = anchor;
  }
};

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

// 加载 Mermaid 库
const loadMermaid = () => {
  return new Promise((resolve) => {
    if (window.mermaid) {
      window.mermaid.initialize({
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose'
      });
      resolve();
      return;
    }
    
    // 检查是否已经在加载中
    if (document.querySelector('script[data-mermaid]')) {
      // 如果正在加载，等待加载完成
      const checkMermaid = () => {
        if (window.mermaid) {
          window.mermaid.initialize({
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'loose'
          });
          resolve();
        } else {
          setTimeout(checkMermaid, 100);
        }
      };
      checkMermaid();
      return;
    }
    
    // 创建 script 标签加载本地文件
    const script = document.createElement('script');
    script.src = '/mermaid.min.js';
    script.setAttribute('data-mermaid', 'true');
    script.onload = () => {
      window.mermaid.initialize({
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose'
      });
      resolve();
    };
    script.onerror = () => {
      console.error('Mermaid 库加载失败');
      resolve(); // 即使失败也 resolve，避免阻塞
    };
    document.head.appendChild(script);
  });
};

// 渲染 Mermaid 图表
const renderMermaid = async () => {
  try {
    await loadMermaid();
    
    // 等待 DOM 更新和 v-html 渲染完成
    await nextTick();
    
    // 轮询等待 markdown-content 元素出现（最多等待 3 秒）
    let markdownContent = null;
    let attempts = 0;
    const maxAttempts = 30; // 30 次 * 100ms = 3 秒
    
    while (!markdownContent && attempts < maxAttempts) {
      markdownContent = document.querySelector('.article-body .markdown-content');
      if (!markdownContent) {
        await new Promise(resolve => setTimeout(resolve, 100));
        attempts++;
      }
    }
    
    if (!markdownContent) {
      console.error('等待超时：未找到 .markdown-content 元素');
      return;
    }
    
    console.log(`✓ 找到 markdown-content 元素 (尝试 ${attempts + 1} 次)`);
    
    // 再等待一小段时间确保 v-html 内容完全渲染
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const mermaidElements = markdownContent.querySelectorAll('.mermaid');
    console.log('找到 Mermaid 元素:', mermaidElements.length);
    
    if (mermaidElements.length > 0) {
      // 清除已渲染的图表（避免重复渲染）
      mermaidElements.forEach((el, index) => {
        // 检查是否已经渲染过（包含 svg 元素）
        if (el.querySelector('svg')) {
          console.log(`图表 ${index + 1} 已经渲染，跳过`);
          return;
        }
        
        // 保存原始代码
        if (!el.getAttribute('data-mermaid-code')) {
          const code = el.textContent.trim();
          console.log(`保存图表 ${index + 1} 原始代码 (前50字符):`, code.substring(0, 50));
          el.setAttribute('data-mermaid-code', code);
        }
      });
      
      console.log('开始渲染 Mermaid 图表...');
      try {
        // 使用 mermaid.init() 方法
        await window.mermaid.init(undefined, markdownContent.querySelectorAll('.mermaid'));
        console.log('✓ Mermaid 图表渲染成功');
      } catch (initError) {
        console.error('mermaid.init() 失败，尝试 mermaid.run():', initError);
        // 如果 init 失败，尝试 run
        await window.mermaid.run({
          nodes: Array.from(mermaidElements)
        });
        console.log('✓ Mermaid 图表渲染成功 (使用 run)');
      }
    } else {
      console.log('未找到 Mermaid 元素');
      console.log('markdown-content HTML 前500字符:', markdownContent.innerHTML.substring(0, 500));
    }
  } catch (error) {
    console.error('Mermaid 渲染失败:', error);
    console.error('错误堆栈:', error.stack);
  }
};

// 设置内部文章链接的点击事件
const setupInternalLinks = () => {
  const links = document.querySelectorAll('.markdown-content .internal-article-link');
  console.log(`找到 ${links.length} 个内部文章链接`);
  
  links.forEach(link => {
    link.addEventListener('click', async (event) => {
      event.preventDefault();
      const articleId = link.getAttribute('data-article-id');
      console.log('点击内部链接，目标文章ID:', articleId);
      
      if (articleId) {
        // 从文章列表中找到对应的文章
        const targetArticle = articles.value.find(article => article.id === articleId);
        
        if (targetArticle) {
          // 使用 selectArticle 加载目标文章
          await selectArticle(targetArticle);
          // 滚动到顶部
          window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
          console.warn('未在当前分类中找到文章:', articleId);
          // 可能需要切换分类，提取分类名
          const parts = articleId.split('/');
          if (parts.length > 1) {
            const category = parts[0];
            console.log('尝试加载分类:', category);
            // 加载该分类的文章
            await loadCategoryArticles(category);
            // 再次查找文章
            const targetArticle = articles.value.find(article => article.id === articleId);
            if (targetArticle) {
              await selectArticle(targetArticle);
              window.scrollTo({ top: 0, behavior: 'smooth' });
            } else {
              console.error('加载分类后仍未找到文章:', articleId);
            }
          }
        }
      }
    });
  });
};

// 修正图片路径，将 /api/ 开头的路径转换为完整URL
const fixImagePaths = () => {
  const images = document.querySelectorAll('.markdown-content img');
  console.log(`修正 ${images.length} 个图片路径`);
  
  images.forEach(img => {
    const src = img.getAttribute('src');
    // 如果是 /api/ 开头的路径，添加 serverUrl 前缀
    if (src && src.startsWith('/api/')) {
      const newSrc = store.state.serverUrl + src;
      img.setAttribute('src', newSrc);
      console.log(`图片路径修正: ${src} -> ${newSrc}`);
    }
  });
};

// 切换文件夹展开状态
const toggleFolderGroup = (group) => {
  group.expanded = !group.expanded
  folderExpandState.value[group.name] = group.expanded

  // 保存折叠状态到本地存储
  localStorage.setItem('blog-folder-expand-state', JSON.stringify(folderExpandState.value))
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

  // 恢复文件夹展开状态
  const savedFolderExpandState = localStorage.getItem('blog-folder-expand-state')
  if (savedFolderExpandState) {
    folderExpandState.value = JSON.parse(savedFolderExpandState)
  }

  // 获取分类 - 确保正确解码中文参数
  currentCategory.value = decodeURIComponent(route.params.category || '')
  console.log('Current category (decoded):', currentCategory.value)

  // 加载文章
  if (currentCategory.value) {
    loadCategoryArticles(currentCategory.value)
  }

  // 监听滚动
  window.addEventListener('scroll', handleScroll)

  // 页面初次加载时，如有hash，自动滚动
  nextTick(() => {
    if (window.location.hash) {
      const anchor = window.location.hash.replace('#', '');
      scrollToHeading(anchor, { preventDefault: () => {} });
    }
    // 图片加载后再补偿
    document.querySelectorAll('.markdown-content img').forEach(img => {
      img.onload = () => {
        if (window.location.hash) {
          const anchor = window.location.hash.replace('#', '');
          scrollToHeading(anchor, { preventDefault: () => {} });
        }
      };
    });
  });
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

// 监听路由变化
watch(() => route.params.category, async (newCategory) => {
  if (newCategory) {
    const decodedCategory = decodeURIComponent(newCategory)
    if (decodedCategory !== currentCategory.value) {
      console.log('Category changed to:', decodedCategory)
      currentCategory.value = decodedCategory
      currentArticle.value = null // 清除当前文章
      await loadCategoryArticles(decodedCategory)
    }
  }
})

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
  background: var(--color-bg-secondary);
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

/* 搜索 - 现代化设计 */
.search-section {
  flex-shrink: 0;
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--primary-25) 100%);
  border-radius: var(--radius-xl);
  padding: var(--space-4);
  border: 1px solid var(--color-border-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.search-box {
  position: relative;
}

.search-icon {
  position: absolute;
  left: var(--space-4);
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: var(--color-text-muted);
  transition: color var(--transition-normal);
  z-index: 2;
}

.search-input {
  width: 100%;
  padding: var(--space-4) var(--space-4) var(--space-4) var(--space-12);
  border: 2px solid var(--color-border-primary);
  border-radius: var(--radius-xl);
  font-size: var(--font-size-sm);
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--color-bg-secondary) 100%);
  transition: all var(--transition-smooth);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.search-input:focus {
  border-color: var(--primary-400);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1), 0 4px 12px rgba(59, 130, 246, 0.15);
  background: var(--color-bg-primary);
  outline: none;
}

.search-input:focus + .search-icon {
  color: var(--primary-600);
}

/* 显示方式切换 - 现代化设计 */
.view-toggle {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-4);
  border-radius: var(--radius-xl);
  background: linear-gradient(135deg, var(--color-bg-secondary) 0%, var(--primary-25) 100%);
  padding: var(--space-2);
  border: 1px solid var(--color-border-primary);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.view-btn {
  flex: 1;
  background: transparent;
  border: none;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-smooth);
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  position: relative;
  overflow: hidden;
}

.view-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, var(--primary-100) 0%, var(--primary-200) 100%);
  opacity: 0;
  transition: opacity var(--transition-normal);
  border-radius: var(--radius-lg);
}

.view-btn:hover {
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--color-bg-primary) 100%);
  color: var(--primary-700);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.1);
}

.view-btn:hover::before {
  opacity: 0.3;
}

.view-btn.active {
  background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-500) 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  transform: translateY(-1px);
}

.view-btn.active::before {
  opacity: 0;
}

.view-btn svg {
  width: 16px;
  height: 16px;
  transition: all var(--transition-normal);
  z-index: 1;
  position: relative;
}

.view-btn:hover svg {
  transform: scale(1.1);
}

.view-btn.active svg {
  transform: scale(1.1);
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}

/* 文章导航 */
.articles-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

/* 目录树视图 - 紧凑列表设计 */
.tree-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: 0;
}

/* 文件夹样式 - 紧凑列表项设计 */
.tree-folder {
  border-radius: var(--radius-md);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-primary);
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.tree-folder:hover {
  background: var(--primary-25);
  border-color: var(--primary-200);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.tree-folder.expanded {
  background: var(--primary-50);
  border-color: var(--primary-300);
  box-shadow: 0 2px 12px rgba(59, 130, 246, 0.15);
}

.tree-folder-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  min-height: 40px;
}

.tree-folder-header:hover {
  background: var(--primary-50);
}

.tree-folder.expanded .tree-folder-header {
  background: var(--primary-100);
  border-bottom: 1px solid var(--color-border-primary);
}

/* 展开/收起指示器 - 简洁设计 */
.tree-folder-header::before {
  content: '';
  width: 0;
  height: 0;
  border-left: 6px solid var(--color-text-secondary);
  border-top: 4px solid transparent;
  border-bottom: 4px solid transparent;
  transition: transform var(--transition-normal);
  flex-shrink: 0;
}

.tree-folder.expanded .tree-folder-header::before {
  transform: rotate(90deg);
  border-left-color: var(--primary-600);
}

.tree-folder-icon {
  width: 16px;
  height: 16px;
  color: var(--primary-600);
  flex-shrink: 0;
}

.tree-folder-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  flex: 1;
}

.tree-folder-count {
  font-size: var(--font-size-xs);
  background: var(--primary-100);
  color: var(--primary-700);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-weight: var(--font-weight-medium);
  min-width: 20px;
  text-align: center;
}

/* 子项容器 - 简洁设计 */
.tree-children {
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border-primary);
  padding: var(--space-1) 0;
  position: relative;
}

.tree-children::before {
  content: '';
  position: absolute;
  left: 16px;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--primary-200);
}

/* 文件项样式 - 简洁列表设计 */
.tree-file {
  transition: all var(--transition-normal);
  position: relative;
}

.tree-file-content {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  margin: 0 var(--space-1);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  border-radius: var(--radius-md);
  background: transparent;
  border: 1px solid transparent;
  min-height: 36px;
}

/* 子文件缩进和连接线 */
.tree-children .tree-file-content {
  margin-left: var(--space-6);
  position: relative;
}

.tree-children .tree-file-content::before {
  content: '';
  position: absolute;
  left: -20px;
  top: 50%;
  width: 12px;
  height: 1px;
  background: var(--primary-300);
  transform: translateY(-50%);
}

.tree-children .tree-file-content::after {
  content: '';
  position: absolute;
  left: -20px;
  top: 0;
  width: 1px;
  height: 50%;
  background: var(--primary-300);
}

.tree-children .tree-file:last-child .tree-file-content::after {
  height: 0;
}

.tree-file-content:hover {
  background: var(--primary-50);
  border-color: var(--primary-200);
  transform: translateX(2px);
}

.tree-file.active .tree-file-content {
  background: var(--primary-100);
  border-color: var(--primary-300);
  border-left: 3px solid var(--primary-600);
  transform: translateX(1px);
}

.tree-file.reading .tree-file-content {
  border-left: 3px solid var(--warning-500);
  background: var(--warning-25);
}

.tree-file.reading.active .tree-file-content {
  background: var(--warning-50);
  border-left: 3px solid var(--warning-600);
}

.tree-file-icon {
  width: 14px;
  height: 14px;
  color: var(--color-text-muted);
  flex-shrink: 0;
  transition: all var(--transition-normal);
}

.tree-file.active .tree-file-icon {
  color: var(--primary-600);
}

.tree-file-name {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-normal);
  flex: 1;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: all var(--transition-normal);
}

.tree-file.active .tree-file-name {
  font-weight: var(--font-weight-semibold);
  color: var(--primary-700);
}

.tree-file:hover .tree-file-name {
  color: var(--primary-600);
}

/* 列表视图 - 按子目录分组 */
.list-view {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.folder-group {
  border-radius: var(--radius-lg);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-primary);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
  overflow: hidden;
  margin-bottom: var(--space-3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.folder-group:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 35px rgba(15, 23, 42, 0.12);
  border-color: var(--primary-200);
}

.folder-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  cursor: pointer;
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border-primary);
  min-height: 60px;
}

.folder-header:hover {
  background: var(--primary-50);
}

.folder-header.expanded {
  background: var(--primary-100);
  border-bottom-color: var(--primary-100);
}

.folder-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: rgba(59, 130, 246, 0.15);
  color: var(--primary-600);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.folder-icon svg {
  width: 18px;
  height: 18px;
}

.folder-info {
  flex: 1;
  min-width: 0;
}

.folder-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.folder-count {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.folder-toggle {
  width: 18px;
  height: 18px;
  color: var(--primary-600);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.folder-header.expanded .folder-toggle {
  transform: rotate(180deg);
}

.folder-articles {
  background: var(--color-bg-primary);
  padding: var(--space-2) var(--space-4) var(--space-4);
}

.folder-articles.direct-articles {
  padding-top: var(--space-3);
}

.doc-title {
  font-size: 15px;
  color: var(--color-text-primary);
  line-height: 1.6;
  cursor: pointer;
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-2);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
  border: 1px solid transparent;
  background: var(--color-bg-secondary);
}

.doc-icon {
  width: 16px;
  height: 16px;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.doc-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.doc-title:hover {
  background: var(--primary-25);
  border-color: var(--primary-200);
  color: var(--primary-700);
}

.doc-title:hover .doc-icon {
  color: var(--primary-600);
}

.doc-title.active {
  background: var(--primary-50);
  border-color: var(--primary-400);
  box-shadow: inset 0 0 0 1px var(--primary-200);
  color: var(--primary-700);
  font-weight: 600;
}

.doc-title.active .doc-icon {
  color: var(--primary-600);
}

.doc-title.reading {
  border-left: 4px solid var(--warning-500);
  background: rgba(251, 191, 36, 0.12);
}

.doc-title.reading .doc-icon {
  color: var(--warning-600);
}

.doc-title.reading.active {
  background: rgba(251, 191, 36, 0.22);
  color: var(--warning-800);
}

.doc-title.reading.active .doc-icon {
  color: var(--warning-700);
}

:global(.dark) .blog-reader {
  background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
}

:global(.dark) .folder-group {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(148, 163, 184, 0.3);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
}

:global(.dark) .folder-group:hover {
  border-color: rgba(147, 197, 253, 0.4);
}

:global(.dark) .folder-header {
  background: rgba(30, 41, 59, 0.85);
  border-bottom-color: rgba(148, 163, 184, 0.2);
}

:global(.dark) .folder-header.expanded {
  background: rgba(59, 130, 246, 0.25);
  border-bottom-color: rgba(147, 197, 253, 0.3);
}

:global(.dark) .folder-header:hover {
  background: rgba(59, 130, 246, 0.2);
}

:global(.dark) .folder-count {
  color: rgba(226, 232, 240, 0.7);
}

:global(.dark) .folder-toggle {
  color: rgba(147, 197, 253, 0.8);
}

:global(.dark) .folder-articles {
  background: rgba(15, 23, 42, 0.7);
}

:global(.dark) .doc-title {
  background: rgba(30, 41, 59, 0.8);
  border-color: transparent;
  color: rgba(226, 232, 240, 0.9);
}

:global(.dark) .doc-title:hover {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.4);
  color: white;
}

:global(.dark) .doc-title.active {
  background: rgba(59, 130, 246, 0.25);
  border-color: rgba(59, 130, 246, 0.5);
  box-shadow: inset 0 0 0 1px rgba(59, 130, 246, 0.3);
  color: white;
}

:global(.dark) .doc-title.reading {
  background: rgba(251, 191, 36, 0.25);
  border-left-color: rgba(251, 191, 36, 0.9);
}

:global(.dark) .doc-title.reading .doc-icon {
  color: rgba(251, 191, 36, 0.9);
}

:global(.dark) .article-meta {
  color: rgba(226, 232, 240, 0.7);
}

:global(.dark) .reading-time {
  background: rgba(30, 41, 59, 0.85);
  color: rgba(191, 219, 254, 0.9);
}

:global(.dark) .sidebar-header,
:global(.dark) .outline-header {
  background: rgba(15, 23, 42, 0.95);
  border-bottom-color: rgba(148, 163, 184, 0.25);
}

/* 根级文件特殊样式 */
.tree-view > .tree-file .tree-file-content {
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-primary);
  margin-bottom: var(--space-1);
}

.tree-view > .tree-file .tree-file-content:hover {
  border-color: var(--primary-300);
  transform: translateX(2px);
}

.tree-view > .tree-file.active .tree-file-content {
  border-color: var(--primary-500);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
}

/* 卡片视图 - 现代化设计（紧凑优化） */
.card-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-3);
  padding: 0;
}

.article-nav-item {
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--primary-25) 100%);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  cursor: pointer;
  transition: all var(--transition-smooth);
  position: relative;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  min-height: 140px;
  max-height: 160px;
}

.article-nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary-500), var(--primary-300));
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.article-nav-item:hover {
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--color-bg-primary) 100%);
  border-color: var(--primary-300);
  transform: translateY(-2px) scale(1.01);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.12);
}

.article-nav-item:hover::before {
  opacity: 1;
}

.article-nav-item.active {
  background: linear-gradient(135deg, var(--primary-100) 0%, var(--primary-50) 100%);
  border-color: var(--primary-400);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.18);
  transform: translateY(-1px);
}

.article-nav-item.active::before {
  opacity: 1;
}

.article-nav-item.reading {
  border-left: 4px solid var(--warning-500);
  background: linear-gradient(135deg, var(--warning-25) 0%, var(--color-bg-primary) 100%);
}

.article-nav-item.reading::before {
  background: linear-gradient(90deg, var(--warning-500), var(--warning-300));
  opacity: 1;
}

.article-nav-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  position: relative;
  z-index: 1;
  height: 100%;
}

.article-nav-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  transition: color var(--transition-normal);
  flex-shrink: 0;
}

.article-nav-item:hover .article-nav-title {
  color: var(--primary-700);
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
  transition: color var(--transition-normal);
  flex: 1;
}

.article-nav-item:hover .article-nav-excerpt {
  color: var(--color-text-primary);
}

.article-nav-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-xs);
  margin-top: auto;
  flex-shrink: 0;
}

.article-date {
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
  background: var(--color-bg-muted);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
}

.article-indicators {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.reading-time {
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
  background: var(--color-bg-secondary);
  color: var(--primary-700);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: 10px;
}

.status-icon {
  width: 14px;
  height: 14px;
  transition: all var(--transition-normal);
}

.status-icon.reading {
  color: var(--warning-500);
  animation: pulse 2s infinite;
}

.status-icon.completed {
  color: var(--success-500);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.article-nav-tags {
  display: flex;
  gap: var(--space-1);
  flex-wrap: wrap;
  margin-top: var(--space-1);
  flex-shrink: 0;
}

.article-nav-tag {
  background: linear-gradient(135deg, var(--primary-100) 0%, var(--primary-200) 100%);
  color: var(--primary-700);
  padding: 2px var(--space-2);
  border-radius: var(--radius-md);
  font-size: 9px;
  font-weight: var(--font-weight-medium);
  border: 1px solid var(--primary-200);
  box-shadow: 0 1px 2px rgba(59, 130, 246, 0.15);
  transition: all var(--transition-normal);
}

.article-nav-tag:hover {
  background: linear-gradient(135deg, var(--primary-200) 0%, var(--primary-300) 100%);
  transform: scale(1.05);
}

.reading-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--color-border-primary);
  border-radius: 0 0 var(--radius-xl) var(--radius-xl);
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-500), var(--primary-300));
  transition: width var(--transition-smooth);
  border-radius: 0 0 var(--radius-xl) var(--radius-xl);
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

/* 内部文章链接样式 */
.markdown-content :deep(.internal-article-link) {
  color: var(--primary-600);
  text-decoration: none;
  border-bottom: 1px solid var(--primary-300);
  transition: all 0.2s ease;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.markdown-content :deep(.internal-article-link:hover) {
  color: var(--primary-700);
  border-bottom-color: var(--primary-500);
  background-color: var(--primary-50);
  padding: 2px 6px;
  margin: -2px -6px;
  border-radius: 4px;
}

.markdown-content :deep(.internal-article-link::before) {
  content: "📄";
  font-size: 0.9em;
}

/* 表格样式 */
.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-6) 0;
  background-color: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-primary);
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border: 1px solid var(--color-border-primary);
  vertical-align: top;
}

.markdown-content :deep(th) {
  background-color: var(--color-bg-secondary);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  border-bottom: 2px solid var(--color-border-primary);
}

.markdown-content :deep(tbody tr:nth-child(even)) {
  background-color: var(--color-bg-muted);
}

.markdown-content :deep(tbody tr:hover) {
  background-color: var(--primary-25);
  transition: background-color var(--transition-normal);
}

.markdown-content :deep(td:first-child),
.markdown-content :deep(th:first-child) {
  border-left: none;
}

.markdown-content :deep(td:last-child),
.markdown-content :deep(th:last-child) {
  border-right: none;
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
  background: var(--color-bg-secondary);
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

/* 响应式设计 - 现代化优化 */
@media (max-width: 1200px) {
  .right-sidebar {
    position: fixed;
    right: 0;
    top: 0;
    z-index: 1000;
    transform: translateX(100%);
    transition: transform var(--transition-smooth);
  }

  .right-sidebar:not(.collapsed) {
    transform: translateX(0);
    box-shadow: -8px 0 32px rgba(0, 0, 0, 0.15);
  }

  .tree-view {
    gap: var(--space-2);
  }

  .card-view {
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: var(--space-2);
  }

  .article-nav-item {
    padding: var(--space-3);
    min-height: 130px;
    max-height: 150px;
  }

  /* 表格响应式优化 */
  .markdown-content :deep(table) {
    font-size: var(--font-size-sm);
  }

  .markdown-content :deep(th),
  .markdown-content :deep(td) {
    padding: var(--space-2) var(--space-3);
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
    max-height: 400px;
    border-right: none;
    border-bottom: 1px solid var(--color-border-primary);
  }

  .left-sidebar.collapsed {
    height: 80px;
    max-height: 80px;
  }

  .sidebar-content {
    padding: var(--space-3);
  }

  .search-section {
    padding: var(--space-3);
  }

  .search-input {
    padding: var(--space-3) var(--space-3) var(--space-3) var(--space-10);
    font-size: var(--font-size-base);
  }

  .view-toggle {
    margin-top: var(--space-3);
    padding: var(--space-1);
  }

  .view-btn {
    padding: var(--space-2) var(--space-3);
    font-size: var(--font-size-xs);
  }

  .main-content {
    order: 2;
  }

  .right-sidebar {
    position: static;
    width: 100%;
    height: auto;
    max-height: 300px;
    order: 3;
    border-left: none;
    border-top: 1px solid var(--color-border-primary);
  }

  .article-reader {
    padding: var(--space-4);
  }

  .article-title {
    font-size: var(--font-size-2xl);
  }

  .article-navigation {
    flex-direction: column;
    gap: var(--space-3);
  }

  .nav-btn {
    max-width: none;
    padding: var(--space-3) var(--space-4);
  }

  /* 移动端卡片优化 */
  .card-view {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: var(--space-2);
  }

  .article-nav-item {
    padding: var(--space-3);
    margin-bottom: 0;
    min-height: 120px;
    max-height: 140px;
  }

  .article-nav-title {
    font-size: var(--font-size-sm);
    -webkit-line-clamp: 2;
  }

  .article-nav-excerpt {
    font-size: var(--font-size-xs);
    -webkit-line-clamp: 2;
  }

  .article-nav-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-1);
  }

  .article-indicators {
    align-self: flex-end;
  }

  /* 移动端目录树优化 */
  .tree-folder-header {
    padding: var(--space-3) var(--space-4);
  }

  .tree-file-content {
    padding: var(--space-2) var(--space-3);
  }

  .tree-children .tree-file-content {
    margin-left: var(--space-6);
  }

  /* 移动端列表视图优化 */
  .folder-header {
    padding: 1px 4px;
    min-height: 16px;
  }

  .folder-name {
    font-size: 9px;
  }

  .folder-count {
    font-size: 6px;
  }

  .article-item {
    padding: 1px 4px;
    min-height: 14px;
  }

  .article-title {
    font-size: 7px;
    line-height: 1.0;
  }
}

@media (max-width: 480px) {
  .left-sidebar {
    max-height: 350px;
  }

  .left-sidebar.collapsed {
    height: 70px;
    max-height: 70px;
  }

  .sidebar-content {
    padding: var(--space-2);
  }

  .search-section {
    padding: var(--space-2);
  }

  .article-reader {
    padding: var(--space-3);
  }

  .article-title {
    font-size: var(--font-size-xl);
  }

  .card-view {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: var(--space-2);
  }

  .article-nav-item {
    padding: var(--space-2);
    min-height: 100px;
    max-height: 120px;
  }

  .article-nav-title {
    font-size: var(--font-size-xs);
  }

  .article-nav-excerpt {
    font-size: 10px;
  }

  .article-nav-tags {
    gap: var(--space-1);
  }

  .article-nav-tag {
    font-size: 8px;
    padding: 1px var(--space-1);
  }

  .tree-folder-header {
    padding: var(--space-2) var(--space-3);
  }

  .tree-file-content {
    padding: var(--space-2);
  }

  .tree-children .tree-file-content {
    margin-left: var(--space-4);
  }

  /* 移动端表格横向滚动 */
  .markdown-content :deep(table) {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
    font-size: var(--font-size-xs);
  }

  .markdown-content :deep(th),
  .markdown-content :deep(td) {
    padding: var(--space-1) var(--space-2);
    white-space: nowrap;
  }
}

/* Mermaid 图表样式 */
.markdown-content :deep(.mermaid) {
  text-align: center;
  margin: var(--space-6) 0;
  background: var(--color-surface-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  border: 1px solid var(--color-border-primary);
  overflow-x: auto;
}

.markdown-content :deep(.mermaid svg) {
  max-width: 100%;
  height: auto;
  display: inline-block;
}

/* 移动端 Mermaid 图表适配 */
@media (max-width: 768px) {
  .markdown-content :deep(.mermaid) {
    padding: var(--space-3);
    margin: var(--space-4) 0;
  }
  
  .markdown-content :deep(.mermaid svg) {
    font-size: 12px;
  }
}

/* 现代化滚动条样式 */
.sidebar-content::-webkit-scrollbar,
.right-sidebar::-webkit-scrollbar {
  width: 8px;
}

.sidebar-content::-webkit-scrollbar-track,
.right-sidebar::-webkit-scrollbar-track {
  background: var(--color-bg-secondary);
  border-radius: 4px;
}

.sidebar-content::-webkit-scrollbar-thumb,
.right-sidebar::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--primary-300) 0%, var(--primary-500) 100%);
  border-radius: 4px;
  transition: all var(--transition-normal);
}

.sidebar-content::-webkit-scrollbar-thumb:hover,
.right-sidebar::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, var(--primary-400) 0%, var(--primary-600) 100%);
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

/* 现代化动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 文章列表动画 */
.article-nav-item {
  animation: fadeInUp 0.3s ease-out;
}

.article-nav-item:nth-child(1) { animation-delay: 0.1s; }
.article-nav-item:nth-child(2) { animation-delay: 0.15s; }
.article-nav-item:nth-child(3) { animation-delay: 0.2s; }
.article-nav-item:nth-child(4) { animation-delay: 0.25s; }
.article-nav-item:nth-child(5) { animation-delay: 0.3s; }

/* 目录树动画 */
.tree-folder {
  animation: slideInLeft 0.4s ease-out;
}

.tree-file {
  animation: fadeInUp 0.3s ease-out;
}

/* 搜索框焦点动画 */
.search-input:focus {
  animation: scaleIn 0.2s ease-out;
}

/* 按钮点击动画 */
.view-btn:active,
.action-btn:active,
.nav-btn:active {
  transform: scale(0.95);
  transition: transform 0.1s ease-out;
}

/* 卡片悬停动画增强 */
.article-nav-item:hover {
  animation: none;
}

.article-nav-item:hover .article-nav-content {
  animation: slideInLeft 0.2s ease-out;
}

/* 加载状态动画 */
.loading-spinner {
  animation: spin 1s linear infinite, pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* 状态指示器动画 */
.status-icon.reading {
  animation: pulse 2s infinite, bounce 1s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-3px); }
  60% { transform: translateY(-2px); }
}

/* 进度条动画 */
.progress-bar {
  animation: progressGlow 2s ease-in-out infinite;
}

@keyframes progressGlow {
  0%, 100% { box-shadow: 0 0 5px rgba(59, 130, 246, 0.3); }
  50% { box-shadow: 0 0 15px rgba(59, 130, 246, 0.6); }
}

/* 标签悬停动画 */
.article-nav-tag:hover {
  animation: bounce 0.3s ease-out;
}

/* 文件夹展开动画 */
.tree-children {
  animation: slideInLeft 0.3s ease-out;
}

/* 侧边栏切换动画 */
.left-sidebar,
.right-sidebar {
  transition: all var(--transition-smooth);
}

/* 文章内容淡入动画 */
.article-reader {
  animation: fadeInUp 0.5s ease-out;
}

/* 空状态动画 */
.empty-state {
  animation: fadeInUp 0.6s ease-out;
}

.empty-icon {
  animation: bounce 2s infinite;
}
</style>