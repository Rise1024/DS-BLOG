<template>
  <div class="admin-container">
    <div class="admin-sidebar">
      <div class="sidebar-header">
        <h2>管理后台</h2>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/admin/questions" class="nav-item" active-class="active">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 11l3 3L22 4"/>
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
          </svg>
          <span>题目管理</span>
        </router-link>

        <router-link to="/admin/tags" class="nav-item" active-class="active">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>
            <line x1="7" y1="7" x2="7.01" y2="7"/>
          </svg>
          <span>标签管理</span>
        </router-link>

        <div class="nav-divider"></div>

        <router-link to="/admin/articles" class="nav-item" active-class="active">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <span>文章管理</span>
        </router-link>

        <div class="nav-divider"></div>

        <router-link to="/" class="nav-item">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          <span>返回首页</span>
        </router-link>
      </nav>
    </div>

    <div class="admin-main">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

const router = useRouter();
const store = useStore();

onMounted(() => {
  // 检查管理员权限（由路由守卫处理，这里不需要再检查）
  // 如果到达这里，说明已经通过了路由守卫的验证
  // 确保主题已应用
  if (store.state.theme === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
});
</script>

<style scoped>
.admin-container {
  display: flex;
  min-height: calc(100vh - 64px);
  background: var(--color-bg-primary, #f5f7fa);
}

.admin-sidebar {
  width: 260px;
  background: var(--color-bg-primary, #ffffff);
  border-right: 1px solid var(--color-border-primary, #e5e7eb);
  position: fixed;
  left: 0;
  top: 64px;
  bottom: 0;
  overflow-y: auto;
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid var(--color-border-primary, #e5e7eb);
}

.sidebar-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary, #1f2937);
}

.sidebar-nav {
  padding: 16px 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin-bottom: 4px;
  border-radius: 8px;
  color: var(--color-text-secondary, #6b7280);
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
}

.nav-item:hover {
  background: var(--color-bg-secondary, #f3f4f6);
  color: var(--color-text-primary, #1f2937);
}

.nav-item.active {
  background: var(--primary-50, #eff6ff);
  color: var(--primary-600, #2563eb);
  font-weight: 500;
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-divider {
  height: 1px;
  background: var(--color-border-primary, #e5e7eb);
  margin: 12px 0;
}

.admin-main {
  margin-left: 260px;
  flex: 1;
  padding: 24px;
}

@media (max-width: 768px) {
  .admin-sidebar {
    width: 200px;
    top: 56px;
  }
  
  .admin-main {
    margin-left: 200px;
  }
}
</style>

