<template>
  <div class="rss-container">
    <div class="rss-card">
      <!-- RSS源选择卡片 -->
      <div class="rss-selector">
        <h3 class="selector-title">选择RSS源</h3>
        <div class="rss-cards-grid">
          <div
            v-for="item in rssData"
            :key="item.name"
            class="rss-card-item"
            :class="{ 'active': selectedRssName === item.name }"
            @click="selectRssSource(item.name)"
          >
            <div class="rss-card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 11a9 9 0 0 1 9 9"/>
                <path d="M4 4a16 16 0 0 1 16 16"/>
                <circle cx="5" cy="19" r="1"/>
              </svg>
            </div>

            <div class="rss-card-content">
              <p class="rss-card-description">{{ item.description || item.name }}</p>
            </div>

            <div class="rss-card-indicator" v-if="selectedRssName === item.name">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M20.285 2l-11.285 11.567-5.286-5.011-3.714 3.716 9 8.728 15-15.285z"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="loading" class="loading-info">
        数据加载中...
      </div>
      
      <div v-else>
        <div v-if="!rssData.length" class="empty-tip">
          暂无订阅数据
        </div>
      </div>
      
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
      
      <div v-if="contentLoading" class="loading-info">
        内容加载中...
      </div>
      
      <div v-else-if="parsedContent" class="content-section">
        <!-- 小按钮放在右上方 -->
        <button @click="shareToEditor" class="compact-share-btn">
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
            <circle cx="12" cy="13" r="3"/>
          </svg>
          生成图片
        </button>

        <div class="content-preview" v-html="parsedContent"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import axios from 'axios';
import MarkdownIt from 'markdown-it';
import markdownItLinkAttributes from 'markdown-it-link-attributes';

const store = useStore();
const router = useRouter();
const rssData = ref([]);
const selectedRssName = ref('');
const loading = ref(false);
const contentLoading = ref(false);
const errorMessage = ref('');
const parsedContent = ref('');
const rawMarkdownContent = ref(''); // 存储原始的markdown内容

// 初始化 markdown-it
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
}).use(markdownItLinkAttributes, {
  attrs: {
    target: '_blank',
    rel: 'noopener'
  }
});

const loadRssData = async () => {
  loading.value = true;
  errorMessage.value = '';
  
  try {
    const response = await axios.get(`${store.state.serverUrl}/rss`);
    
    // 后端直接返回RSS配置数组，不是success格式
    if (response.data && Array.isArray(response.data)) {
      rssData.value = response.data;
      if (rssData.value.length > 0) {
        selectedRssName.value = rssData.value[0].name;
        await loadRssContent();
      }
    } else {
      errorMessage.value = 'RSS配置数据格式错误';
    }
  } catch (error) {
    console.error('加载RSS列表失败:', error);
    errorMessage.value = error.response?.data?.error || '加载RSS列表失败';
  } finally {
    loading.value = false;
  }
};

const loadRssContent = async () => {
  if (!selectedRssName.value) return;
  
  contentLoading.value = true;
  errorMessage.value = '';
  
  try {
    // 后端接口是 /rss/<rssName>，直接返回内容
    const response = await axios.get(`${store.state.serverUrl}/rss/${selectedRssName.value}`);
    
    // 后端直接返回内容，不是success格式
    if (response.data) {
      // 保存原始markdown内容
      rawMarkdownContent.value = response.data;
      // 使用 markdown-it 将 markdown 转换为 HTML
      parsedContent.value = md.render(response.data);
    } else {
      errorMessage.value = '未找到RSS内容';
    }
  } catch (error) {
    console.error('加载RSS内容失败:', error);
    if (error.response?.status === 404) {
      errorMessage.value = '未找到RSS内容';
    } else {
      errorMessage.value = error.response?.data || '加载RSS内容失败';
    }
  } finally {
    contentLoading.value = false;
  }
};

const selectRssSource = async (rssName) => {
  if (selectedRssName.value !== rssName) {
    selectedRssName.value = rssName;
    await loadRssContent();
  }
};

const shareToEditor = () => {
  if (rawMarkdownContent.value) {
    // 将markdown内容存储到store
    store.commit('setTempMarkdownContent', rawMarkdownContent.value);
    // 跳转到Editor页面
    router.push('/editor');
  } else {
    alert('没有可分享的内容');
  }
};

