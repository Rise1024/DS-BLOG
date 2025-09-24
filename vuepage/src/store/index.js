import { createStore } from 'vuex';
import axios from 'axios';

const store = createStore({
  state() {
    return {
      serverUrl: 'http://localhost',
      // serverUrl: 'https://dongsheng.online/rssmd',
      // 临时存储从RSS传递到Editor的markdown内容
      tempMarkdownContent: ''
    }
  },
  mutations: {
    setTempMarkdownContent(state, content) {
      state.tempMarkdownContent = content;
    },
    clearTempMarkdownContent(state) {
      state.tempMarkdownContent = '';
    }
  },
  actions: {
    initializeInterceptors() {
      // 添加统一请求头
      axios.interceptors.request.use(config => {
        config.headers['X-Request-Source'] = 'web';
        return config;
      });
    }
  }
});

// 初始化拦截器
store.dispatch('initializeInterceptors');

export default store;