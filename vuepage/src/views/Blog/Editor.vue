<template>
  <div class="editor-container">
    <div class="editor-header">
      <div class="header-content">
        <h1 class="editor-title">{{ isEdit ? '编辑文章' : '写文章' }}</h1>
        <p class="editor-subtitle">{{ isEdit ? '修改你的文章内容' : '创建一篇新的博客文章' }}</p>
      </div>
    </div>

    <div class="editor-main">
      <div class="editor-card card">
        <!-- 文章元数据 -->
        <div class="article-meta-section">
          <div class="meta-row">
            <div class="meta-field">
              <label class="field-label">文章标题</label>
              <input 
                v-model="articleData.title"
                placeholder="请输入文章标题..."
                class="field-input"
              >
            </div>
            
            <div class="meta-field">
              <label class="field-label">分类</label>
              <select v-model="articleData.category_id" class="field-select">
                <option :value="null">选择分类</option>
                <template v-for="cat in flatCategories" :key="cat.id">
                  <option :value="cat.id">
                    {{ cat.displayName }}
                  </option>
                </template>
              </select>
            </div>
          </div>
          
          <div class="meta-row">
            <div class="meta-field">
              <label class="field-label">标签</label>
              <input 
                v-model="tagsInput"
                @keyup.enter="addTag"
                placeholder="输入标签后按回车添加..."
                class="field-input"
              >
              <div v-if="articleData.tags.length" class="tags-list">
                <span 
                  v-for="(tag, index) in articleData.tags" 
                  :key="index"
                  class="tag-item"
                >
                  {{ tag }}
                  <button @click="removeTag(index)" class="tag-remove">×</button>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 编辑器工具栏 -->
        <div class="editor-toolbar">
          <div class="toolbar-group">
            <button @click="insertMarkdown('**', '**')" class="toolbar-btn" title="粗体">
              <strong>B</strong>
            </button>
            <button @click="insertMarkdown('*', '*')" class="toolbar-btn" title="斜体">
              <em>I</em>
            </button>
            <button @click="insertMarkdown('`', '`')" class="toolbar-btn" title="代码">
              <code>&lt;/&gt;</code>
            </button>
          </div>
          
          <div class="toolbar-group">
            <button @click="insertMarkdown('# ', '')" class="toolbar-btn" title="一级标题">
              H1
            </button>
            <button @click="insertMarkdown('## ', '')" class="toolbar-btn" title="二级标题">
              H2
            </button>
            <button @click="insertMarkdown('### ', '')" class="toolbar-btn" title="三级标题">
              H3
            </button>
          </div>
          
          <div class="toolbar-group">
            <button @click="insertMarkdown('[', '](url)')" class="toolbar-btn" title="链接">
              🔗
            </button>
            <button @click="insertMarkdown('![', '](url)')" class="toolbar-btn" title="图片">
              🖼️
            </button>
            <button @click="insertMarkdown('> ', '')" class="toolbar-btn" title="引用">
              💬
            </button>
          </div>
          
          <div class="toolbar-group">
            <button @click="insertMarkdown('- ', '')" class="toolbar-btn" title="无序列表">
              •
            </button>
            <button @click="insertMarkdown('1. ', '')" class="toolbar-btn" title="有序列表">
              1.
            </button>
            <button @click="insertMarkdown('```\n', '\n```')" class="toolbar-btn" title="代码块">
              { }
            </button>
          </div>
        </div>

        <!-- 编辑器主体 -->
        <div class="editor-body">
          <div class="editor-tabs">
            <button 
              @click="activeTab = 'edit'"
              :class="{ active: activeTab === 'edit' }"
              class="tab-btn"
            >
              编辑
            </button>
            <button 
              @click="activeTab = 'preview'"
              :class="{ active: activeTab === 'preview' }"
              class="tab-btn"
            >
              预览
            </button>
          </div>
          
          <div class="editor-content">
            <textarea
              v-if="activeTab === 'edit'"
              v-model="articleData.content"
              placeholder="开始写你的文章..."
              class="editor-textarea"
              @input="handleContentChange"
            ></textarea>
            
            <div v-else class="preview-content">
              <MarkdownViewer :content="articleData.content" />
            </div>
          </div>
        </div>

        <!-- 编辑器操作 -->
        <div class="editor-actions">
          <button @click="saveDraft" :disabled="saving" class="btn btn-secondary">
            <svg v-if="saving" class="btn-icon animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 12a9 9 0 11-6.219-8.56"/>
            </svg>
            <svg v-else class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
              <polyline points="17,21 17,13 7,13 7,21"/>
              <polyline points="7,3 7,8 15,8"/>
            </svg>
            {{ saving ? '保存中...' : '保存草稿' }}
          </button>
          
          <button @click="publishArticle" :disabled="saving || !canPublish" class="btn btn-primary">
            <svg v-if="saving" class="btn-icon animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 12a9 9 0 11-6.219-8.56"/>
            </svg>
            <svg v-else class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
              <polyline points="16,6 12,2 8,6"/>
              <line x1="12" y1="2" x2="12" y2="15"/>
            </svg>
            {{ saving ? '发布中...' : (isEdit ? '更新文章' : '发布文章') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex';
import axios from 'axios';
import MarkdownViewer from '../../components/MarkdownViewer.vue';

const router = useRouter();
const route = useRoute();
const store = useStore();

// 响应式数据
const articleData = ref({
  title: '',
  content: '',
  category_id: null,
  tags: []
});

const tagsInput = ref('');
const activeTab = ref('edit');
const saving = ref(false);
const isEdit = ref(false);
const blogCategories = ref([]);

// 计算属性
const canPublish = computed(() => {
  return articleData.value.title.trim() && articleData.value.content.trim();
});

// 方法
const insertMarkdown = (before, after) => {
  const textarea = document.querySelector('.editor-textarea');
  if (!textarea) return;
  
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const selectedText = articleData.value.content.substring(start, end);
  
  const newText = before + selectedText + after;
  articleData.value.content = 
    articleData.value.content.substring(0, start) + 
    newText + 
    articleData.value.content.substring(end);
  
  // 设置光标位置
  setTimeout(() => {
    textarea.focus();
    textarea.setSelectionRange(start + before.length, start + before.length + selectedText.length);
  }, 0);
};

const addTag = () => {
  const tag = tagsInput.value.trim();
  if (tag && !articleData.value.tags.includes(tag)) {
    articleData.value.tags.push(tag);
    tagsInput.value = '';
  }
};

const removeTag = (index) => {
  articleData.value.tags.splice(index, 1);
};

const handleContentChange = () => {
  // 可以在这里添加自动保存逻辑
};

// 扁平化分类列表（用于下拉选择）
const flatCategories = computed(() => {
  const flatten = (cats, level = 0) => {
    const result = [];
    for (const cat of cats) {
      result.push({
        id: cat.id,
        name: cat.name,
        displayName: '  '.repeat(level) + cat.name
      });
      if (cat.children && cat.children.length > 0) {
        result.push(...flatten(cat.children, level + 1));
      }
    }
    return result;
  };
  return flatten(blogCategories.value);
});

const loadBlogCategories = async () => {
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/v1/admin/blog-categories`, {
      headers: {
        'Authorization': store.state.token
      }
    });
    
    if (response.data?.success) {
      blogCategories.value = response.data.data || [];

      // 如果是新建，并且路由带入了 category_id，则预填
      if (!isEdit.value) {
        const presetCategoryId = route.query.category_id;
        if (presetCategoryId) {
          articleData.value.category_id = parseInt(presetCategoryId);
        }
      }
    }
  } catch (error) {
    console.error('加载博客分类失败:', error);
  }
};

const saveDraft = async () => {
  saving.value = true;
  try {
    const response = await axios.post(`${store.state.serverUrl}/api/v1/admin/articles`, articleData.value, {
      headers: {
        'Authorization': store.state.token
      }
    });
    
    // 获取当前类目ID
    const categoryId = articleData.value.category_id || route.query.category_id || '';
    
    if (response.data?.success) {
      alert('草稿已保存');
      if (!isEdit.value) {
        // 新文章保存后跳转到编辑模式，携带分类参数以便返回时定位
        router.push({
          path: `/admin/articles/edit/${response.data.data.id}`,
          query: categoryId ? { category_id: categoryId } : {}
        });
      }
    } else {
      alert(response.data?.error || '保存失败');
      // 失败时保持在当前页面
    }
  } catch (error) {
    console.error('保存草稿失败:', error);
    alert('保存失败，请重试');
    // 失败时保持在当前页面
  } finally {
    saving.value = false;
  }
};

const publishArticle = async () => {
  if (!canPublish.value) {
    alert('请填写标题和内容');
    return;
  }
  
  saving.value = true;
  try {
    let response;
    if (isEdit.value) {
      response = await axios.put(`${store.state.serverUrl}/api/v1/admin/articles/${articleData.value.id}`, articleData.value, {
        headers: {
          'Authorization': store.state.token
        }
      });
    } else {
      response = await axios.post(`${store.state.serverUrl}/api/v1/admin/articles`, articleData.value, {
        headers: {
          'Authorization': store.state.token
        }
      });
    }
    
    // 获取当前类目ID，优先使用文章的分类ID，其次使用路由中的
    const categoryId = articleData.value.category_id || route.query.category_id || '';
    
    if (response.data?.success) {
      alert(isEdit.value ? '文章已更新' : '文章已发布');
      router.push({
        path: '/admin/articles',
        query: categoryId ? { category_id: categoryId } : {}
      });
    } else {
      alert(response.data?.error || '发布失败');
      // 失败时也跳转回当前类目
      router.push({
        path: '/admin/articles',
        query: categoryId ? { category_id: categoryId } : {}
      });
    }
  } catch (error) {
    console.error('发布文章失败:', error);
    alert('发布失败，请重试');
    // 失败时也跳转回当前类目
    const categoryId = articleData.value.category_id || route.query.category_id || '';
    router.push({
      path: '/admin/articles',
      query: categoryId ? { category_id: categoryId } : {}
    });
  } finally {
    saving.value = false;
  }
};

const loadArticle = async (id) => {
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/v1/admin/articles/${id}`, {
      headers: {
        'Authorization': store.state.token
      }
    });
    
    if (response.data?.success) {
      const data = response.data.data;
      articleData.value = {
        id: data.id,
        title: data.title || '',
        content: data.content || '',
        category_id: data.category_id || null,
        tags: data.tags || []
      };
      
      // 如果路由中没有 category_id，但文章有 category_id，则更新路由
      if (!route.query.category_id && data.category_id) {
        router.replace({
          path: route.path,
          query: { ...route.query, category_id: data.category_id }
        });
      }
    } else {
      console.error('加载文章失败:', response.data?.error);
    }
  } catch (error) {
    console.error('加载文章失败:', error);
  }
};

