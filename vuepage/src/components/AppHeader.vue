<template>
  <header class="app-header">
    <div class="header-container">
      <!-- Logo区域 -->
      <div class="logo-section">
        <router-link to="/" class="logo-link">
          <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
            <circle cx="12" cy="13" r="3"/>
          </svg>
          <span class="logo-text">Day Day Up</span>
        </router-link>
      </div>

      <!-- 主导航 -->
      <nav class="main-nav">
        <router-link 
          to="/" 
          class="nav-item"
          :class="{ active: $route.path === '/' }"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 11a9 9 0 0 1 9 9"/>
            <path d="M4 4a16 16 0 0 1 16 16"/>
            <circle cx="5" cy="19" r="1"/>
          </svg>
          <span>牛逼的热门</span>
        </router-link>

        <router-link 
          to="/blog" 
          class="nav-item"
          :class="{ active: $route.path.startsWith('/blog') }"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
          <span>牛逼的博客</span>
        </router-link>

        <router-link 
          to="/editor" 
          class="nav-item"
          :class="{ active: $route.path === '/editor' }"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="m18.5 2.5 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          <span>牛逼的Markdown</span>
        </router-link>
      </nav>

      <!-- 搜索区域 -->
      <div class="search-section">
        <div class="search-box">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
          <input 
            v-model="searchQuery"
            @keyup.enter="handleSearch"
            placeholder="搜索文章..."
            class="search-input"
          >
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const searchQuery = ref('');

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // 跳转到博客页面并传递搜索参数
    router.push({
      path: '/blog',
      query: { search: searchQuery.value.trim() }
    });
  }
};
</script>

<style scoped>
.app-header {
  background-color: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-border-primary);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.header-container {
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: 0 var(--space-4);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.logo-section {
  flex-shrink: 0;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  text-decoration: none;
  color: var(--color-text-primary);
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-lg);
  transition: color var(--transition-normal);
}

.logo-link:hover {
  color: var(--primary-600);
}

.logo-icon {
  width: 28px;
  height: 28px;
  color: var(--primary-600);
}

.logo-text {
  white-space: nowrap;
}

.main-nav {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  flex: 1;
  justify-content: center;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-base);
  transition: all var(--transition-normal);
  position: relative;
}

.nav-item:hover {
  color: var(--color-text-primary);
  background-color: var(--color-bg-secondary);
}

.nav-item.active {
  color: var(--primary-600);
  background-color: var(--primary-50);
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background-color: var(--primary-600);
  border-radius: var(--radius-full);
}

.nav-icon {
  width: 20px;
  height: 20px;
}

.search-section {
  flex-shrink: 0;
  min-width: 200px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: var(--space-3);
  width: 18px;
  height: 18px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: var(--space-2) var(--space-2) var(--space-2) var(--space-10);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  background-color: var(--color-bg-secondary);
  font-size: var(--font-size-sm);
  transition: all var(--transition-normal);
}

.search-input:focus {
  background-color: var(--color-bg-primary);
  border-color: var(--color-border-focus);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-input::placeholder {
  color: var(--color-text-muted);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-container {
    padding: 0 var(--space-3);
    height: 56px;
  }

  .logo-text {
    display: none;
  }

  .main-nav {
    gap: var(--space-1);
  }

  .nav-item {
    padding: var(--space-2);
    font-size: var(--font-size-sm);
  }

  .nav-item span {
    display: none;
  }

  .search-section {
    min-width: 120px;
  }

  .search-input {
    font-size: var(--font-size-xs);
  }
}

@media (max-width: 480px) {
  .search-section {
    display: none;
  }
}
</style>
