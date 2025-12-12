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
        <!-- 主题切换开关 -->
        <button @click="toggleTheme" class="theme-toggle" :class="{ 'is-dark': theme === 'dark' }" :title="theme === 'dark' ? '切换到亮色模式' : '切换到暗色模式'">
          <span class="theme-label">{{ theme === 'dark' ? '黑夜' : '白天' }}</span>
          <span class="theme-slider"></span>
        </button>
      </div>

      <!-- 主导航 -->
      <nav class="main-nav">
        <router-link 
          to="/question-bank" 
          class="nav-item"
          :class="{ active: $route.path.startsWith('/question-bank') || $route.path === '/' }"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 11l3 3L22 4"/>
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
          </svg>
          <span>题库</span>
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
          <span>博客</span>
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
            :placeholder="router.currentRoute.value.path.startsWith('/question-bank') || router.currentRoute.value.path === '/' ? '搜索题目...' : '搜索文章...'"
            class="search-input"
          >
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

const router = useRouter();
const store = useStore();
const searchQuery = ref('');

const theme = computed(() => store.state.theme);

const toggleTheme = () => {
  const newTheme = theme.value === 'dark' ? 'light' : 'dark';
  store.commit('setTheme', newTheme);
};

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // 根据当前路由决定跳转到题库搜索还是博客搜索
    if (router.currentRoute.value.path.startsWith('/question-bank') || router.currentRoute.value.path === '/') {
      router.push({
        path: '/question-bank',
        query: { search: searchQuery.value.trim() }
      });
    } else {
    router.push({
      path: '/blog',
      query: { search: searchQuery.value.trim() }
    });
    }
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
  display: flex;
  align-items: center;
  gap: var(--space-4);
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

/* 主题切换开关 */
.theme-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  width: 78px;
  height: 30px;
  padding: 0 12px;
  border: none;
  border-radius: 20px;
  background: var(--primary-600, #2563eb);
  cursor: pointer;
  transition: background 0.2s ease;
}

.theme-toggle:hover {
  background: var(--primary-700, #1d4ed8);
}

.theme-toggle.is-dark {
  background: #1f2937;
}

.theme-label {
  font-size: 12px;
  font-weight: 600;
  color: white;
  white-space: nowrap;
}

.theme-slider {
  width: 18px;
  height: 18px;
  border-radius: 999px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
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
  border-radius: var(--radius-full);
  text-decoration: none;
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-base);
  transition: all var(--transition-normal);
  position: relative;
  background-color: transparent;
}

.nav-item:hover {
  color: var(--color-text-primary);
  background-color: var(--color-bg-secondary);
}

.nav-item.active {
  color: var(--primary-600);
  background-color: rgba(59, 130, 246, 0.15);
  box-shadow: inset 0 0 0 1px rgba(59, 130, 246, 0.2);
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

:global(.dark) .app-header {
  background-color: rgba(2, 6, 23, 0.9);
  border-bottom-color: rgba(15, 23, 42, 0.8);
}

:global(.dark) .nav-item {
  color: rgba(226, 232, 240, 0.7);
  background-color: transparent;
  box-shadow: none;
}

:global(.dark) .nav-item:hover {
  background-color: rgba(59, 130, 246, 0.15);
  color: rgba(255, 255, 255, 0.95);
}

:global(.dark) .nav-item.active {
  color: rgba(255, 255, 255, 0.95);
  background-color: rgba(59, 130, 246, 0.25);
  box-shadow: inset 0 0 0 1px rgba(59, 130, 246, 0.4);
}

:global(.dark) .nav-item.active::after {
  background-color: rgba(147, 197, 253, 0.9);
}

:global(.dark) .search-input {
  background-color: rgba(30, 41, 59, 0.9);
  border-color: rgba(148, 163, 184, 0.3);
  color: rgba(226, 232, 240, 0.95);
}

:global(.dark) .search-input::placeholder {
  color: rgba(148, 163, 184, 0.7);
}

:global(.dark) .search-input:focus {
  background-color: rgba(15, 23, 42, 0.95);
  border-color: rgba(96, 165, 250, 0.6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-container {
    padding: 0 var(--space-3);
    height: 56px;
  }

  .logo-section {
    gap: var(--space-2);
  }

  .logo-text {
    display: none;
  }

  .theme-toggle {
    width: 68px;
    height: 26px;
    padding: 0 10px;
  }

  .theme-label {
    font-size: 11px;
  }

  .theme-slider {
    width: 16px;
    height: 16px;
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
