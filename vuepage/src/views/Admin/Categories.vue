<template>
  <div class="categories-manage">
    <div class="page-header">
      <div>
        <h1 class="page-title">分类管理</h1>
        <p class="page-subtitle">管理题库分类结构</p>
      </div>
      <button @click="createCategory" class="btn btn-primary">
        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        新建分类
      </button>
    </div>

    <div class="content-card">
      <table class="data-table" v-if="!loading && categories.length > 0">
        <thead>
          <tr>
            <th>ID</th>
            <th>名称</th>
            <th>描述</th>
            <th>父分类</th>
            <th>排序</th>
            <th>题目数</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="category in categories" :key="category.id">
            <td>{{ category.id }}</td>
            <td>
              <span :style="{ paddingLeft: (category.level || 0) * 20 + 'px' }">
                {{ category.level > 0 ? '└─ ' : '' }}{{ category.name }}
              </span>
            </td>
            <td class="description-cell">{{ category.description || '-' }}</td>
            <td>{{ category.parent_name || '-' }}</td>
            <td>{{ category.order }}</td>
            <td>{{ category.question_count }}</td>
            <td>
              <div class="action-buttons">
                <button @click="editCategory(category)" class="btn-action btn-edit" title="编辑">
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
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-if="!loading && categories.length === 0" class="empty-state">
        <p>暂无分类</p>
      </div>
    </div>

    <!-- 编辑对话框 -->
    <div v-if="showDialog" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ editingCategory.id ? '编辑分类' : '新建分类' }}</h3>
          <button @click="closeDialog" class="dialog-close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="dialog-body">
          <div class="form-group">
            <label class="form-label required">分类名称</label>
            <input
              v-model="editingCategory.name"
              type="text"
              class="form-input"
              placeholder="请输入分类名称"
            />
          </div>

          <div class="form-group">
            <label class="form-label">描述</label>
            <textarea
              v-model="editingCategory.description"
              class="form-textarea"
              placeholder="请输入分类描述（可选）"
              rows="3"
            ></textarea>
          </div>

          <div class="form-group">
            <label class="form-label">父分类</label>
            <select v-model="editingCategory.parent_id" class="form-select">
              <option :value="null">无（顶级分类）</option>
              <option
                v-for="cat in availableParents"
                :key="cat.id"
                :value="cat.id"
              >
                {{ cat.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">排序</label>
            <input
              v-model.number="editingCategory.order"
              type="number"
              class="form-input"
              placeholder="数字越小越靠前"
              min="0"
            />
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="closeDialog" class="btn btn-secondary">取消</button>
          <button @click="saveCategory" class="btn btn-primary" :disabled="!editingCategory.name">
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import axios from 'axios';

const store = useStore();

const loading = ref(false);
const categories = ref([]);
const showDialog = ref(false);
const editingCategory = ref({
  id: null,
  name: '',
  description: '',
  parent_id: null,
  order: 0
});

const availableParents = computed(() => {
  // 编辑时，不能选择自己和自己的子分类作为父分类
  if (editingCategory.value.id) {
    return categories.value.filter(cat => 
      cat.id !== editingCategory.value.id && 
      cat.parent_id !== editingCategory.value.id &&
      cat.level === 0 // 只允许顶级分类作为父分类
    );
  }
  return categories.value.filter(cat => !cat.parent_id);
});

const loadCategories = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/v1/admin/categories`, {
      headers: {
        'Authorization': store.state.token
      }
    });

    if (response.data?.success) {
      // 扁平化并添加层级信息
      const flattenCategories = (cats, level = 0, parentName = '') => {
        let result = [];
        cats.forEach(cat => {
          result.push({
            ...cat,
            level,
            parent_name: parentName
          });
          if (cat.children && cat.children.length > 0) {
            result = result.concat(flattenCategories(cat.children, level + 1, cat.name));
          }
        });
        return result;
      };

      categories.value = flattenCategories(response.data.data);
    }
  } catch (error) {
    console.error('加载分类失败:', error);
    alert('加载分类失败: ' + (error.response?.data?.error || error.message));
  } finally {
    loading.value = false;
  }
};

const createCategory = () => {
  editingCategory.value = {
    id: null,
    name: '',
    description: '',
    parent_id: null,
    order: 0
  };
  showDialog.value = true;
};

const editCategory = (category) => {
  editingCategory.value = {
    id: category.id,
    name: category.name,
    description: category.description || '',
    parent_id: category.parent_id,
    order: category.order
  };
  showDialog.value = true;
};

const saveCategory = async () => {
  if (!editingCategory.value.name) {
    alert('请输入分类名称');
    return;
  }

  try {
    const url = editingCategory.value.id
      ? `${store.state.serverUrl}/api/v1/admin/categories/${editingCategory.value.id}`
      : `${store.state.serverUrl}/api/v1/admin/categories`;
    
    const method = editingCategory.value.id ? 'put' : 'post';

    const response = await axios[method](
      url,
      editingCategory.value,
      {
        headers: {
          'Authorization': store.state.token
        }
      }
    );

    if (response.data?.success) {
      alert(editingCategory.value.id ? '分类更新成功' : '分类创建成功');
      closeDialog();
      loadCategories();
    } else {
      alert(response.data?.error || '保存失败');
    }
  } catch (error) {
    console.error('保存分类失败:', error);
    alert('保存失败: ' + (error.response?.data?.error || error.message));
  }
};

const deleteCategory = async (category) => {
  if (category.question_count > 0) {
    alert(`该分类下有 ${category.question_count} 道题目，无法删除`);
    return;
  }

  if (!confirm(`确定要删除分类「${category.name}」吗？`)) return;

  try {
    const response = await axios.delete(
      `${store.state.serverUrl}/api/v1/admin/categories/${category.id}`,
      {
        headers: {
          'Authorization': store.state.token
        }
      }
    );

    if (response.data?.success) {
      alert('删除成功');
      loadCategories();
    }
  } catch (error) {
    console.error('删除分类失败:', error);
    alert('删除失败: ' + (error.response?.data?.error || error.message));
  }
};

const closeDialog = () => {
  showDialog.value = false;
  editingCategory.value = {
    id: null,
    name: '',
    description: '',
    parent_id: null,
    order: 0
  };
};

onMounted(() => {
  loadCategories();
});
</script>

<style scoped>
/* 复用之前的样式 */
.categories-manage {
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
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: var(--color-bg-secondary, #f9fafb);
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 13px;
  color: var(--color-text-secondary, #6b7280);
  border-bottom: 1px solid var(--color-border-primary, #e5e7eb);
}

.data-table td {
  padding: 16px;
  border-bottom: 1px solid var(--color-border-primary, #e5e7eb);
  font-size: 14px;
  color: var(--color-text-primary, #1f2937);
}

.description-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-action {
  padding: 6px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-action svg {
  width: 16px;
  height: 16px;
}

.btn-edit {
  background: var(--color-bg-secondary, #f3f4f6);
  color: var(--color-text-secondary, #6b7280);
}

.btn-edit:hover {
  background: var(--primary-50, #eff6ff);
  color: var(--primary-600, #2563eb);
}

.btn-delete {
  background: var(--color-bg-secondary, #f3f4f6);
  color: var(--color-text-secondary, #6b7280);
}

.btn-delete:hover {
  background: #fee2e2;
  color: #dc2626;
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

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border-secondary, #d1d5db);
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-600, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border-primary, #e5e7eb);
}
</style>


