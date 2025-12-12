<template>
  <div class="question-editor">
    <div class="editor-header">
      <div>
        <h1 class="page-title">{{ isEdit ? '编辑题目' : '新建题目' }}</h1>
        <p class="page-subtitle">{{ isEdit ? '修改题目内容' : '创建一道新的题目' }}</p>
      </div>
      <div class="header-actions">
        <button @click="goBack" class="btn btn-secondary">
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="19" y1="12" x2="5" y2="12"/>
            <polyline points="12 19 5 12 12 5"/>
          </svg>
          返回
        </button>
        <button @click="saveQuestion" class="btn btn-primary" :disabled="saving || !canSave">
          <svg v-if="!saving" class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
            <polyline points="17 21 17 13 7 13 7 21"/>
            <polyline points="7 3 7 8 15 8"/>
          </svg>
          <div v-else class="spinner-small"></div>
          {{ saving ? '保存中...' : (isEdit ? '更新题目' : '创建题目') }}
        </button>
      </div>
    </div>

    <div class="editor-content">
      <!-- 基本信息 -->
      <div class="section-card">
        <h3 class="section-title">基本信息</h3>
        
        <div class="form-row">
          <div class="form-group">
            <label class="form-label required">题目标题</label>
            <input
              v-model="questionData.title"
              type="text"
              class="form-input"
              placeholder="请输入题目标题..."
              maxlength="500"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label required">所属分类</label>
            <select v-model="questionData.category_id" class="form-select">
              <option value="">请选择分类</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.parent_name ? `${cat.parent_name} > ` : '' }}{{ cat.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">题目类型</label>
            <div class="radio-group">
              <label class="radio-label">
                <input v-model="questionData.type" type="radio" value="short_answer" />
                <span>简答题</span>
              </label>
              <label class="radio-label">
                <input v-model="questionData.type" type="radio" value="programming" />
                <span>编程题</span>
              </label>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label required">难度等级</label>
            <div class="difficulty-selector">
              <button
                v-for="level in 5"
                :key="level"
                @click="questionData.difficulty = level"
                :class="['difficulty-btn', { active: questionData.difficulty === level }]"
                type="button"
              >
                {{ '⭐'.repeat(level) }}
              </button>
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">标签</label>
            <div class="tags-input-wrapper">
              <div class="tags-list">
                <span v-for="(tag, index) in questionData.tags" :key="index" class="tag-item">
                  {{ tag }}
                  <button @click="removeTag(index)" class="tag-remove" type="button">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="18" y1="6" x2="6" y2="18"/>
                      <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                  </button>
                </span>
              </div>
              <input
                v-model="newTag"
                @keyup.enter="addTag"
                type="text"
                class="tag-input"
                placeholder="输入标签后按回车添加..."
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">关联文章</label>
            <p class="form-hint">可选择多个博客文章，题目详情页将提供跳转</p>
            
            <div class="selected-articles" v-if="selectedArticles.length">
              <div
                v-for="article in selectedArticles"
                :key="article.id"
                class="selected-article-chip"
              >
                <span class="chip-title">{{ article.title }}</span>
                <span class="chip-meta">
                  {{ article.category || '未分类' }}
                  <template v-if="article.subcategory"> / {{ article.subcategory }}</template>
                </span>
                <button class="chip-remove" @click="removeSelectedArticle(article.id)" type="button" title="移除关联">
                  ×
                </button>
              </div>
            </div>
            <div class="article-search-bar">
              <input
                v-model="articleSearch"
                type="text"
                class="form-input"
                placeholder="输入关键字后按回车或点击搜索"
                @keyup.enter="loadArticleOptions"
              />
              <button class="btn btn-secondary" type="button" @click="loadArticleOptions" :disabled="optionsLoading">
                {{ optionsLoading ? '搜索中...' : '搜索文章' }}
              </button>
            </div>
            <div class="article-options-panel">
              <div v-if="optionsLoading" class="article-options-loading">
                <div class="spinner-small"></div>
                <span>加载文章列表...</span>
              </div>
              <div v-else class="article-options-list">
                <div
                  v-for="article in articleOptions"
                  :key="article.id"
                  class="article-option-item"
                  :class="{ selected: questionData.related_article_ids.includes(article.id) }"
                  @click="toggleArticleSelection(article)"
                >
                  <div class="article-option-header">
                    <div class="article-option-title">{{ article.title }}</div>
                    <input
                      type="checkbox"
                      :checked="questionData.related_article_ids.includes(article.id)"
                      @click.stop.prevent="toggleArticleSelection(article)"
                    />
                  </div>
                  <div class="article-option-meta">
                    {{ article.category || '未分类' }}
                    <template v-if="article.subcategory"> / {{ article.subcategory }}</template>
                    <span class="option-id">ID: {{ article.id }}</span>
                  </div>
                </div>
                <div v-if="!articleOptions.length" class="article-options-empty">
                  暂无匹配的文章，请尝试其它关键字
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 题目内容 -->
      <div class="section-card">
        <h3 class="section-title required">题目内容</h3>
        <div class="editor-tabs">
          <button
            @click="activeTab = 'content'"
            :class="['tab-btn', { active: activeTab === 'content' }]"
            type="button"
          >
            编辑
          </button>
          <button
            @click="activeTab = 'content-preview'"
            :class="['tab-btn', { active: activeTab === 'content-preview' }]"
            type="button"
          >
            预览
          </button>
        </div>
        <textarea
          v-show="activeTab === 'content'"
          v-model="questionData.content"
          class="markdown-textarea"
          placeholder="请输入题目内容，支持 Markdown 格式..."
          rows="8"
        ></textarea>
        <div
          v-show="activeTab === 'content-preview'"
          class="markdown-preview"
          v-html="renderMarkdown(questionData.content)"
        ></div>
      </div>

      <!-- 答案 -->
      <div class="section-card">
        <h3 class="section-title required">答案</h3>
        <div class="editor-tabs">
          <button
            @click="activeTab = 'answer'"
            :class="['tab-btn', { active: activeTab === 'answer' }]"
            type="button"
          >
            编辑
          </button>
          <button
            @click="activeTab = 'answer-preview'"
            :class="['tab-btn', { active: activeTab === 'answer-preview' }]"
            type="button"
          >
            预览
          </button>
        </div>
        <textarea
          v-show="activeTab === 'answer'"
          v-model="questionData.answer"
          class="markdown-textarea"
          placeholder="请输入答案内容，支持 Markdown 格式..."
          rows="10"
        ></textarea>
        <div
          v-show="activeTab === 'answer-preview'"
          class="markdown-preview"
          v-html="renderMarkdown(questionData.answer)"
        ></div>
      </div>

      <!-- 解析（可选） -->
      <div class="section-card">
        <h3 class="section-title">解析（可选）</h3>
        <div class="editor-tabs">
          <button
            @click="activeTab = 'explanation'"
            :class="['tab-btn', { active: activeTab === 'explanation' }]"
            type="button"
          >
            编辑
          </button>
          <button
            @click="activeTab = 'explanation-preview'"
            :class="['tab-btn', { active: activeTab === 'explanation-preview' }]"
            type="button"
          >
            预览
          </button>
        </div>
        <textarea
          v-show="activeTab === 'explanation'"
          v-model="questionData.explanation"
          class="markdown-textarea"
          placeholder="请输入解析内容（可选），支持 Markdown 格式..."
          rows="6"
        ></textarea>
        <div
          v-show="activeTab === 'explanation-preview'"
          class="markdown-preview"
          v-html="renderMarkdown(questionData.explanation)"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex';
import axios from 'axios';
import { marked } from 'marked';

const router = useRouter();
const route = useRoute();
const store = useStore();

const isEdit = computed(() => !!route.params.id);
const questionId = computed(() => route.params.id);

const questionData = ref({
  title: '',
  category_id: '',
  type: 'short_answer',
  difficulty: 3,
  content: '',
  answer: '',
  explanation: '',
  tags: [],
  related_article_ids: []
});

const categories = ref([]);
const articleOptions = ref([]);
const selectedArticles = ref([]);
const articleSearch = ref('');
const optionsLoading = ref(false);
const activeTab = ref('content');
const newTag = ref('');
const saving = ref(false);

const canSave = computed(() => {
  return questionData.value.title &&
         questionData.value.category_id &&
         questionData.value.type &&
         questionData.value.content &&
         questionData.value.answer;
});

const loadCategories = async () => {
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/v1/question-bank/categories`);
    if (response.data?.success) {
      // 扁平化所有分类
      const flattenCategories = (cats, parentName = '') => {
        let result = [];
        cats.forEach(cat => {
          result.push({
            ...cat,
            parent_name: parentName
          });
          if (cat.children && cat.children.length > 0) {
            result = result.concat(flattenCategories(cat.children, cat.name));
          }
        });
        return result;
      };
      categories.value = flattenCategories(response.data.data);

      // 如果是新建，并且路由带了 category_id，则预填分类
      if (!isEdit.value) {
        const presetId = route.query.category_id;
        if (presetId) {
          // 转为数字尝试匹配，若失败再用原值
          const parsed = Number(presetId);
          questionData.value.category_id = Number.isNaN(parsed) ? presetId : parsed;
        }
      }
    }
  } catch (error) {
    console.error('加载分类失败:', error);
  }
};

const loadQuestion = async () => {
  if (!isEdit.value) return;

  try {
    const response = await axios.get(
      `${store.state.serverUrl}/api/v1/admin/questions/${questionId.value}`,
      {
        headers: {
          'Authorization': store.state.token
        }
      }
    );

    if (response.data?.success) {
      const data = response.data.data;
      questionData.value = {
        title: data.title || '',
        category_id: data.category_id || '',
        type: data.type || 'short_answer',
        difficulty: data.difficulty || 3,
        content: data.content || '',
        answer: data.answer || '',
        explanation: data.explanation || '',
        tags: data.tags || [],
        related_article_ids: (data.related_articles || []).map(item => item.id)
      };
      selectedArticles.value = data.related_articles || [];
    }
  } catch (error) {
    console.error('加载题目失败:', error);
    alert('加载题目失败: ' + (error.response?.data?.error || error.message));
  }
};

const saveQuestion = async () => {
  if (!canSave.value) {
    alert('请填写必填项');
    return;
  }

  saving.value = true;

  try {
    const url = isEdit.value
      ? `${store.state.serverUrl}/api/v1/admin/questions/${questionId.value}`
      : `${store.state.serverUrl}/api/v1/admin/questions`;
    
    const method = isEdit.value ? 'put' : 'post';

    const response = await axios[method](
      url,
      questionData.value,
      {
        headers: {
          'Authorization': store.state.token
        }
      }
    );

    if (response.data?.success) {
      alert(isEdit.value ? '题目更新成功' : '题目创建成功');
      redirectToList();
    } else {
      alert(response.data?.error || '保存失败');
    }
  } catch (error) {
    console.error('保存题目失败:', error);
    alert('保存失败: ' + (error.response?.data?.error || error.message));
  } finally {
    saving.value = false;
  }
};

const addTag = () => {
  const tag = newTag.value.trim();
  if (tag && !questionData.value.tags.includes(tag)) {
    questionData.value.tags.push(tag);
    newTag.value = '';
  }
};

const removeTag = (index) => {
  questionData.value.tags.splice(index, 1);
};

const loadArticleOptions = async () => {
  optionsLoading.value = true;
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/v1/admin/articles/options`, {
      params: {
        q: articleSearch.value,
        limit: 200
      },
      headers: {
        Authorization: store.state.token
      }
    });
    if (response.data?.success) {
      articleOptions.value = response.data.data || [];
      // 更新已选文章详情
      const selectedMap = new Map(selectedArticles.value.map(item => [item.id, item]));
      questionData.value.related_article_ids.forEach(id => {
        if (!selectedMap.has(id)) {
          const option = articleOptions.value.find(item => item.id === id);
          if (option) {
            selectedMap.set(id, option);
          }
        }
      });
      selectedArticles.value = Array.from(selectedMap.values()).filter(item =>
        questionData.value.related_article_ids.includes(item.id)
      );
    }
  } catch (error) {
    console.error('加载文章列表失败:', error);
  } finally {
    optionsLoading.value = false;
  }
};

