<template>
  <div id="app">
    <AppHeader />
    <main class="app-main">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
import AppHeader from './components/AppHeader.vue';
</script>

<style>
#app {
  min-height: 100vh;
  font-family: var(--font-family-sans);
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
  display: flex;
  flex-direction: column;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--color-bg-muted);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb {
  background: var(--color-border-secondary);
  border-radius: var(--radius-full);
  transition: background var(--transition-normal);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-border-primary);
}

/* 全局选择文本样式 */
::selection {
  background-color: var(--primary-200);
  color: var(--color-text-primary);
}

::-moz-selection {
  background-color: var(--primary-200);
  color: var(--color-text-primary);
}

/* 全局焦点样式 */
*:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

/* 全局链接样式 */
a {
  color: var(--primary-600);
  text-decoration: none;
  transition: color var(--transition-normal);
}

a:hover {
  color: var(--primary-700);
}

/* 全局图片样式 */
img {
  max-width: 100%;
  height: auto;
}

/* 全局代码样式 */
code {
  font-family: var(--font-family-mono);
  background-color: var(--color-bg-muted);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
}

pre {
  background-color: var(--color-bg-muted);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  overflow-x: auto;
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  line-height: var(--line-height-relaxed);
}

pre code {
  background: none;
  padding: 0;
  border-radius: 0;
}
</style>