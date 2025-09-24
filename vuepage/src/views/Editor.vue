<template>
  <div class="markdown-studio">
    <!-- 主要内容区域 -->
    <div class="studio-content">
      <!-- 左侧编辑器 -->
      <div class="editor-panel">
        <!-- 文档管理工具栏 -->
        <div class="editor-toolbar">
          <div class="toolbar-group">
            <button @click="newDocument" class="toolbar-btn" title="新建文档">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
                <circle cx="12" cy="13" r="3"/>
              </svg>
            </button>
            <button @click="showTemplates = true" class="toolbar-btn" title="模板库">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <line x1="9" y1="9" x2="15" y2="9"/>
                <line x1="9" y1="15" x2="15" y2="15"/>
              </svg>
            </button>
          </div>

          <div class="toolbar-group">
            <span class="doc-name">{{ currentDoc.name }}</span>
          </div>

          <div class="toolbar-group">
            <button @click="saveDocument" class="toolbar-btn save-btn" title="保存">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                <polyline points="17,21 17,13 7,13 7,21"/>
                <polyline points="7,3 7,8 15,8"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- 编辑工具 -->
        <div class="editor-tools">
          <div class="format-tools">
            <button @click="insertFormat('**', '**')" class="format-btn" title="粗体">
              <strong>B</strong>
            </button>
            <button @click="insertFormat('*', '*')" class="format-btn" title="斜体">
              <em>I</em>
            </button>
            <button @click="insertFormat('`', '`')" class="format-btn" title="代码">
              <code>&lt;/&gt;</code>
            </button>
            <button @click="insertFormat('\n### ', '')" class="format-btn" title="标题">
              <strong>H</strong>
            </button>
            <button @click="insertFormat('\n- ', '')" class="format-btn" title="列表">
              <span>•</span>
            </button>
            <button @click="insertFormat('\n> ', '')" class="format-btn" title="引用">
              <span>"</span>
            </button>
          </div>

          <div class="word-count">
            <span>{{ markdownContent.length }} 字符</span>
            <span>{{ markdownContent.split('\\n').length }} 行</span>
          </div>
        </div>

        <!-- Markdown编辑器 -->
        <div class="editor-main">
          <textarea
            v-model="markdownContent"
            @input="handleInput"
            @keydown="handleKeyDown"
            placeholder="开始创作您的Markdown文档..."
            class="editor-textarea"
            ref="editorTextarea"
          ></textarea>
        </div>
      </div>

      <!-- 右侧预览/输出区域 -->
      <div class="preview-panel">
        <!-- 右上角控制区 -->
        <div class="preview-controls">
          <!-- 预览选项卡 -->
          <div class="preview-tabs">
            <button
              v-for="format in exportFormats"
              :key="format.id"
              @click="activeFormat = format.id"
              :class="['preview-tab', { active: activeFormat === format.id }]"
            >
              {{ format.name }}
            </button>
          </div>

          <!-- 导出按钮组 -->
          <div class="export-buttons">
            <button
              v-if="activeFormat === 'image'"
              @click="generatePreview"
              :disabled="isProcessing"
              class="export-btn primary"
            >
              <svg v-if="isProcessing" class="btn-icon animate-spin" viewBox="0 0 24 24">
                <path d="M21 12a9 9 0 11-6.219-8.56"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="9" cy="9" r="2"/>
                <path d="M21 15l-3.086-3.086a2 2 0 00-2.828 0L6 21"/>
              </svg>
              {{ isProcessing ? '生成中...' : '生成图片' }}
            </button>
            <button
              v-if="activeFormat === 'html'"
              @click="exportContent"
              :disabled="isExporting"
              class="export-btn primary"
            >
              <svg v-if="isExporting" class="btn-icon animate-spin" viewBox="0 0 24 24">
                <path d="M21 12a9 9 0 11-6.219-8.56"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7,10 12,15 17,10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              {{ isExporting ? '导出中...' : '导出HTML' }}
            </button>
            <button
              v-if="activeFormat === 'wechat'"
              @click="copyToClipboard(wechatPreview)"
              class="export-btn primary"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
              复制内容
            </button>
          </div>
        </div>

        <!-- 进度条 -->
        <div v-if="showProgress" class="progress-container">
          <div class="progress-bar">
            <div :style="{ width: progress + '%' }" class="progress-fill"></div>
          </div>
          <span class="progress-text">{{ progress }}%</span>
        </div>

        <!-- 预览内容 -->
        <div class="preview-content">
          <!-- HTML预览 -->
          <div v-if="activeFormat === 'html'" class="html-preview">
            <div v-html="htmlPreview" class="preview-render"></div>
          </div>

          <!-- 图片预览 -->
          <div v-if="activeFormat === 'image'" class="image-preview-panel">
            <!-- 图片样式设置 -->
            <div class="image-settings">
              <div class="setting-group">
                <label class="setting-label">图片样式</label>
                <select v-model="imageStyle" class="setting-select">
                  <option value="carbon">Carbon 风格</option>
                  <option value="github">GitHub 风格</option>
                  <option value="monokai">Monokai 风格</option>
                  <option value="dracula">Dracula 风格</option>
                  <option value="nord">Nord 风格</option>
                </select>
              </div>

              <div class="setting-group">
                <label class="setting-label">
                  <input type="checkbox" v-model="enableWatermark">
                  启用水印
                </label>
                <input
                  v-if="enableWatermark"
                  v-model="watermarkText"
                  placeholder="水印内容"
                  class="setting-input"
                >
              </div>
            </div>

            <div v-if="previewImages.length === 0" class="empty-preview">
              <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="9" cy="9" r="2"/>
                <path d="M21 15l-3.086-3.086a2 2 0 00-2.828 0L6 21"/>
              </svg>
              <p>点击"生成图片"预览效果</p>
            </div>
            <div v-else class="images-grid">
              <div v-for="(img, index) in previewImages" :key="index" class="image-item">
                <img :src="img + '?t=' + Date.now()" alt="生成图片" @click="previewImage(img)">
                <div class="image-actions">
                  <button @click="downloadImage(img)" class="download-btn">下载</button>
                </div>
              </div>
            </div>
          </div>

          <!-- 微信公众号预览 -->
          <div v-if="activeFormat === 'wechat'" class="wechat-preview">
            <div class="wechat-mockup">
              <div class="wechat-header">
                <span class="wechat-title">微信公众号预览</span>
              </div>
              <div v-html="wechatPreview" class="wechat-content"></div>
            </div>
          </div>
        </div>
      </div>
    </div>


    <!-- 模板选择弹窗 -->
    <div v-if="showTemplates" class="templates-modal">
      <div class="modal-overlay" @click="showTemplates = false"></div>
      <div class="modal-content">
        <h3>选择模板</h3>
        <div class="templates-grid">
          <div
            v-for="template in templates"
            :key="template.id"
            @click="useTemplate(template)"
            class="template-card"
          >
            <div class="template-icon">{{ template.icon }}</div>
            <h4>{{ template.name }}</h4>
            <p>{{ template.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useStore } from 'vuex';
import axios from 'axios';
import MarkdownIt from 'markdown-it';

// 实例化markdown-it
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
});