// 监听路由变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    isEdit.value = true;
    loadArticle(newId);
  } else {
    isEdit.value = false;
    articleData.value = {
      title: '',
      content: '',
      category: '',
      subcategory: '',
      tags: []
    };
  }
}, { immediate: true });

onMounted(() => {
  // 加载博客分类列表
  loadBlogCategories();
});
</script>

<style scoped>
.editor-container {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--gray-50) 100%);
}

.editor-header {
  background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
  color: white;
  padding: var(--space-8) 0;
}

.header-content {
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: 0 var(--space-4);
  text-align: center;
}

.editor-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--space-2);
}

.editor-subtitle {
  font-size: var(--font-size-lg);
  opacity: 0.9;
}

.editor-main {
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: var(--space-8) var(--space-4);
}

.editor-card {
  background-color: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.article-meta-section {
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border-primary);
  background-color: var(--color-bg-secondary);
}

.meta-row {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.meta-row:last-child {
  margin-bottom: 0;
}

.meta-field {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.field-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.field-input,
.field-select {
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-base);
  transition: all var(--transition-normal);
}

.field-input:focus,
.field-select:focus {
  border-color: var(--color-border-focus);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.tags-list {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  margin-top: var(--space-2);
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  background-color: var(--primary-100);
  color: var(--primary-700);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.tag-remove {
  background: none;
  border: none;
  color: var(--primary-700);
  cursor: pointer;
  font-size: var(--font-size-sm);
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color var(--transition-normal);
}

.tag-remove:hover {
  background-color: var(--primary-200);
}

.editor-toolbar {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--color-border-primary);
  background-color: var(--color-bg-secondary);
  flex-wrap: wrap;
}

.toolbar-group {
  display: flex;
  gap: var(--space-1);
  padding-right: var(--space-4);
  border-right: 1px solid var(--color-border-primary);
}

.toolbar-group:last-child {
  border-right: none;
  padding-right: 0;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md);
  background-color: var(--color-bg-primary);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-normal);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.toolbar-btn:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border-color: var(--color-border-secondary);
}

