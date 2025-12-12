<template>
  <div class="article-container">
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="!article" class="error-state">
      <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="12" cy="12" r="10"/>
        <line x1="15" y1="9" x2="9" y2="15"/>
        <line x1="9" y1="9" x2="15" y2="15"/>
      </svg>
      <h3 class="error-title">文章不存在</h3>
      <p class="error-subtitle">请检查文章链接是否正确</p>
      <router-link to="/blog" class="btn btn-primary">
        返回博客
      </router-link>
    </div>

    <div v-else class="article-layout">
      <!-- 文章内容 -->
      <article class="article-content">
        <!-- 文章头部 -->
        <header class="article-header">
          <div class="article-meta">
            <span class="article-date">{{ formatDate(article.createdAt) }}</span>
            <span class="article-category">{{ article.category }}</span>
            <span v-if="article.updatedAt !== article.createdAt" class="article-updated">
              更新于 {{ formatDate(article.updatedAt) }}
            </span>
          </div>
          
          <h1 class="article-title">{{ article.title }}</h1>
          
          <div v-if="article.tags && article.tags.length" class="article-tags">
            <span 
              v-for="tag in article.tags" 
              :key="tag"
              class="article-tag"
            >
              {{ tag }}
            </span>
          </div>
        </header>

        <!-- 文章正文 -->
        <div class="article-body">
          <div v-html="article.html_content" class="markdown-content"></div>
        </div>

        <!-- 相关题目 -->
        <div v-if="article.related_questions && article.related_questions.length > 0" class="related-questions">
          <h3 class="related-title">相关题目</h3>
          <div class="questions-grid">
            <router-link 
              v-for="question in article.related_questions" 
              :key="question.id"
              :to="`/question-bank/question/${question.id}`"
              class="question-card"
            >
              <div class="question-card-header">
                <span class="question-type">{{ question.type === 'short_answer' ? '简答题' : '编程题' }}</span>
                <span class="difficulty" :class="`difficulty-${question.difficulty}`">
                  {{ '⭐'.repeat(question.difficulty) }}
                </span>
              </div>
              <h4 class="question-card-title">{{ question.title }}</h4>
              <div class="question-card-tags">
                <span v-for="tag in question.tags" :key="tag" class="tag">{{ tag }}</span>
              </div>
            </router-link>
          </div>
        </div>

        <!-- 文章底部 -->
        <footer class="article-footer">
          <div class="article-navigation">
            <button @click="goBack" class="btn btn-ghost">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 12H5"/>
                <path d="M12 19l-7-7 7-7"/>
              </svg>
              返回列表
            </button>
          </div>
        </footer>
      </article>

      <!-- 大纲侧边栏 -->
      <aside class="outline-sidebar" :class="{ 'outline-visible': showOutline }">
        <div class="outline-header">
          <h3 class="outline-title">文章大纲</h3>
          <button @click="toggleOutline" class="outline-toggle">
            <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </button>
        </div>
        
        <nav class="outline-nav">
          <ul class="outline-list">
            <li 
              v-for="heading in article.headings" 
              :key="heading.anchor"
              class="outline-item"
              :class="`outline-level-${heading.level}`"
            >
              <a 
                :href="`#${heading.anchor}`"
                @click="scrollToHeading(heading.anchor, $event)"
                class="outline-link"
                :class="{ 'outline-active': activeHeading === heading.anchor }"
              >
                {{ heading.title }}
              </a>
            </li>
          </ul>
        </nav>
      </aside>
    </div>

    <!-- 大纲切换按钮（移动端） -->
    <button 
      v-if="article && article.headings && article.headings.length > 0"
      @click="toggleOutline"
      class="outline-mobile-toggle"
      :class="{ 'outline-mobile-toggle-active': showOutline }"
    >
      <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M4 6h16M4 12h16M4 18h16"/>
      </svg>
      <span>大纲</span>
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex';
import axios from 'axios';
import dayjs from 'dayjs';

const router = useRouter();
const route = useRoute();
const store = useStore();

const article = ref(null);
const loading = ref(false);
const showOutline = ref(false);
const activeHeading = ref('');