const store = useStore();

// 核心状态
const activeFormat = ref('html');
const markdownContent = ref('');
const isProcessing = ref(false);
const isExporting = ref(false);
const showProgress = ref(false);
const progress = ref(0);

// UI状态
const showTemplates = ref(false);

// 文档状态
const currentDoc = ref({
  id: Date.now(),
  name: '未命名文档',
  content: '',
  lastModified: new Date()
});

// 预览内容
const htmlPreview = ref('');
const wechatPreview = ref('');
const previewImages = ref([]);

// 设置
const imageStyle = ref('carbon');
const enableWatermark = ref(false);
const watermarkText = ref('');

// 导出格式配置
const exportFormats = ref([
  {
    id: 'html',
    name: 'HTML',
    icon: 'svg', // HTML图标组件
    description: '网页格式'
  },
  {
    id: 'image',
    name: '图片',
    icon: 'svg', // 图片图标组件
    description: '高质量PNG图片'
  },
  {
    id: 'wechat',
    name: '微信公众号',
    icon: 'svg', // 微信图标组件
    description: '公众号排版样式'
  }
]);

// 模板库
const templates = ref([
  {
    id: 'readme',
    name: 'README',
    icon: '📋',
    description: '项目说明文档模板',
    content: `# 项目名称

## 简介
简要描述项目的功能和用途

## 特性
- 特性1
- 特性2
- 特性3

## 安装
\`\`\`bash
npm install
\`\`\`

## 使用方法
\`\`\`javascript
// 代码示例
\`\`\`

## 许可证
MIT License`
  },
  {
    id: 'blog',
    name: '博客文章',
    icon: '📝',
    description: '博客文章模板',
    content: `# 文章标题

> 文章摘要或引言

## 前言
在这里写前言...

## 正文
### 小标题1
内容...

### 小标题2
内容...

## 总结
总结内容...

---
*发表于 ${new Date().toLocaleDateString()}*`
  },
  {
    id: 'tech',
    name: '技术文档',
    icon: '🔧',
    description: '技术文档模板',
    content: `# API 文档

## 概述
API的基本介绍

## 认证
\`\`\`http
Authorization: Bearer YOUR_TOKEN
\`\`\`

## 接口列表

### GET /api/users
获取用户列表

**参数**
| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| page | number | 否 | 页码 |
| size | number | 否 | 每页数量 |

**响应**
\`\`\`json
{
  "code": 200,
  "data": [],
  "message": "success"
}
\`\`\``
  }
]);