onMounted(() => {
  loadRssData();
});
</script>

<style scoped>
.rss-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.rss-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  padding: 2.5rem 2rem 2rem 2rem;
  max-width: 700px;
  width: 100%;
}

.rss-selector {
  margin-bottom: 2rem;
}

.selector-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3a4a;
  margin-bottom: 1.5rem;
  text-align: center;
}

.rss-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
}

.rss-card-item {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.rss-card-item:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.rss-card-item.active {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border-color: #4f8cff;
  box-shadow: 0 4px 20px rgba(79, 140, 255, 0.15);
}

.rss-card-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #4f8cff 0%, #357ae8 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.rss-card-icon svg {
  width: 16px;
  height: 16px;
}

.rss-card-content {
  flex: 1;
  min-width: 0;
}

.rss-card-description {
  font-size: 0.9rem;
  font-weight: 500;
  color: #1e293b;
  margin: 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.rss-card-indicator {
  width: 24px;
  height: 24px;
  color: #4f8cff;
  flex-shrink: 0;
}

.rss-card-indicator svg {
  width: 100%;
  height: 100%;
}

.loading-info,
.empty-tip {
  padding: 2rem;
  text-align: center;
  color: #666;
  font-size: 1.1rem;
}

.error-message {
  color: #ff4d4f;
  padding: 1rem;
  margin-top: 1rem;
  background: #fff1f0;
  border-radius: 8px;
  font-size: 1rem;
}

.content-section {
  margin-top: 2rem;
  position: relative;
}

/* 紧凑的右上角按钮 */
.compact-share-btn {
  position: absolute;
  top: 0;
  right: 0;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.8rem;
  font-weight: 500;
  border-radius: 6px;
  background: linear-gradient(135deg, #4f8cff 0%, #357ae8 100%);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 6px rgba(79, 140, 255, 0.25);
  z-index: 5;
}

.compact-share-btn:hover {
  background: linear-gradient(135deg, #357ae8 0%, #2563eb 100%);
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(79, 140, 255, 0.35);
}

.compact-share-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(79, 140, 255, 0.25);
}

.btn-icon {
  width: 0.9em;
  height: 0.9em;
}

.content-preview {
  margin: 0 auto;
  padding: 3rem 0.5rem 0.5rem 0.5rem;
  font-size: 1.08rem;
  color: #222;
  line-height: 1.7;
}

.content-preview :deep(h1),
.content-preview :deep(h2),
.content-preview :deep(h3) {
  color: #2d3a4a;
  margin: 1.5em 0 0.5em;
  font-weight: 600;
}

.content-preview :deep(p) {
  line-height: 1.7;
  margin-bottom: 1em;
}

.content-preview :deep(a) {
  color: #4f8cff;
  text-decoration: underline;
  transition: color 0.2s;
}
.content-preview :deep(a:hover) {
  color: #357ae8;
}

.content-preview :deep(code) {
  background-color: #f6f8fa;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.98em;
}

.content-preview :deep(pre) {
  background-color: #f6f8fa;
  padding: 1em;
  overflow: auto;
  border-radius: 8px;
  margin: 1em 0;
  font-size: 0.98em;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .rss-card {
    padding: 1.5rem 1rem;
    margin: 1rem;
  }

  .selector-title {
    font-size: 1.1rem;
  }

  .rss-cards-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .rss-card-item {
    padding: 0.75rem;
    flex-direction: row;
    text-align: left;
    gap: 0.5rem;
  }

  .rss-card-content {
    text-align: left;
  }

  .rss-card-indicator {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    width: 20px;
    height: 20px;
  }
}

@media (max-width: 480px) {
  .rss-card {
    margin: 0.5rem;
    padding: 1rem 0.75rem;
  }

  .rss-card-item {
    padding: 0.75rem;
  }

  .rss-card-icon {
    width: 28px;
    height: 28px;
  }

  .rss-card-icon svg {
    width: 14px;
    height: 14px;
  }

  .compact-share-btn {
    position: static;
    margin-bottom: 1rem;
    align-self: flex-end;
  }

  .content-preview {
    padding: 1rem 0.5rem 0.5rem 0.5rem;
  }
}
</style>