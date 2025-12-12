<template>
  <div class="articles-manage">
    <div class="page-header">
      <div>
        <h1 class="page-title">文章管理</h1>
        <p class="page-subtitle">管理博客文章</p>
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

    <!-- 博客分类编辑对话框 -->
    <BlogCategoryDialog
      :show="showCategoryDialog"
      :category="editingCategory"
      :parent-categories="flatCategories"
      @close="closeCategoryDialog"
      @save="saveCategory"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex';
import axios from 'axios';
import AdminTreeView from '@/components/AdminTreeView.vue';
import BlogCategoryDialog from '@/components/BlogCategoryDialog.vue';

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
    const response = await axios.get(`${store.state.serverUrl}/api/v1/blog/categories?clear_cache=true`);

    if (response.data?.success) {
      categories.value = response.data.data || [];
      // 数据加载完成后，确保展开到当前类目
      // 使用 nextTick 确保 treeData 已更新
      await nextTick();
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
      id: cat.id,
      title: cat.name,
      name: cat.name,
      count: cat.count || 0,
      total_count: cat.total_count || cat.count || 0,
      parent_id: cat.parent_id, // 保留 parent_id 用于判断是否是分类节点
      isCategory: true // 明确标记这是分类节点
    };

    const childrenSource = cat.children || [];
    if (childrenSource.length > 0) {
      node.children = childrenSource.map(convertCategory).filter(n => n !== null);
    }

    const itemsSource = cat.items || [];
    if (itemsSource.length > 0) {
      node.items = itemsSource.map(item => ({
        title: item.title,
        id: item.id,
        category_id: item.category_id
      }));
    }

    return node;
  };

  // 直接返回所有根分类的数组
  const result = categories.value.map(convertCategory).filter(n => n !== null);
  console.log('文章管理 treeData:', result);
  return result;
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
  // 在指定分类下创建文章
  router.push({
    path: '/admin/articles/new',
    query: { 
      category_id: node.id || ''
    }
  });
};

const handleEdit = (node) => {
  if (node.id) {
    editArticle(node.id, node.category_id);
  }
};

const editArticle = (id, categoryId = null) => {
  // 获取当前类目ID，优先使用传入的 category_id，否则使用路由中的
  const currentCategoryId = categoryId || route.query.category_id;
  router.push({
    path: `/admin/articles/edit/${id}`,
    query: currentCategoryId ? { category_id: currentCategoryId } : {}
  });
};

const handleDelete = async (node) => {
  if (node.id) {
    await deleteArticle(node.id);
  }
};

const deleteArticle = async (id) => {
  if (!confirm('确定要删除这篇文章吗？')) return;

  try {
    const response = await axios.delete(`${store.state.serverUrl}/api/v1/admin/articles/${id}`, {
      headers: {
        'Authorization': store.state.token
      }
    });

    if (response.data?.success) {
      alert('删除成功');
      // 保持在当前类目，只重新加载数据
      const currentCategoryId = route.query.category_id;
      await loadCategories();
      // 确保路由保持在当前类目（使用 push 而不是 replace 以触发更新）
      if (currentCategoryId) {
        await nextTick();
        router.push({
          path: '/admin/articles',
          query: { category_id: currentCategoryId }
        });
      }
    } else {
      alert(response.data?.error || '删除失败');
      // 失败时也保持在当前类目
      const currentCategoryId = route.query.category_id;
      if (currentCategoryId) {
        await nextTick();
        router.push({
          path: '/admin/articles',
          query: { category_id: currentCategoryId }
        });
      }
    }
  } catch (error) {
    console.error('删除文章失败:', error);
    alert('删除失败: ' + (error.response?.data?.error || error.message));
    // 失败时也保持在当前类目
    const currentCategoryId = route.query.category_id;
    if (currentCategoryId) {
      await nextTick();
      router.push({
        path: '/admin/articles',
        query: { category_id: currentCategoryId }
      });
    }
  }
};

const handleNodeClick = (node) => {
  // 点击节点时的处理（如果需要）
};

