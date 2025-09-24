<template>
  <div class="home-container">
    <div class="hero-section">
      <h1 class="hero-title">欢迎使用Markdown转换工具</h1>
      <p class="hero-subtitle">将您的Markdown文档转换为精美的图片，支持多种样式和自定义选项</p>
      
      <nav class="nav-section">
        <router-link to="/editor" class="nav-btn btn btn-primary">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="m18.5 2.5 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          开始创作
        </router-link>
        <router-link to="/" class="nav-btn btn btn-secondary">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 11a9 9 0 0 1 9 9"/>
            <path d="M4 4a16 16 0 0 1 16 16"/>
            <circle cx="5" cy="19" r="1"/>
          </svg>
          RSS订阅
        </router-link>
        <router-link to="/blog" class="nav-btn btn btn-secondary">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
          我的博客
        </router-link>
      </nav>
    </div>
    
    <div class="recent-section" v-if="previewImages.length">
      <div class="section-header">
        <h2 class="section-title">最近生成</h2>
        <p class="section-subtitle">查看您最近创建的Markdown图片</p>
      </div>
      
      <div class="image-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <div 
          v-for="(img, index) in previewImages" 
          :key="index"
          class="image-card card"
          @click="previewImage(img)"
        >
          <div class="image-wrapper">
            <img :src="img + '?t=' + Date.now()" alt="历史图片" class="image-preview">
            <div class="image-overlay">
              <svg class="overlay-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="empty-state" v-else>
      <div class="empty-content">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
          <circle cx="12" cy="13" r="3"/>
        </svg>
        <h3 class="empty-title">还没有生成过图片</h3>
        <p class="empty-subtitle">开始创建您的第一个Markdown图片吧</p>
        <router-link to="/editor" class="btn btn-primary">
          立即开始
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const previewImages = ref([]);

const previewImage = (img) => {
  window.open(img, '_blank');
};
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--gray-50) 100%);
  padding: var(--space-8) 0;
}

.hero-section {
  text-align: center;
  padding: var(--space-16) var(--space-4);
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-4);
  line-height: 1.2;
}

.hero-subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-8);
  line-height: 1.6;
}

.nav-section {
  display: flex;
  gap: var(--space-4);
  justify-content: center;
  flex-wrap: wrap;
}

.nav-btn {
  min-width: 140px;
  height: 48px;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
}

.nav-icon {
  width: 20px;
  height: 20px;
  margin-right: var(--space-2);
}

.recent-section {
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: 0 var(--space-4);
}

.section-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.section-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.section-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.image-grid {
  gap: var(--space-6);
}

.image-card {
  cursor: pointer;
  overflow: hidden;
  transition: all var(--transition-normal);
}

.image-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.image-wrapper {
  position: relative;
  aspect-ratio: 16/9;
  overflow: hidden;
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-normal);
}

.image-card:hover .image-preview {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.image-card:hover .image-overlay {
  opacity: 1;
}

.overlay-icon {
  width: 32px;
  height: 32px;
  color: white;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: var(--space-8) var(--space-4);
}

.empty-content {
  text-align: center;
  max-width: 400px;
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
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-6);
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: var(--font-size-2xl);
  }
  
  .hero-subtitle {
    font-size: var(--font-size-base);
  }
  
  .nav-section {
    flex-direction: column;
    align-items: center;
  }
  
  .nav-btn {
    width: 100%;
    max-width: 280px;
  }
}
</style> 