.editor-body {
  display: flex;
  flex-direction: column;
  height: 600px;
  min-height: 0;
}

.editor-tabs {
  display: flex;
  border-bottom: 1px solid var(--color-border-primary);
  background-color: var(--color-bg-secondary);
}

.tab-btn {
  flex: 1;
  padding: var(--space-3) var(--space-4);
  border: none;
  background: none;
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-normal);
  border-bottom: 2px solid transparent;
}

.tab-btn.active {
  color: var(--primary-600);
  border-bottom-color: var(--primary-600);
  background-color: var(--color-bg-primary);
}

.tab-btn:hover:not(.active) {
  color: var(--color-text-primary);
  background-color: var(--color-bg-muted);
}

.editor-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.editor-textarea {
  flex: 1;
  width: 100%;
  padding: var(--space-6);
  border: none;
  outline: none;
  font-family: var(--font-family-mono);
  font-size: var(--font-size-base);
  line-height: 1.6;
  resize: none;
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.preview-content {
  flex: 1;
  padding: var(--space-6);
  overflow-y: auto;
  background-color: var(--color-bg-primary);
  min-height: 0;
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-6);
  border-top: 1px solid var(--color-border-primary);
  background-color: var(--color-bg-secondary);
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .editor-title {
    font-size: var(--font-size-2xl);
  }
  
  .editor-subtitle {
    font-size: var(--font-size-base);
  }
  
  .meta-row {
    flex-direction: column;
    gap: var(--space-3);
  }
  
  .editor-toolbar {
    padding: var(--space-3) var(--space-4);
  }
  
  .toolbar-group {
    padding-right: var(--space-2);
  }
  
  .toolbar-btn {
    width: 28px;
    height: 28px;
    font-size: var(--font-size-xs);
  }
  
  .editor-body {
    height: 500px;
  }
  
  .editor-textarea,
  .preview-content {
    padding: var(--space-4);
  }
  
  .editor-actions {
    flex-direction: column;
    padding: var(--space-4);
  }
}
</style>
