<template>
  <div v-if="show" class="dialog-overlay" @click="handleOverlayClick">
    <div class="dialog-content" @click.stop>
      <div class="dialog-header">
        <h3>{{ editingCategory ? '编辑分类' : '新建分类' }}</h3>
        <button @click="close" class="close-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
      
      <div class="dialog-body">
        <div class="form-group">
          <label>分类名称 <span class="required">*</span></label>
          <input 
            v-model="formData.name" 
            type="text" 
            placeholder="请输入分类名称"
            class="form-input"
          />
        </div>
        
        <div class="form-group" v-if="parentCategories.length > 0">
          <label>父分类</label>
          <select v-model="formData.parent_id" class="form-select">
            <option :value="null">无（主分类）</option>
            <option 
              v-for="cat in parentCategories" 
              :key="cat.id || cat.name" 
              :value="cat.id"
            >
              {{ cat.name || cat.title }}
            </option>
          </select>
        </div>
        
        <div class="form-group">
          <label>描述</label>
          <textarea 
            v-model="formData.description" 
            placeholder="请输入分类描述（可选）"
            class="form-textarea"
            rows="3"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>排序</label>
          <input 
            v-model.number="formData.order" 
            type="number" 
            placeholder="0"
            class="form-input"
            min="0"
          />
        </div>
      </div>
      
      <div class="dialog-footer">
        <button @click="close" class="btn btn-secondary">取消</button>
        <button @click="save" class="btn btn-primary">保存</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  category: {
    type: Object,
    default: null
  },
  parentCategories: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['close', 'save']);

const formData = ref({
  id: null,
  name: '',
  parent_id: null,
  description: '',
  order: 0
});

watch(() => props.show, (newVal) => {
  if (newVal && props.category) {
    formData.value = {
      id: props.category.id || null,
      name: props.category.name || props.category.title || '',
      parent_id: props.category.parent_id || null,
      description: props.category.description || '',
      order: props.category.order || 0
    };
  } else if (newVal && !props.category) {
    formData.value = {
      id: null,
      name: '',
      parent_id: null,
      description: '',
      order: 0
    };
  }
});

const close = () => {
  emit('close');
};

const save = () => {
  if (!formData.value.name.trim()) {
    alert('请输入分类名称');
    return;
  }
  emit('save', { ...formData.value });
};

const handleOverlayClick = (e) => {
  if (e.target === e.currentTarget) {
    close();
  }
};
</script>

<style scoped>
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
}

.dialog-content {
  background: var(--color-bg-primary, #ffffff);
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
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

.close-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary, #6b7280);
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--color-bg-secondary, #f3f4f6);
  color: var(--color-text-primary, #1f2937);
}

.dialog-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary, #1f2937);
}

.required {
  color: #dc2626;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border-primary, #e5e7eb);
  border-radius: 6px;
  font-size: 14px;
  color: var(--color-text-primary, #1f2937);
  background: var(--color-bg-primary, #ffffff);
  transition: all 0.2s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: var(--primary-600, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--color-border-primary, #e5e7eb);
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: var(--color-bg-secondary, #f3f4f6);
  color: var(--color-text-primary, #1f2937);
}

.btn-secondary:hover {
  background: var(--color-bg-muted, #e5e7eb);
}

.btn-primary {
  background: var(--primary-600, #2563eb);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-700, #1d4ed8);
}
</style>