// 引用编辑器文本域
const editorTextarea = ref(null);

// 计算属性
const currentFormatConfig = computed(() => {
  return exportFormats.value.find(f => f.id === activeFormat.value);
});

// 监听器
watch(markdownContent, () => {
  // 自动更新HTML预览
  if (activeFormat.value === 'html') {
    updateHtmlPreview();
  }
  // 自动更新微信公众号预览
  if (activeFormat.value === 'wechat') {
    updateWechatPreview();
  }
  // 更新文档
  currentDoc.value.content = markdownContent.value;
  currentDoc.value.lastModified = new Date();
});

// 核心方法
const handleInput = () => {
  // 实时更新预览
  if (activeFormat.value === 'html') {
    updateHtmlPreview();
  }
};

const handleKeyDown = (event) => {
  // 处理快捷键
  if (event.ctrlKey || event.metaKey) {
    if (event.key === 's') {
      event.preventDefault();
      saveDocument();
    }
    if (event.key === 'b') {
      event.preventDefault();
      insertFormat('**', '**');
    }
    if (event.key === 'i') {
      event.preventDefault();
      insertFormat('*', '*');
    }
  }

  // Tab键缩进支持
  if (event.key === 'Tab') {
    event.preventDefault();
    const textarea = event.target;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;

    markdownContent.value = markdownContent.value.substring(0, start) +
                           '  ' +
                           markdownContent.value.substring(end);

    // 恢复光标位置
    setTimeout(() => {
      textarea.selectionStart = textarea.selectionEnd = start + 2;
    });
  }
};

// 文档管理方法
const newDocument = () => {
  if (markdownContent.value && !confirm('确定要创建新文档吗？当前文档未保存的内容将丢失。')) {
    return;
  }

  currentDoc.value = {
    id: Date.now(),
    name: '未命名文档',
    content: '',
    lastModified: new Date()
  };

  markdownContent.value = '';
  htmlPreview.value = '';
  wechatPreview.value = '';
  previewImages.value = [];
};

const saveDocument = () => {
  // 更新文档名称
  if (currentDoc.value.name === '未命名文档' && markdownContent.value) {
    const firstLine = markdownContent.value.split('\\n')[0];
    if (firstLine.startsWith('# ')) {
      currentDoc.value.name = firstLine.substring(2).trim() || '未命名文档';
    }
  }

  currentDoc.value.content = markdownContent.value;
  currentDoc.value.lastModified = new Date();

  console.log('文档已保存:', currentDoc.value.name);
};

