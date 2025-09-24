<script setup>
import { ref } from 'vue'

defineProps({
  msg: String,
})

const count = ref(0)
</script>

<template>
  <div class="hello-world">
    <h1 class="hello-title">{{ msg }}</h1>

    <div class="hello-card card">
      <div class="card-content">
        <button type="button" @click="count++" class="btn btn-primary">
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          计数: {{ count }}
        </button>
        <p class="card-text">
          编辑 <code class="code">components/HelloWorld.vue</code> 来测试热重载
        </p>
      </div>
    </div>

    <div class="links-section">
      <p class="link-item">
        查看
        <a href="https://vuejs.org/guide/quick-start.html#local" target="_blank" class="link">
          create-vue
        </a>
        ，官方 Vue + Vite 启动器
      </p>
      <p class="link-item">
        了解更多关于 Vue IDE 支持的信息，请查看
        <a href="https://vuejs.org/guide/scaling-up/tooling.html#ide-support" target="_blank" class="link">
          Vue 文档扩展指南
        </a>
      </p>
    </div>

    <p class="read-the-docs">
      点击 Vite 和 Vue 徽标了解更多信息
    </p>
  </div>
</template>

<style scoped>
.hello-world {
  text-align: center;
  padding: var(--space-8) var(--space-4);
}

.hello-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-8);
  line-height: var(--line-height-tight);
}

.hello-card {
  max-width: 600px;
  margin: 0 auto var(--space-8) auto;
  padding: var(--space-8);
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-6);
}

.card-text {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin: 0;
}

.code {
  background-color: var(--color-bg-muted);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  color: var(--primary-600);
}

.links-section {
  max-width: 600px;
  margin: 0 auto var(--space-8) auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.link-item {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin: 0;
}

.link {
  color: var(--primary-600);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  transition: color var(--transition-normal);
}

.link:hover {
  color: var(--primary-700);
  text-decoration: underline;
}

.read-the-docs {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hello-title {
    font-size: var(--font-size-2xl);
  }
  
  .hello-card {
    padding: var(--space-6);
    margin: 0 var(--space-4) var(--space-8) var(--space-4);
  }
  
  .card-content {
    gap: var(--space-4);
  }
}
</style>
