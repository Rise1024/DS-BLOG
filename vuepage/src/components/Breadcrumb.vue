<template>
  <nav class="breadcrumb" aria-label="面包屑导航">
    <ol class="breadcrumb-list">
      <li
        v-for="(item, index) in breadcrumbItems"
        :key="index"
        class="breadcrumb-item"
        :class="{ 'is-active': index === breadcrumbItems.length - 1 }"
      >
        <!-- 首页图标 -->
        <svg
          v-if="index === 0"
          class="breadcrumb-home-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M3 9L12 2L21 9V20A2 2 0 0 1 19 22H5A2 2 0 0 1 3 20V9Z"/>
          <polyline points="9,22 9,12 15,12 15,22"/>
        </svg>

        <!-- 链接或文本 -->
        <router-link
          v-if="item.path && index !== breadcrumbItems.length - 1"
          :to="item.path"
          class="breadcrumb-link"
        >
          {{ item.text }}
        </router-link>

        <span v-else class="breadcrumb-text">
          {{ item.text }}
        </span>

        <!-- 分隔符 -->
        <svg
          v-if="index !== breadcrumbItems.length - 1"
          class="breadcrumb-separator"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M9 18L15 12L9 6"/>
        </svg>
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const breadcrumbItems = computed(() => {
  const items = [
    {
      text: '首页',
      path: '/'
    }
  ]

  // 根据当前路由生成面包屑
  const path = route.path
  const query = route.query
  const params = route.params

  if (path.startsWith('/blog')) {
    items.push({
      text: '博客',
      path: '/blog'
    })

    // 博客阅读器页面
    if (path.startsWith('/blog/reader/')) {
      const categoryName = decodeURIComponent(params.category || '')
      items.push({
        text: categoryName,
        path: null // 当前页面，不可点击
      })

      // 如果有文章ID，添加文章标题
      if (query.article) {
        // 这里可以根据需要添加文章标题
        // 由于需要异步获取，这里暂时用文章ID
        items.push({
          text: '文章详情',
          path: null
        })
      }
    }

    // 博客文章页面
    else if (path.startsWith('/blog/article/')) {
      items.push({
        text: '文章详情',
        path: null
      })
    }

    // 博客编辑器页面
    else if (path.startsWith('/blog/editor')) {
      items.push({
        text: params.id ? '编辑文章' : '新建文章',
        path: null
      })
    }
  }

  // 编辑器页面
  else if (path.startsWith('/editor')) {
    items.push({
      text: 'Markdown 编辑器',
      path: null
    })
  }

  // RSS 面板页面
  else if (path === '/') {
    items[0].text = 'RSS 转换器'
    items[0].path = null
  }

  // 首页
  else if (path === '/home') {
    items.push({
      text: '工具首页',
      path: null
    })
  }

  return items
})
</script>

<style scoped>
.breadcrumb {
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-border-primary);
  padding: var(--space-3) var(--space-6);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px);
  background: rgba(255, 255, 255, 0.95);
}

.breadcrumb-list {
  display: flex;
  align-items: center;
  list-style: none;
  margin: 0;
  padding: 0;
  max-width: var(--container-max-width);
  margin: 0 auto;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.breadcrumb-item.is-active {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.breadcrumb-home-icon {
  width: 16px;
  height: 16px;
  color: var(--color-text-muted);
}

.breadcrumb-link {
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: color var(--transition-normal);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
}

.breadcrumb-link:hover {
  color: var(--primary-600);
  background: var(--primary-50);
}

.breadcrumb-text {
  color: inherit;
}

.breadcrumb-separator {
  width: 16px;
  height: 16px;
  color: var(--color-text-muted);
  margin: 0 var(--space-1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .breadcrumb {
    padding: var(--space-2) var(--space-4);
  }

  .breadcrumb-item {
    font-size: var(--font-size-xs);
  }

  .breadcrumb-home-icon,
  .breadcrumb-separator {
    width: 14px;
    height: 14px;
  }

  /* 在小屏幕上可能需要隐藏中间的面包屑项 */
  .breadcrumb-list {
    flex-wrap: wrap;
    gap: var(--space-1);
  }
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .breadcrumb {
    background: rgba(23, 25, 35, 0.95);
    border-bottom-color: var(--color-border-primary);
  }
}
</style>