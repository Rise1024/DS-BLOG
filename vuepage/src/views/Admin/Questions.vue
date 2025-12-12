<template>
  <div class="questions-manage">
    <div class="page-header">
      <div>
        <h1 class="page-title">题目管理</h1>
        <p class="page-subtitle">管理题库中的所有题目</p>
      </div>
      <button @click="createRootCategory" class="btn btn-primary">
        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>
        新建根分类
      </button>
    </div>

    <div class="content-card">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="categories.length === 0" class="empty-state">
        <p>暂无分类</p>
      </div>

      <AdminTreeView 
        v-else-if="treeData && (Array.isArray(treeData) || treeData.title)"
        :data="treeData"
        :default-expand-node-id="route.query.category_id"
        :on-node-click="handleNodeClick"
        :on-edit="handleEdit"
        :on-delete="handleDelete"
        :on-create="handleCreate"
        :on-create-category="handleCreateCategory"
        :on-edit-category="handleEditCategory"
        :on-delete-category="handleDeleteCategory"
      />
    </div>

    <!-- 分类编辑对话框 -->
    <CategoryDialog
      :show="showCategoryDialog"
      :category="editingCategory"
      :parent-categories="allCategories"
      @close="closeCategoryDialog"
      @save="saveCategory"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex';
import axios from 'axios';
import AdminTreeView from '@/components/AdminTreeView.vue';
import CategoryDialog from '@/components/CategoryDialog.vue';

const router = useRouter();
const route = useRoute();
const store = useStore();

const loading = ref(false);
const categories = ref([]);
const showCategoryDialog = ref(false);
const editingCategory = ref(null);

const loadCategories = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`${store.state.serverUrl}/api/v1/question-bank/categories?clear_cache=true`, {
      headers: {
        'Authorization': store.state.token
      }
    });
    if (response.data?.success) {
      categories.value = response.data.data || [];
    }
  } catch (error) {
    console.error('加载分类失败:', error);
    categories.value = [];
  } finally {
    loading.value = false;
  }
};

// 转换为树形结构
const treeData = computed(() => {
  if (!categories.value || categories.value.length === 0) {
    return [];
  }

  // 递归转换分类为树形节点
  const convertCategory = (cat) => {
    if (!cat) return null;
    
    const node = {
      title: cat.name,
      name: cat.name,
      id: cat.id,
      description: cat.description,
      parent_id: cat.parent_id,
      order: cat.order || 0,
      total_question_count: cat.total_question_count || cat.question_count || 0,
      question_count: cat.question_count || 0,
      isCategory: true // 明确标记这是分类节点
    };

    // 如果有子分类，转换子分类
    if (cat.children && cat.children.length > 0) {
      node.children = cat.children.map(convertCategory).filter(n => n !== null);
    }

    // 如果有题目列表（items），转换为 items 格式
    if (cat.items && cat.items.length > 0) {
      node.items = cat.items.map(item => ({
        title: item.title,
        id: item.id,
        type: item.type,
        difficulty: item.difficulty
      }));
    }

    return node;
  };

  // 直接返回所有根分类的数组
  return categories.value.map(convertCategory).filter(n => n !== null);
});

const createRootCategory = () => {
  // 创建根分类（parent_id 为 null）
  editingCategory.value = {
    parent_id: null,
    order: 0
  };
  showCategoryDialog.value = true;
};

const handleCreate = (node) => {
  // 在指定分类下创建题目
  router.push({
    path: '/admin/questions/new',
    query: { category_id: node.id }
  });
};

const handleEdit = (node) => {
  if (node.id) {
    editQuestion(node.id);
  }
};

const editQuestion = (id) => {
  router.push(`/admin/questions/edit/${id}`);
};

const handleDelete = async (node) => {
  if (node.id) {
    await deleteQuestion(node.id);
  }
};