// 扁平化分类列表（用于父分类选择，排除当前编辑的分类及其子分类）
const flatCategories = computed(() => {
  const flatten = (cats, excludeId = null) => {
    const result = [];
    for (const cat of cats) {
      if (cat.id !== excludeId) {
        result.push({
          id: cat.id,
          name: cat.name,
          title: cat.name
        });
        if (cat.children && cat.children.length > 0) {
          result.push(...flatten(cat.children, excludeId));
        }
      }
    }
    return result;
  };
  const excludeId = editingCategory.value?.id;
  return flatten(categories.value, excludeId);
});

// 博客分类管理功能
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
          parent_id: cat.parent_id || null,
          description: cat.description || '',
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
  const categoryId = node.id;
  if (!categoryId) return;
  
  const categoryName = node.name || node.title || '该分类';
  
  if (!confirm(`确定要删除分类「${categoryName}」吗？删除后相关文章的 category_id 将置为 NULL。`)) return;

  // 获取当前类目ID
  const currentCategoryId = route.query.category_id;
  
  try {
    // 博客分类通过删除API删除
    const response = await axios.delete(
      `${store.state.serverUrl}/api/v1/admin/blog-categories/${categoryId}`,
      {
        headers: {
          'Authorization': store.state.token
        }
      }
    );

    if (response.data?.success) {
      alert(`删除成功，已更新 ${response.data.data.updated_count} 篇文章`);
      await loadCategories();
      
      // 如果删除的是当前类目，则清除 category_id 参数，否则保持在当前类目
      await nextTick();
      if (currentCategoryId && parseInt(currentCategoryId) === categoryId) {
        router.push({
          path: '/admin/articles',
          query: {}
        });
      } else if (currentCategoryId) {
        router.push({
          path: '/admin/articles',
          query: { category_id: currentCategoryId }
        });
      }
    } else {
      alert(response.data?.error || '删除失败');
      // 失败时也保持在当前类目
      if (currentCategoryId) {
        await nextTick();
        router.push({
          path: '/admin/articles',
          query: { category_id: currentCategoryId }
        });
      }
    }
  } catch (error) {
    console.error('删除分类失败:', error);
    alert('删除失败: ' + (error.response?.data?.error || error.message));
    // 失败时也保持在当前类目
    if (currentCategoryId) {
      await nextTick();
      router.push({
        path: '/admin/articles',
        query: { category_id: currentCategoryId }
      });
    }
  }
};

const saveCategory = async (categoryData) => {
  try {
    let response;
    if (categoryData.id) {
      // 更新
      response = await axios.put(
        `${store.state.serverUrl}/api/v1/admin/blog-categories/${categoryData.id}`,
        categoryData,
        {
          headers: {
            'Authorization': store.state.token
          }
        }
      );
    } else {
      // 创建
      response = await axios.post(
        `${store.state.serverUrl}/api/v1/admin/blog-categories`,
        categoryData,
        {
          headers: {
            'Authorization': store.state.token
          }
        }
      );
    }

    // 获取当前类目ID，优先使用保存的分类ID，其次使用路由中的
    const currentCategoryId = route.query.category_id;
    const savedCategoryId = response.data?.data?.id;

    if (response.data?.success) {
      alert(categoryData.id ? '分类更新成功' : '分类创建成功');
      closeCategoryDialog();
      await loadCategories();
      
      // 保存后保持在当前类目，如果是新建则跳转到新分类
      await nextTick();
      router.push({
        path: '/admin/articles',
        query: { category_id: savedCategoryId || currentCategoryId || '' }
      });
    } else {
      alert(response.data?.error || '保存失败');
      // 失败时也保持在当前类目
      if (currentCategoryId) {
        await nextTick();
        router.push({
          path: '/admin/articles',
          query: { category_id: currentCategoryId }
        });
      }
    }
  } catch (error) {
    console.error('保存分类失败:', error);
    alert('保存失败: ' + (error.response?.data?.error || error.message));
    // 失败时也保持在当前类目
    const currentCategoryId = route.query.category_id;
    if (currentCategoryId) {
      await nextTick();
      router.push({
        path: '/admin/articles',
        query: { category_id: currentCategoryId }
      });
    }
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
.articles-manage {
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