// 格式化工具
const insertFormat = (prefix, suffix) => {
  const textarea = editorTextarea.value;
  if (!textarea) return;

  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const selectedText = markdownContent.value.substring(start, end);

  const newText = prefix + selectedText + suffix;

  markdownContent.value = markdownContent.value.substring(0, start) +
                         newText +
                         markdownContent.value.substring(end);

  // 恢复光标位置
  setTimeout(() => {
    const newPos = start + prefix.length + selectedText.length + suffix.length;
    textarea.selectionStart = textarea.selectionEnd = newPos;
    textarea.focus();
  });
};

// 模板使用
const useTemplate = (template) => {
  if (markdownContent.value && !confirm(`确定要使用"${template.name}"模板吗？当前内容将被替换。`)) {
    return;
  }

  markdownContent.value = template.content;
  currentDoc.value.name = template.name;
  showTemplates.value = false;

  // 自动更新预览
  updateHtmlPreview();
  updateWechatPreview();
};

// 预览更新方法
const updateHtmlPreview = () => {
  if (!markdownContent.value.trim()) {
    htmlPreview.value = '<div class="empty-content">开始编写内容来查看预览...</div>';
    return;
  }

  try {
    htmlPreview.value = md.render(markdownContent.value);
  } catch (error) {
    console.error('Markdown渲染失败:', error);
    htmlPreview.value = '<div class="error-content">预览渲染失败</div>';
  }
};

const updateWechatPreview = () => {
  if (!markdownContent.value.trim()) {
    wechatPreview.value = '<div class="empty-content">开始编写内容来查看预览...</div>';
    return;
  }

  try {
    // 微信公众号样式的HTML
    let html = md.render(markdownContent.value);

    // 添加微信特有的样式处理
    html = html
      .replace(/<h1>/g, '<h1 style="font-size: 1.5em; font-weight: bold; margin: 1em 0; color: #333;">')
      .replace(/<h2>/g, '<h2 style="font-size: 1.3em; font-weight: bold; margin: 1em 0; color: #333; border-left: 4px solid #1AAD19; padding-left: 10px;">')
      .replace(/<h3>/g, '<h3 style="font-size: 1.1em; font-weight: bold; margin: 1em 0; color: #333;">')
      .replace(/<p>/g, '<p style="margin: 1em 0; line-height: 1.6; color: #333;">')
      .replace(/<blockquote>/g, '<blockquote style="border-left: 4px solid #ddd; margin: 1em 0; padding-left: 1em; color: #666; font-style: italic; background: #f9f9f9;">')
      .replace(/<code>/g, '<code style="background: #f5f5f5; padding: 2px 4px; border-radius: 3px; font-family: monospace; color: #d14;">')
      .replace(/<pre>/g, '<pre style="background: #f8f8f8; padding: 1em; border-radius: 5px; overflow-x: auto; margin: 1em 0;">');

    wechatPreview.value = html;
  } catch (error) {
    console.error('微信预览渲染失败:', error);
    wechatPreview.value = '<div class="error-content">预览渲染失败</div>';
  }
}

// 导出和生成方法
const generatePreview = async () => {
  if (!markdownContent.value.trim()) {
    alert('请输入内容');
    return;
  }

  try {
    isProcessing.value = true;
    showProgress.value = true;
    await simulateProgress();

    if (activeFormat.value === 'html') {
      updateHtmlPreview();
    } else if (activeFormat.value === 'wechat') {
      updateWechatPreview();
    } else if (activeFormat.value === 'image') {
      await generateImagePreview();
    }
  } catch (error) {
    console.error('生成预览失败:', error);
    alert('生成预览失败');
  } finally {
    isProcessing.value = false;
    showProgress.value = false;
    progress.value = 0;
  }
};

