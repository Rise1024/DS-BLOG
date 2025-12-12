<template>
  <div class="markdown-viewer">
    <div v-html="renderedContent" class="markdown-content"></div>
  </div>
</template>

<script setup>
import { computed, watch, nextTick, onMounted } from 'vue';
import MarkdownIt from 'markdown-it';
import markdownItLinkAttributes from 'markdown-it-link-attributes';

const props = defineProps({
  content: {
    type: String,
    required: true
  }
});

// 初始化 markdown-it 并启用表格支持
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true,
  tables: true  // 显式启用表格支持
}).use(markdownItLinkAttributes, {
  attrs: {
    target: '_blank',
    rel: 'noopener noreferrer'
  }
});

// 自定义 fence 渲染规则以支持 Mermaid
md.renderer.rules.fence = (tokens, idx, options, env, slf) => {
  const token = tokens[idx];
  const info = token.info ? md.utils.unescapeAll(token.info).trim() : '';
  const langName = info ? info.split(/\s+/g)[0] : '';
  
  // 如果是 mermaid 代码块，生成特殊的 div
  if (langName === 'mermaid') {
    const code = token.content.trim();
    return `<div class="mermaid">${code}</div>\n`;
  }
  
  // 其他代码块使用默认渲染
  const langClass = langName ? ` class="language-${md.utils.escapeHtml(langName)}"` : '';
  return `<pre><code${langClass}>${md.utils.escapeHtml(token.content)}</code></pre>\n`;
};

const renderedContent = computed(() => {
  if (!props.content) return '';
  return md.render(props.content);
});

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
      resolve();
    };
    document.head.appendChild(script);
  });
};

// 渲染 Mermaid 图表
const renderMermaid = async () => {
  await loadMermaid();
  await nextTick();
  
  const mermaidElements = document.querySelectorAll('.markdown-viewer .mermaid');
  if (mermaidElements.length > 0) {
    try {
      // 清除已渲染的图表
      mermaidElements.forEach(el => {
        if (el.getAttribute('data-processed')) {
          el.removeAttribute('data-processed');
          const code = el.getAttribute('data-mermaid-code');
          if (code) {
            el.textContent = code;
          }
        } else {
          el.setAttribute('data-mermaid-code', el.textContent);
        }
      });
      
      await window.mermaid.run({
        querySelector: '.markdown-viewer .mermaid'
      });
    } catch (error) {
      console.error('Mermaid 渲染失败:', error);
    }
  }
};

// 监听内容变化，重新渲染 Mermaid
watch(() => props.content, async () => {
  await nextTick();
  renderMermaid();
}, { immediate: false });

// 组件挂载时渲染 Mermaid
onMounted(() => {
  nextTick(() => {
    renderMermaid();
  });
});
</script>

<style scoped>
.markdown-viewer {
  width: 100%;
}

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

@media (max-width: 480px) {
  /* 小屏幕表格横向滚动 */
  .markdown-content :deep(table) {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
    font-size: var(--font-size-xs);
    margin: var(--space-4) 0;
  }

  .markdown-content :deep(th),
  .markdown-content :deep(td) {
    padding: var(--space-1) var(--space-2);
    white-space: nowrap;
    min-width: 80px;
  }
}

/* Mermaid 图表样式 */
.markdown-content :deep(.mermaid) {
  text-align: center;
  margin: var(--space-6) 0;
  background: var(--color-bg-secondary);
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
</style>