const toggleArticleSelection = (article) => {
  const ids = questionData.value.related_article_ids;
  const index = ids.indexOf(article.id);
  if (index > -1) {
    questionData.value.related_article_ids = ids.filter(item => item !== article.id);
    selectedArticles.value = selectedArticles.value.filter(item => item.id !== article.id);
  } else {
    questionData.value.related_article_ids = [...ids, article.id];
    if (!selectedArticles.value.find(item => item.id === article.id)) {
      selectedArticles.value.push(article);
    }
  }
};

const removeSelectedArticle = (articleId) => {
  questionData.value.related_article_ids = questionData.value.related_article_ids.filter(id => id !== articleId);
  selectedArticles.value = selectedArticles.value.filter(item => item.id !== articleId);
};

const renderMarkdown = (content) => {
  if (!content) return '<p class="text-muted">暂无内容</p>';
  return marked(content);
};

// 跳转回列表并携带当前分类
const redirectToList = () => {
  const categoryId = questionData.value.category_id || route.query.category_id;
  router.push({
    path: '/admin/questions',
    query: categoryId ? { category_id: categoryId } : {}
  });
};

const goBack = () => {
  redirectToList();
};

onMounted(() => {
  loadCategories();
  loadArticleOptions();
  if (isEdit.value) {
    loadQuestion();
  }
});
</script>