const generateImagePreview = async () => {
  try {
    const response = await axios.post(`${store.state.serverUrl}/preview`, {
      content: markdownContent.value,
      style: imageStyle.value,
      watermark: enableWatermark.value ? watermarkText.value : '',
      user_id: 'anonymous'
    });

    if (response.data?.success) {
      previewImages.value = response.data.images;
    } else {
      throw new Error(response.data?.error || '生成图片失败');
    }
  } catch (error) {
    console.error('生成图片预览失败:', error);
    throw error;
  }
};

const exportContent = async () => {
  if (!markdownContent.value.trim()) {
    alert('请输入内容');
    return;
  }

  try {
    isExporting.value = true;
    showProgress.value = true;
    await simulateProgress();

    switch (activeFormat.value) {
      case 'html':
        await exportAsHtml();
        break;
      case 'image':
        await exportAsImage();
        break;
      case 'wechat':
        await exportAsWechat();
        break;
      default:
        throw new Error('不支持的导出格式');
    }
  } catch (error) {
    console.error('导出失败:', error);
    alert(`导出失败: ${error.message}`);
  } finally {
    isExporting.value = false;
    showProgress.value = false;
    progress.value = 0;
  }
};

const exportAsHtml = async () => {
  const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${currentDoc.value.name}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }
        h1, h2, h3, h4, h5, h6 { margin-top: 2rem; margin-bottom: 1rem; }
        pre { background: #f5f5f5; padding: 1rem; border-radius: 5px; overflow-x: auto; }
        code { background: #f0f0f0; padding: 0.2em 0.4em; border-radius: 3px; }
        blockquote { border-left: 4px solid #ddd; margin: 1rem 0; padding-left: 1rem; color: #666; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 0.5rem; text-align: left; }
        th { background-color: #f5f5f5; }
    </style>
</head>
<body>
    ${htmlPreview.value}
</body>
</html>`;

  const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${currentDoc.value.name}.html`;
  link.click();
  URL.revokeObjectURL(url);
};

const exportAsImage = async () => {
  try {
    const response = await axios.post(`${store.state.serverUrl}/convert`, {
      content: markdownContent.value,
      style: imageStyle.value,
      watermark: enableWatermark.value ? watermarkText.value : '',
      user_id: 'anonymous'
    });

    if (response.data?.success) {
      previewImages.value = response.data.images;
      // 自动下载所有图片
      await downloadAllImages();
    } else {
      throw new Error(response.data?.error || '生成图片失败');
    }
  } catch (error) {
    console.error('导出图片失败:', error);
    throw error;
  }
};

const exportAsWechat = async () => {
  // 复制到剪贴板
  try {
    await navigator.clipboard.writeText(wechatPreview.value);
    alert('微信公众号格式已复制到剪贴板，可直接粘贴到微信公众号编辑器中！');
  } catch (error) {
    console.error('复制到剪贴板失败:', error);
    // 降级方案：下载为HTML文件
    const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${currentDoc.value.name} - 微信公众号版本</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', sans-serif; max-width: 600px; margin: 0 auto; padding: 2rem 1rem; background: #fff; }
    </style>
</head>
<body>
    ${wechatPreview.value}
</body>
</html>`;

    const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${currentDoc.value.name}-微信版.html`;
    link.click();
    URL.revokeObjectURL(url);

    alert('已下载为HTML文件，请在浏览器中打开后复制内容到微信公众号编辑器');
  }
};

// 复制到剪贴板
const copyToClipboard = async (html) => {
  try {
    // 移除HTML标签，只保留文本内容用于复制
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    const textContent = tempDiv.textContent || tempDiv.innerText || '';

    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(textContent);
    } else {
      // 兼容旧浏览器
      const textArea = document.createElement('textarea');
      textArea.value = textContent;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }

    alert('内容已复制到剪贴板');
  } catch (err) {
    console.error('复制失败:', err);
    alert('复制失败，请手动复制内容');
  }
};

// 图片相关方法（保留原有功能）
const previewImage = (img) => {
  window.open(img, '_blank');
};

const downloadImage = async (url) => {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `${currentDoc.value.name}-${Date.now()}.png`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  } catch (error) {
    console.error('下载失败:', error);
    alert('下载失败，请重试');
  }
};

const downloadAllImages = async () => {
  if (previewImages.value.length === 0) {
    alert('没有可下载的图片');
    return;
  }

  try {
    for (let i = 0; i < previewImages.value.length; i++) {
      await downloadImage(previewImages.value[i]);
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    alert(`批量下载完成，共 ${previewImages.value.length} 张图片`);
  } catch (error) {
    console.error('批量下载失败:', error);
    alert('批量下载失败，请重试');
  }
};

// 工具方法
const simulateProgress = () => {
  return new Promise(resolve => {
    progress.value = 0;
    const interval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += 15;
      }
    }, 200);

    setTimeout(() => {
      clearInterval(interval);
      progress.value = 100;
      resolve();
    }, 2000);
  });
};

