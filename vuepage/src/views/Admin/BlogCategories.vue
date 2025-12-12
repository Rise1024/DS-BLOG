<template>
  <div class="blog-categories-manage">
    <div class="page-header">
      <div>
        <h1 class="page-title">博客分类管理</h1>
        <p class="page-subtitle">管理博客文章分类</p>
      </div>
      <button @click="showCreateDialog = true" class="btn btn-primary">
        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        新建分类
      </button>
    </div>

    <div class="content-card">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="categories.length === 0" class="empty-state">
        <p>暂无分类</p>
        <p class="empty-hint">分类会在创建文章时自动创建</p>
      </div>

      <div v-else class="categories-list">
        <div v-for="category in categories" :key="category.name" class="category-card">
          <div class="category-header">
            <div class="category-info">
              <h3 class="category-name">{{ category.name }}</h3>
              <span class="category-count">{{ category.count }} 篇文章</span>
            </div>
            <div class="category-actions">
              <button @click="editCategory(category)" class="btn-action btn-edit" title="重命名">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
              <button @click="deleteCategory(category)" class="btn-action btn-delete" title="删除">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- 子分类列表 -->
          <div v-if="category.subcategories && category.subcategories.length > 0" class="subcategories">
            <div v-for="subcat in category.subcategories" :key="subcat.name" class="subcategory-item">
              <span class="subcategory-name">{{ subcat.name }}</span>
              <span class="subcategory-count">{{ subcat.count }} 篇</span>
              <button @click="editSubcategory(category, subcat)" class="btn-action-small btn-edit-small" title="重命名">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
              <button @click="deleteSubcategory(category, subcat)" class="btn-action-small btn-delete-small" title="删除">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建分类对话框 -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click.self="closeCreateDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>新建分类</h3>
          <button @click="closeCreateDialog" class="dialog-close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="dialog-body">
          <div class="form-group">
            <label class="form-label">作为子分类</label>
            <select v-model="parentCategoryForSub" class="form-select">
              <option :value="null">无（创建主分类）</option>
              <option v-for="cat in categories" :key="cat.name" :value="cat.name">
                {{ cat.name }}
              </option>
            </select>
            <p class="form-hint">选择父分类可创建子分类，留空则创建主分类</p>
          </div>

          <div class="form-group">
            <label class="form-label required">{{ parentCategoryForSub ? '子分类名称' : '分类名称' }}</label>
            <input
              v-model="newCategoryName"
              type="text"
              class="form-input"
              :placeholder="parentCategoryForSub ? '请输入子分类名称' : '请输入分类名称'"
            />
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="closeCreateDialog" class="btn btn-secondary">取消</button>
          <button @click="createCategory" class="btn btn-primary" :disabled="!newCategoryName || saving">
            {{ saving ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 重命名对话框 -->
    <div v-if="showRenameDialog" class="dialog-overlay" @click.self="closeRenameDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ editingSubcategory ? '重命名子分类' : '重命名分类' }}</h3>
          <button @click="closeRenameDialog" class="dialog-close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="dialog-body">
          <div class="form-group">
            <label class="form-label">当前名称</label>
            <input
              :value="editingCategory?.name || editingSubcategory?.name"
              type="text"
              class="form-input"
              disabled
            />
          </div>

          <div class="form-group">
            <label class="form-label required">新名称</label>
            <input
              v-model="newCategoryName"
              type="text"
              class="form-input"
              placeholder="请输入新名称"
            />
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="closeRenameDialog" class="btn btn-secondary">取消</button>
          <button @click="saveRename" class="btn btn-primary" :disabled="!newCategoryName || saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
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
const categories = ref([]);
const showRenameDialog = ref(false);
const showCreateDialog = ref(false);
const editingCategory = ref(null);
const editingSubcategory = ref(null);
const newCategoryName = ref('');
const newSubcategoryName = ref('');
const parentCategoryForSub = ref(null);
const saving = ref(false);

const loadCategories = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/v1/admin/blog-categories`, {
      headers: {
        'Authorization': store.state.token
      }
    });

    if (response.data?.success) {
      categories.value = response.data.data || [];
    }
  } catch (error) {
    console.error('加载博客分类失败:', error);
    alert('加载分类失败: ' + (error.response?.data?.error || error.message));
  } finally {
    loading.value = false;
  }
};

const editCategory = (category) => {
  editingCategory.value = category;
  editingSubcategory.value = null;
  newCategoryName.value = category.name;
  showRenameDialog.value = true;
};

const editSubcategory = (category, subcategory) => {
  editingCategory.value = category;
  editingSubcategory.value = subcategory;
  newCategoryName.value = subcategory.name;
  showRenameDialog.value = true;
};

const saveRename = async () => {
  if (!newCategoryName.value.trim()) {
    alert('请输入新名称');
    return;
  }

  saving.value = true;
  try {
    const response = await axios.post(
      `${store.state.serverUrl}/api/v1/admin/blog-categories/rename`,
      {
        old_name: editingCategory.value.name,
        new_name: newCategoryName.value.trim(),
        subcategory: editingSubcategory.value?.name
      },
      {
        headers: {
          'Authorization': store.state.token
        }
      }
    );

    if (response.data?.success) {
      alert(`重命名成功，已更新 ${response.data.data.updated_count} 篇文章`);
      closeRenameDialog();
      loadCategories();
    } else {
      alert(response.data?.error || '重命名失败');
    }
  } catch (error) {
    console.error('重命名失败:', error);
    alert('重命名失败: ' + (error.response?.data?.error || error.message));
  } finally {
    saving.value = false;
  }
};

const deleteCategory = async (category) => {
  if (category.count > 0) {
    if (!confirm(`分类「${category.name}」下有 ${category.count} 篇文章，删除后这些文章将移到「未分类」。确定要删除吗？`)) {
      return;
    }
  } else {
    if (!confirm(`确定要删除分类「${category.name}」吗？`)) {
      return;
    }
  }

  try {
    const response = await axios.post(
      `${store.state.serverUrl}/api/v1/admin/blog-categories/delete`,
      {
        name: category.name
      },
      {
        headers: {
          'Authorization': store.state.token
        }
      }
    );

    if (response.data?.success) {
      alert(`删除成功，已更新 ${response.data.data.updated_count} 篇文章`);
      loadCategories();
    } else {
      alert(response.data?.error || '删除失败');
    }
  } catch (error) {
    console.error('删除分类失败:', error);
    alert('删除失败: ' + (error.response?.data?.error || error.message));
  }
};

const deleteSubcategory = async (category, subcategory) => {
  if (!confirm(`确定要删除子分类「${subcategory.name}」吗？删除后相关文章的子分类将被清空。`)) {
    return;
  }

  try {
    const response = await axios.post(
      `${store.state.serverUrl}/api/v1/admin/blog-categories/delete`,
      {
        name: category.name,
        subcategory: subcategory.name
      },
      {
        headers: {
          'Authorization': store.state.token
        }
      }
    );

    if (response.data?.success) {
      alert(`删除成功，已更新 ${response.data.data.updated_count} 篇文章`);
      loadCategories();
    } else {
      alert(response.data?.error || '删除失败');
    }
  } catch (error) {
    console.error('删除子分类失败:', error);
    alert('删除失败: ' + (error.response?.data?.error || error.message));
  }
};

const closeRenameDialog = () => {
  showRenameDialog.value = false;
  editingCategory.value = null;
  editingSubcategory.value = null;
  newCategoryName.value = '';
};

const closeCreateDialog = () => {
  showCreateDialog.value = false;
  newCategoryName.value = '';
  newSubcategoryName.value = '';
  parentCategoryForSub.value = null;
};

const createCategory = async () => {
  if (!newCategoryName.value.trim()) {
    alert('请输入分类名称');
    return;
  }

  saving.value = true;
  try {
    const response = await axios.post(
      `${store.state.serverUrl}/api/v1/admin/blog-categories`,
      {
        name: newCategoryName.value.trim(),
        parent_name: parentCategoryForSub.value,
        description: '',
        order: 0
      },
      {
        headers: {
          'Authorization': store.state.token
        }
      }
    );

    if (response.data?.success) {
      alert('分类创建成功！');
      closeCreateDialog();
      loadCategories();
    } else {
      alert(response.data?.error || '创建失败');
    }
  } catch (error) {
    console.error('创建分类失败:', error);
    alert('创建失败: ' + (error.response?.data?.error || error.message));
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  loadCategories();
});
</script>

<style scoped>
.blog-categories-manage {
  max-width: 1400px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--color-text-secondary, #6b7280);
}

.empty-hint {
  font-size: 13px;
  color: var(--color-text-muted, #9ca3af);
  margin-top: 8px;
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

.categories-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.category-card {
  border: 1px solid var(--color-border-primary, #e5e7eb);
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s;
  background: var(--color-bg-primary, #ffffff);
}

.category-card:hover {
  border-color: var(--primary-600, #2563eb);
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: var(--color-text-primary, #1f2937);
}

.category-count {
  font-size: 13px;
  color: var(--color-text-secondary, #6b7280);
  background: var(--color-bg-secondary, #f3f4f6);
  padding: 4px 10px;
  border-radius: 12px;
}

.category-actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  padding: 6px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--color-bg-secondary, #f3f4f6);
  color: var(--color-text-secondary, #6b7280);
}

.btn-action svg {
  width: 16px;
  height: 16px;
}

.btn-edit:hover {
  background: var(--primary-50, #eff6ff);
  color: var(--primary-600, #2563eb);
}

.btn-delete:hover {
  background: #fee2e2;
  color: #dc2626;
}

.subcategories {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-primary, #e5e7eb);
}

.subcategory-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--color-bg-secondary, #f9fafb);
  border-radius: 6px;
  margin-bottom: 8px;
}

.subcategory-item:last-child {
  margin-bottom: 0;
}

.subcategory-name {
  flex: 1;
  font-size: 14px;
  color: var(--color-text-primary, #374151);
  font-weight: 500;
}

.subcategory-count {
  font-size: 12px;
  color: var(--color-text-secondary, #6b7280);
}

.btn-action-small {
  padding: 4px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  background: transparent;
  color: var(--color-text-muted, #9ca3af);
}

.btn-action-small svg {
  width: 14px;
  height: 14px;
}

.btn-edit-small:hover {
  color: var(--primary-600, #2563eb);
}

.btn-delete-small:hover {
  color: #dc2626;
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.dialog {
  background: var(--color-bg-primary, #ffffff);
  color: var(--color-text-primary, #1f2937);
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border-primary, #e5e7eb);
}

.dialog-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary, #1f2937);
}

.dialog-close {
  padding: 4px;
  border: none;
  background: none;
  cursor: pointer;
  color: var(--color-text-secondary, #6b7280);
  transition: color 0.2s;
}

.dialog-close:hover {
  color: var(--color-text-primary, #1f2937);
}

.dialog-close svg {
  width: 20px;
  height: 20px;
}

.dialog-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.form-group {
  margin-bottom: 20px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary, #374151);
  margin-bottom: 8px;
}

.form-label.required::after {
  content: ' *';
  color: #dc2626;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border-secondary, #d1d5db);
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-600, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-input:disabled {
  background: var(--color-bg-secondary, #f3f4f6);
  color: var(--color-text-secondary, #6b7280);
  cursor: not-allowed;
}

.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border-secondary, #d1d5db);
  border-radius: 6px;
  font-size: 14px;
  background: var(--color-bg-primary, #ffffff);
  transition: all 0.2s;
}

.form-select:focus {
  outline: none;
  border-color: var(--primary-600, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-hint {
  font-size: 12px;
  color: var(--color-text-secondary, #6b7280);
  margin-top: 4px;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border-primary, #e5e7eb);
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
</style>