<style scoped>
.question-editor {
  max-width: 1200px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--color-text-primary, #1f2937);
}

.page-subtitle {
  margin: 0;
  color: var(--color-text-secondary, #6b7280);
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--primary-600, #2563eb);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-700, #1d4ed8);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--color-bg-secondary, #f3f4f6);
  color: var(--gray-600, #4b5563);
}

.btn-secondary:hover {
  background: var(--color-bg-muted, #e5e7eb);
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.editor-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-card {
  background: var(--color-bg-primary, #ffffff);
  color: var(--color-text-primary, #1f2937);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 20px 0;
  color: var(--color-text-primary, #1f2937);
}

.section-title.required::after {
  content: ' *';
  color: #dc2626;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary, #374151);
}

.form-label.required::after {
  content: ' *';
  color: #dc2626;
}

.form-input,
.form-select {
  padding: 10px 12px;
  border: 1px solid var(--color-border-secondary, #d1d5db);
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--primary-600, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.radio-group {
  display: flex;
  gap: 16px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
  color: var(--gray-600, #4b5563);
}

.radio-label input[type="radio"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.difficulty-selector {
  display: flex;
  gap: 8px;
}

.difficulty-btn {
  padding: 8px 16px;
  border: 2px solid var(--color-border-primary, #e5e7eb);
  border-radius: 6px;
  background: var(--color-bg-primary, #ffffff);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.difficulty-btn:hover {
  border-color: var(--primary-600, #2563eb);
  background: var(--primary-50, #eff6ff);
}

.difficulty-btn.active {
  border-color: var(--primary-600, #2563eb);
  background: var(--primary-600, #2563eb);
  color: white;
}

.tags-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  border: 1px solid var(--color-border-secondary, #d1d5db);
  border-radius: 6px;
  background: var(--color-bg-primary, #ffffff);
}

.selected-articles {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.selected-article-chip {
  display: flex;
  flex-direction: column;
  padding: 8px 12px;
  border-radius: 10px;
  background: var(--primary-50, #eff6ff);
  border: 1px solid var(--primary-200, #bfdbfe);
  position: relative;
  min-width: 160px;
}

.chip-title {
  font-weight: 600;
  font-size: 13px;
  color: var(--primary-800, #1e40af);
}

.chip-meta {
  font-size: 12px;
  color: var(--color-text-secondary, #6b7280);
}

.chip-remove {
  position: absolute;
  top: 4px;
  right: 6px;
  border: none;
  background: transparent;
  color: var(--color-text-muted, #9ca3af);
  cursor: pointer;
  font-size: 14px;
}

.chip-remove:hover {
  color: var(--primary-600, #2563eb);
}

.article-search-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.article-options-panel {
  border: 1px solid var(--color-border-secondary, #d1d5db);
  border-radius: 10px;
  padding: 12px;
  background: var(--color-bg-primary, #ffffff);
}

.article-options-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-secondary, #6b7280);
}

.article-options-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 260px;
  overflow-y: auto;
}

.article-option-item {
  border: 1px solid var(--color-border-primary, #e5e7eb);
  border-radius: 8px;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--color-bg-secondary, #f9fafb);
}

.article-option-item.selected {
  border-color: var(--primary-400, #60a5fa);
  background: rgba(96, 165, 250, 0.15);
}

.article-option-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.article-option-title {
  font-weight: 600;
  color: var(--color-text-primary, #1f2937);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: 8px;
}

.article-option-meta {
  font-size: 12px;
  color: var(--color-text-secondary, #6b7280);
  margin-top: 4px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.option-id {
  color: var(--color-text-muted, #9ca3af);
}

.article-options-empty {
  text-align: center;
  color: var(--color-text-secondary, #6b7280);
  padding: 20px 0;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: var(--primary-50, #eff6ff);
  color: var(--primary-800, #1e40af);
  border-radius: 4px;
  font-size: 13px;
}

.tag-remove {
  display: flex;
  align-items: center;
  padding: 0;
  border: none;
  background: none;
  cursor: pointer;
  color: var(--primary-800, #1e40af);
}

.tag-remove svg {
  width: 14px;
  height: 14px;
}

.tag-input {
  padding: 8px 0;
  border: none;
  font-size: 14px;
  outline: none;
}

.editor-tabs {
  display: flex;
  gap: 2px;
  margin-bottom: 12px;
  border-bottom: 2px solid var(--color-border-primary, #e5e7eb);
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary, #6b7280);
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--primary-600, #2563eb);
}

.tab-btn.active {
  color: var(--primary-600, #2563eb);
  border-bottom-color: var(--primary-600, #2563eb);
}

.markdown-textarea {
  width: 100%;
  padding: 16px;
  border: 1px solid var(--color-border-secondary, #d1d5db);
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  min-height: 150px;
}

.markdown-textarea:focus {
  outline: none;
  border-color: var(--primary-600, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.markdown-preview {
  padding: 16px;
  border: 1px solid var(--color-border-secondary, #d1d5db);
  border-radius: 6px;
  background: var(--color-bg-secondary, #f9fafb);
  min-height: 150px;
  line-height: 1.6;
}

.markdown-preview :deep(pre) {
  background: #1f2937;
  color: #f9fafb;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-preview :deep(code) {
  background: var(--color-bg-muted, #e5e7eb);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.9em;
}

.markdown-preview :deep(pre code) {
  background: none;
  padding: 0;
}

.text-muted {
  color: var(--color-text-muted, #9ca3af);
  font-style: italic;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .header-actions {
    width: 100%;
  }

  .btn {
    flex: 1;
  }
}
</style>