// 组件挂载时的初始化
onMounted(() => {
  // 检查是否有从RSS传递过来的内容
  if (store.state.tempMarkdownContent) {
    markdownContent.value = store.state.tempMarkdownContent;
    store.commit('clearTempMarkdownContent');
  }

  // 初始化HTML预览
  updateHtmlPreview();
  updateWechatPreview();
});
</script>

<style scoped>
/* 全局容器 */
.markdown-studio {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  display: flex;
  flex-direction: column;
}






.settings-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 0.5rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.settings-btn:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.settings-btn svg {
  width: 20px;
  height: 20px;
}

/* 主要内容区域 */
.studio-content {
  display: flex;
  height: 100vh;
}

/* 左侧编辑器面板 */
.editor-panel {
  width: 50%;
  background: white;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e2e8f0;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toolbar-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 0.25rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.toolbar-btn:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.toolbar-btn.save-btn {
  color: #059669;
}

.toolbar-btn svg {
  width: 16px;
  height: 16px;
}

.doc-name {
  font-weight: 500;
  color: #1e293b;
  font-size: 0.875rem;
}

/* 编辑器主体 */
.editor-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.editor-textarea {
  flex: 1;
  border: none;
  outline: none;
  padding: 1.5rem;
  font-family: 'Fira Code', 'Monaco', 'Menlo', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
  resize: none;
  background: white;
  color: #1e293b;
}

.editor-textarea::placeholder {
  color: #94a3b8;
}

/* 编辑工具栏 */
.editor-tools {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.format-tools {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.format-btn {
  background: none;
  border: none;
  padding: 0.375rem 0.5rem;
  border-radius: 0.25rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 500;
}

.format-btn:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.word-count {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #64748b;
}

.word-count span {
  white-space: nowrap;
}

/* 右侧预览面板 */
.preview-panel {
  width: 50%;
  background: white;
  display: flex;
  flex-direction: column;
}

/* 右上角控制区 */
.preview-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
  gap: 1rem;
  position: relative;
}

.preview-tabs {
  display: flex;
  gap: 0.25rem;
}

.export-buttons {
  display: flex;
  gap: 0.5rem;
}

.export-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.export-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.export-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.export-btn.primary {
  background: var(--primary-600);
  color: white;
  border-color: var(--primary-600);
}

.export-btn.primary:hover {
  background: var(--primary-700);
  border-color: var(--primary-700);
}

.export-btn svg {
  width: 1rem;
  height: 1rem;
}

.progress-container {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 10;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: #f1f5f9;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-600);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.875rem;
  color: #64748b;
  min-width: 3rem;
  text-align: right;
}

/* 动画 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.preview-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  background: none;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
  border-bottom: 2px solid transparent;
}

.preview-tab.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
  background: white;
}

.preview-tab:hover:not(.active) {
  background: #f1f5f9;
  color: #1e293b;
}

/* 预览内容 */
.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.html-preview .preview-render {
  max-width: none;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
  color: #1e293b;
}

.html-preview .preview-render :deep(h1),
.html-preview .preview-render :deep(h2),
.html-preview .preview-render :deep(h3),
.html-preview .preview-render :deep(h4),
.html-preview .preview-render :deep(h5),
.html-preview .preview-render :deep(h6) {
  margin-top: 2rem;
  margin-bottom: 1rem;
  font-weight: 600;
  color: #1e293b;
}

.html-preview .preview-render :deep(h1) { font-size: 2rem; }
.html-preview .preview-render :deep(h2) { font-size: 1.5rem; }
.html-preview .preview-render :deep(h3) { font-size: 1.25rem; }

.html-preview .preview-render :deep(p) {
  margin: 1rem 0;
}

.html-preview .preview-render :deep(pre) {
  background: #f1f5f9;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  font-family: 'Fira Code', monospace;
}

.html-preview .preview-render :deep(code) {
  background: #f1f5f9;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-family: 'Fira Code', monospace;
  font-size: 0.875em;
}

.html-preview .preview-render :deep(blockquote) {
  border-left: 4px solid #3b82f6;
  margin: 1rem 0;
  padding-left: 1rem;
  color: #64748b;
  background: #f8fafc;
  padding: 1rem;
  border-radius: 0 0.5rem 0.5rem 0;
}

/* 图片预览面板 */
.image-preview-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.image-settings {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.setting-group {
  margin-bottom: 1rem;
}

.setting-group:last-child {
  margin-bottom: 0;
}

.setting-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.setting-label input[type="checkbox"] {
  margin-right: 0.5rem;
}

.setting-select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  font-size: 0.875rem;
  color: #374151;
}

.setting-select:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.setting-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #374151;
  margin-top: 0.5rem;
}

.setting-input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.empty-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #64748b;
  text-align: center;
}