const loadArticle = async (id) => {
  loading.value = true;
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/v1/blog/articles/${id}`);
    
    if (response.data?.success) {
      article.value = response.data.data;
      // 延迟生成锚点，确保DOM已渲染
      nextTick(async () => {
        generateAnchors();
        updateActiveHeading();
        // 渲染Mermaid图表
        await renderMermaid();
      });
    } else {
      console.error('加载文章失败:', response.data?.error);
      article.value = null;
    }
  } catch (error) {
    console.error('加载文章失败:', error);
    article.value = null;
  } finally {
    loading.value = false;
  }
};

const generateAnchors = () => {
  if (!article.value?.headings) return;
  
  // 为每个标题添加锚点
  article.value.headings.forEach(heading => {
    const element = document.getElementById(heading.anchor);
    if (element) {
      element.scrollMarginTop = '80px'; // 为固定头部留出空间
    }
  });
};

const updateActiveHeading = () => {
  if (!article.value?.headings) return;
  
  const headings = article.value.headings;
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  
  for (let i = headings.length - 1; i >= 0; i--) {
    const heading = headings[i];
    const element = document.getElementById(heading.anchor);
    if (element) {
      const rect = element.getBoundingClientRect();
      if (rect.top <= 100) { // 考虑固定头部高度
        activeHeading.value = heading.anchor;
        return;
      }
    }
  }
  
  // 如果没有找到任何标题，设置为第一个
  if (headings.length > 0) {
    activeHeading.value = headings[0].anchor;
  }
};

const scrollToHeading = (anchor, event) => {
  event.preventDefault();
  const element = document.getElementById(anchor);
  if (element) {
    element.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    });
    activeHeading.value = anchor;
  }
};

const toggleOutline = () => {
  showOutline.value = !showOutline.value;
};

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY年MM月DD日');
};

const goBack = () => {
  router.push('/blog');
};

// 监听滚动事件
const handleScroll = () => {
  updateActiveHeading();
};

// 加载Mermaid
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
      resolve();
    };
    document.head.appendChild(script);
  });
};

// 渲染Mermaid图表
const renderMermaid = async () => {
  await loadMermaid();
  await nextTick();
  
  const mermaidElements = document.querySelectorAll('.mermaid');
  if (mermaidElements.length > 0) {
    try {
      await window.mermaid.run({
        querySelector: '.mermaid'
      });
    } catch (error) {
      console.error('Mermaid渲染失败:', error);
    }
  }
};

onMounted(() => {
  const articleId = route.params.id;
  if (articleId) {
    loadArticle(articleId);
  }
  
  // 添加滚动监听
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  // 移除滚动监听
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
.article-container {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--gray-50) 100%);
  position: relative;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: var(--color-text-secondary);
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

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
  padding: var(--space-8);
}

.error-icon {
  width: 64px;
  height: 64px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-4);
}

.error-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.error-subtitle {
  color: var(--color-text-secondary);
  margin-bottom: var(--space-6);
}

.article-layout {
  display: flex;
  max-width: var(--container-max-width);
  margin: 0 auto;
  min-height: calc(100vh - 200px);
}

/* 文章内容区域 */
.article-content {
  flex: 1;
  background-color: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  margin-right: var(--space-6);
}

.article-header {
  padding: var(--space-8) var(--space-8) var(--space-6);
  border-bottom: 1px solid var(--color-border-primary);
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--gray-50) 100%);
}

.article-meta {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  flex-wrap: wrap;
}

.article-category {
  background-color: var(--primary-100);
  color: var(--primary-700);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.article-updated {
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
}

.article-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  line-height: 1.3;
  margin-bottom: var(--space-6);
}

.article-tags {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.article-tag {
  background-color: var(--color-bg-muted);
  color: var(--color-text-secondary);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.article-body {
  padding: var(--space-8);
  line-height: 1.8;
  color: var(--color-text-primary);
}

/* Markdown内容样式 */
.markdown-content {
  font-family: var(--font-family-sans);
  line-height: 1.8;
  color: var(--color-text-primary);
}

/* 标题样式 */
.markdown-content :deep(h1) {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: var(--space-8) 0 var(--space-4) 0;
  padding-bottom: var(--space-2);
  border-bottom: 2px solid var(--color-border-primary);
}

.markdown-content :deep(h2) {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: var(--space-6) 0 var(--space-3) 0;
  padding-bottom: var(--space-1);
  border-bottom: 1px solid var(--color-border-primary);
}

.markdown-content :deep(h3) {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: var(--space-5) 0 var(--space-2) 0;
}

.markdown-content :deep(h4) {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: var(--space-4) 0 var(--space-2) 0;
}

.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: var(--space-3) 0 var(--space-1) 0;
}

/* 段落样式 */
.markdown-content :deep(p) {
  margin: var(--space-4) 0;
  line-height: 1.8;
}

/* 链接样式 */
.markdown-content :deep(a) {
  color: var(--primary-600);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: all var(--transition-normal);
}

.markdown-content :deep(a:hover) {
  color: var(--primary-700);
  border-bottom-color: var(--primary-300);
}

/* 列表样式 */
.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: var(--space-4) 0;
  padding-left: var(--space-6);
}

.markdown-content :deep(li) {
  margin: var(--space-2) 0;
  line-height: 1.7;
}

.markdown-content :deep(ul li) {
  list-style-type: disc;
}

.markdown-content :deep(ol li) {
  list-style-type: decimal;
}

/* 引用样式 */
.markdown-content :deep(blockquote) {
  margin: var(--space-4) 0;
  padding: var(--space-4) var(--space-6);
  background-color: var(--color-bg-secondary);
  border-left: 4px solid var(--primary-500);
  border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
  font-style: italic;
  color: var(--color-text-secondary);
}

.markdown-content :deep(blockquote p) {
  margin: 0;
}

/* 代码样式 */
.markdown-content :deep(code) {
  background-color: var(--color-bg-muted);
  color: var(--primary-700);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-mono);
  font-size: 0.9em;
  font-weight: var(--font-weight-medium);
}

.markdown-content :deep(pre) {
  background-color: var(--color-bg-muted);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  margin: var(--space-6) 0;
  overflow-x: auto;
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  line-height: 1.6;
}

.markdown-content :deep(pre code) {
  background: none;
  padding: 0;
  border-radius: 0;
  color: var(--color-text-primary);
  font-weight: normal;
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
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border-bottom: 1px solid var(--color-border-primary);
}

.markdown-content :deep(th) {
  background-color: var(--color-bg-secondary);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.markdown-content :deep(tr:hover) {
  background-color: var(--color-bg-secondary);
}

/* 分割线样式 */
.markdown-content :deep(hr) {
  border: none;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--color-border-primary), transparent);
  margin: var(--space-8) 0;
}

/* 图片样式 */
.markdown-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  margin: var(--space-4) 0;
  transition: transform var(--transition-normal);
}

.markdown-content :deep(img:hover) {
  transform: scale(1.02);
}

/* 强调样式 */
.markdown-content :deep(strong) {
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.markdown-content :deep(em) {
  font-style: italic;
  color: var(--color-text-secondary);
}

/* 删除线样式 */
.markdown-content :deep(del) {
  text-decoration: line-through;
  color: var(--color-text-muted);
}

/* 标记样式 */
.markdown-content :deep(mark) {
  background-color: var(--warning-50);
  color: var(--color-text-primary);
  padding: var(--space-1) var(--space-1);
  border-radius: var(--radius-sm);
}

/* 任务列表样式 */
.markdown-content :deep(input[type="checkbox"]) {
  margin-right: var(--space-2);
  transform: scale(1.2);
}

.markdown-content :deep(li:has(input[type="checkbox"])) {
  list-style: none;
  margin-left: calc(-1 * var(--space-6));
}

/* 响应式设计 */
@media (max-width: 768px) {
  .markdown-content :deep(h1) {
    font-size: var(--font-size-2xl);
  }
  
  .markdown-content :deep(h2) {
    font-size: var(--font-size-xl);
  }
  
  .markdown-content :deep(h3) {
    font-size: var(--font-size-lg);
  }
  
  .markdown-content :deep(pre) {
    padding: var(--space-4);
    font-size: var(--font-size-xs);
  }
  
  .markdown-content :deep(table) {
    font-size: var(--font-size-sm);
  }
  
  .markdown-content :deep(th),
  .markdown-content :deep(td) {
    padding: var(--space-2) var(--space-3);
  }
}

.article-footer {
  padding: var(--space-6) var(--space-8);
  border-top: 1px solid var(--color-border-primary);
  background-color: var(--color-bg-secondary);
}

.article-navigation {
  display: flex;
  justify-content: center;
}

/* 大纲侧边栏 */
.outline-sidebar {
  width: 280px;
  background-color: var(--color-bg-primary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 100px;
  height: fit-content;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
  transition: all var(--transition-normal);
}

.outline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-4) var(--space-2);
  border-bottom: 1px solid var(--color-border-primary);
}

.outline-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.outline-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-2);
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  transition: all var(--transition-normal);
}

.outline-toggle:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.toggle-icon {
  width: 16px;
  height: 16px;
}

.outline-nav {
  padding: var(--space-2) 0;
}

.outline-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.outline-item {
  margin: 0;
}

.outline-link {
  display: block;
  padding: var(--space-2) var(--space-4);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  line-height: 1.4;
  transition: all var(--transition-normal);
  border-left: 2px solid transparent;
}

.outline-link:hover {
  color: var(--primary-600);
  background-color: var(--primary-50);
}

.outline-link.outline-active {
  color: var(--primary-700);
  background-color: var(--primary-100);
  border-left-color: var(--primary-500);
  font-weight: var(--font-weight-medium);
}

/* 不同级别的标题缩进 */
.outline-level-1 .outline-link {
  padding-left: var(--space-4);
  font-weight: var(--font-weight-medium);
}

.outline-level-2 .outline-link {
  padding-left: var(--space-6);
}

.outline-level-3 .outline-link {
  padding-left: var(--space-8);
}

.outline-level-4 .outline-link {
  padding-left: var(--space-10);
}

.outline-level-5 .outline-link {
  padding-left: var(--space-12);
}

.outline-level-6 .outline-link {
  padding-left: var(--space-14);
}

/* 移动端大纲切换按钮 */
.outline-mobile-toggle {
  position: fixed;
  bottom: var(--space-6);
  right: var(--space-6);
  background-color: var(--primary-600);
  color: white;
  border: none;
  border-radius: var(--radius-full);
  padding: var(--space-3) var(--space-4);
  box-shadow: var(--shadow-lg);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-normal);
  z-index: var(--z-sticky);
}

.outline-mobile-toggle:hover {
  background-color: var(--primary-700);
  transform: translateY(-2px);
}

.outline-mobile-toggle-active {
  background-color: var(--primary-800);
}

.outline-mobile-toggle .toggle-icon {
  width: 18px;
  height: 18px;
}

/* Mermaid图表样式 */
.mermaid {
  text-align: center;
  margin: var(--space-6) 0;
  background: var(--surface-50);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  border: 1px solid var(--border-200);
}

.mermaid svg {
  max-width: 100%;
  height: auto;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .article-layout {
    flex-direction: column;
  }
  
  .article-content {
    margin-right: 0;
    margin-bottom: var(--space-6);
  }
  
  .outline-sidebar {
    position: static;
    max-height: 400px;
  }
  
  .outline-toggle {
    display: block;
  }
  
  .outline-sidebar:not(.outline-visible) {
    display: none;
  }
}

@media (max-width: 768px) {
  .article-content {
    margin: var(--space-4);
    border-radius: var(--radius-lg);
  }
  
  .article-header {
    padding: var(--space-6) var(--space-6) var(--space-4);
  }
  
  .article-title {
    font-size: var(--font-size-2xl);
  }
  
  .article-body {
    padding: var(--space-6);
  }
  
  .article-footer {
    padding: var(--space-4) var(--space-6);
  }
  
  .outline-mobile-toggle {
    bottom: var(--space-4);
    right: var(--space-4);
  }
}

@media (max-width: 480px) {
  .outline-mobile-toggle span {
    display: none;
  }
  
  .outline-mobile-toggle {
    padding: var(--space-3);
  }
}

/* 相关题目样式 */
.related-questions {
  margin-top: var(--space-8);
  padding-top: var(--space-8);
  border-top: 2px solid var(--color-border-primary);
}

.related-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-6) 0;
}

.questions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-4);
}

.question-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  text-decoration: none;
  color: inherit;
  transition: all var(--transition-normal);
  display: block;
}

.question-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary-300);
  background: var(--primary-50);
}

.question-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.question-type {
  background: var(--primary-100);
  color: var(--primary-700);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.difficulty {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.question-card-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-3) 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.question-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.tag {
  background: var(--color-bg-muted);
  color: var(--color-text-secondary);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
}

@media (max-width: 768px) {
  .questions-grid {
    grid-template-columns: 1fr;
  }
}
</style>