const deleteQuestion = async (id) => {
  if (!confirm('确定要删除这道题目吗？')) return;

  try {
    const response = await axios.delete(`${store.state.serverUrl}/api/v1/admin/questions/${id}`, {
      headers: {
        'Authorization': store.state.token
      }
    });

    if (response.data?.success) {
      alert('删除成功');
      loadCategories(); // 重新加载分类数据
    }
  } catch (error) {
    console.error('删除题目失败:', error);
    alert('删除失败: ' + (error.response?.data?.error || error.message));
  }
};

const handleNodeClick = (node) => {
  // 点击节点时的处理（如果需要）
};

// 获取所有分类（扁平化）用于选择父分类
const allCategories = computed(() => {
  const flatten = (cats, result = []) => {
    cats.forEach(cat => {
      result.push({
        id: cat.id,
        name: cat.name
      });
      if (cat.children && cat.children.length > 0) {
        flatten(cat.children, result);
      }
    });
    return result;
  };
  return flatten(categories.value);
});

// 分类管理功能
const handleCreateCategory = (parentNode) => {
  editingCategory.value = {
    parent_id: parentNode?.id || null,
    order: 0
  };
  showCategoryDialog.value = true;
};

const handleEditCategory = (node) => {
  // 从原始分类数据中查找完整信息
  const findCategory = (cats, id) => {
    for (const cat of cats) {
      if (cat.id === id) {
        return {
          id: cat.id,
          name: cat.name,
          description: cat.description || '',
          parent_id: cat.parent_id,
          order: cat.order || 0
        };
      }
      if (cat.children) {
        const found = findCategory(cat.children, id);
        if (found) return found;
      }
    }
    return null;
  };
  
  const fullCategory = findCategory(categories.value, node.id);
  if (fullCategory) {
    editingCategory.value = fullCategory;
    showCategoryDialog.value = true;
  }
};

const handleDeleteCategory = async (node) => {
  if (!node.id) return;
  
  // 检查是否有子分类或题目
  const findCategory = (cats, id) => {
    for (const cat of cats) {
      if (cat.id === id) return cat;
      if (cat.children) {
        const found = findCategory(cat.children, id);
        if (found) return found;
      }
    }
    return null;
  };
  
  const fullCategory = findCategory(categories.value, node.id);
  if (fullCategory) {
    const questionCount = fullCategory.total_question_count || fullCategory.question_count || 0;
    const childrenCount = fullCategory.children?.length || 0;
    
    if (questionCount > 0 || childrenCount > 0) {
      alert(`该分类下有 ${questionCount} 道题目和 ${childrenCount} 个子分类，无法删除`);
      return;
    }
  }
  
  if (!confirm(`确定要删除分类「${node.title || node.name}」吗？`)) return;

  try {
    const response = await axios.delete(`${store.state.serverUrl}/api/v1/admin/categories/${node.id}`, {
      headers: {
        'Authorization': store.state.token
      }
    });

    if (response.data?.success) {
      alert('删除成功');
      loadCategories();
    }
  } catch (error) {
    console.error('删除分类失败:', error);
    alert('删除失败: ' + (error.response?.data?.error || error.message));
  }
};

const saveCategory = async (categoryData) => {
  try {
    const url = categoryData.id
      ? `${store.state.serverUrl}/api/v1/admin/categories/${categoryData.id}`
      : `${store.state.serverUrl}/api/v1/admin/categories`;
    
    const method = categoryData.id ? 'put' : 'post';

    const response = await axios[method](
      url,
      categoryData,
      {
        headers: {
          'Authorization': store.state.token
        }
      }
    );

    if (response.data?.success) {
      alert(categoryData.id ? '分类更新成功' : '分类创建成功');
      closeCategoryDialog();
      loadCategories();
    } else {
      alert(response.data?.error || '保存失败');
    }
  } catch (error) {
    console.error('保存分类失败:', error);
    alert('保存失败: ' + (error.response?.data?.error || error.message));
  }
};

const closeCategoryDialog = () => {
  showCategoryDialog.value = false;
  editingCategory.value = null;
};

onMounted(() => {
  loadCategories();
});
</script>

<style scoped>
.questions-manage {
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
  padding: 20px;
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

.btn-primary:hover {
  background: var(--primary-700, #1d4ed8);
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
</style>