.empty-preview .empty-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 1rem;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.image-item {
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  overflow: hidden;
  transition: all 0.2s;
}

.image-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.image-item img {
  width: 100%;
  height: auto;
  cursor: pointer;
  display: block;
}

.image-actions {
  padding: 0.75rem;
  background: #f8fafc;
  display: flex;
  justify-content: center;
}

.download-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.download-btn:hover {
  background: #2563eb;
}

/* 微信公众号预览 */
.wechat-preview {
  display: flex;
  justify-content: center;
  padding: 1rem;
}

.wechat-mockup {
  width: 350px;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.wechat-header {
  background: #1aad19;
  color: white;
  padding: 1rem;
  text-align: center;
  font-weight: 500;
}

.wechat-content {
  padding: 1.5rem;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', sans-serif;
  line-height: 1.6;
  color: #333;
}

/* 导出操作区域 */
.export-actions {
  border-top: 1px solid #e2e8f0;
  padding: 1rem;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #1d4ed8);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: #64748b;
  min-width: 3rem;
  text-align: right;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

.btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  font-size: 0.875rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 模板选择弹窗 */
.templates-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}

.modal-content {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  padding: 2rem;
  max-width: 600px;
  width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}

.modal-content h3 {
  margin: 0 0 1.5rem 0;
  color: #1e293b;
  font-size: 1.25rem;
  font-weight: 600;
  text-align: center;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.template-card {
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #3b82f6;
}

.template-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.template-card h4 {
  margin: 0 0 0.5rem 0;
  color: #1e293b;
  font-weight: 600;
}

.template-card p {
  margin: 0;
  color: #64748b;
  font-size: 0.875rem;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .studio-content {
    flex-direction: column;
    height: auto;
  }

  .editor-panel,
  .preview-panel {
    width: 100%;
  }

  .preview-panel {
    min-height: 400px;
  }

  .preview-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .preview-tabs {
    justify-content: center;
  }

  .export-buttons {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .studio-content {
    height: auto;
  }

  .format-tools {
    flex-wrap: wrap;
  }

  .word-count {
    flex-direction: column;
    gap: 0.25rem;
  }


  .templates-grid {
    grid-template-columns: 1fr;
  }

  .wechat-mockup {
    width: 100%;
    max-width: 350px;
  }
}
</style>