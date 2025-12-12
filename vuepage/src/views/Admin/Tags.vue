<template>
  <div class="tags-manage">
    <div class="page-header">
      <div>
        <h1 class="page-title">标签管理</h1>
        <p class="page-subtitle">管理题目和文章标签</p>
      </div>
    </div>

    <div class="content-card">
      <div class="tags-grid" v-if="!loading && tags.length > 0">
        <div v-for="tag in tags" :key="tag.id" class="tag-card">
          <div class="tag-header">
            <span class="tag-name">{{ tag.name }}</span>
            <span class="tag-count">{{ tag.count }} 次使用</span>
          </div>
          <div class="tag-actions">
            <button @click="deleteTag(tag)" class="btn-tag-action" title="删除">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-if="!loading && tags.length === 0" class="empty-state">
        <p>暂无标签</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import axios from 'axios';

const store = useStore();

const loading = ref(false);
const tags = ref([]);

const loadTags = async () => {
  loading.value = true;
  try {
    // 从所有题目中获取标签（简化版）
    const response = await axios.get(`${store.state.serverUrl}/api/v1/question-bank/questions?page_size=1000`);
    
    if (response.data?.success) {
      // 统计标签
      const tagMap = new Map();
      response.data.data.forEach(question => {
        if (question.tags) {
          question.tags.forEach(tagName => {
            if (tagMap.has(tagName)) {
              tagMap.set(tagName, tagMap.get(tagName) + 1);
            } else {
              tagMap.set(tagName, 1);
            }
          });
        }
      });

      tags.value = Array.from(tagMap.entries()).map(([name, count], index) => ({
        id: index + 1,
        name,
        count
      })).sort((a, b) => b.count - a.count);
    }
  } catch (error) {
    console.error('加载标签失败:', error);
    alert('加载标签失败: ' + (error.response?.data?.error || error.message));
  } finally {
    loading.value = false;
  }
};

const deleteTag = (tag) => {
  if (tag.count > 0) {
    alert(`标签「${tag.name}」正在被 ${tag.count} 个项目使用，无法删除`);
    return;
  }

  if (!confirm(`确定要删除标签「${tag.name}」吗？`)) return;

  // 实际应该调用后端API删除
  alert('删除功能需要后端支持');
};

onMounted(() => {
  loadTags();
});
</script>

<style scoped>
.tags-manage {
  max-width: 1400px;
}

.page-header {
  margin-bottom: 24px;
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
}

.content-card {
  background: var(--color-bg-primary, #ffffff);
  color: var(--color-text-primary, #1f2937);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.tag-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: var(--color-bg-secondary, #f9fafb);
  border: 1px solid var(--color-border-primary, #e5e7eb);
  border-radius: 8px;
  transition: all 0.2s;
}

.tag-card:hover {
  background: var(--primary-50, #eff6ff);
  border-color: var(--primary-600, #2563eb);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
}

.tag-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tag-name {
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text-primary, #1f2937);
}

.tag-count {
  font-size: 13px;
  color: var(--color-text-secondary, #6b7280);
}

.tag-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-tag-action {
  padding: 6px;
  border: none;
  border-radius: 4px;
  background: var(--color-bg-secondary, #f3f4f6);
  color: var(--color-text-secondary, #6b7280);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-tag-action:hover {
  background: #fee2e2;
  color: #dc2626;
}

.btn-tag-action svg {
  width: 16px;
  height: 16px;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--color-text-secondary, #6b7280);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border-primary, #e5e7eb);
  border-top-color: var(--primary-600, #2563eb);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .tags-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>


