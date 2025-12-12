import { createStore } from 'vuex';
import axios from 'axios';

const store = createStore({
  state() {
    // 从 localStorage 读取主题设置，如果没有则使用系统偏好
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
    
    // 立即应用主题到 document
    if (initialTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    
    return {
      serverUrl: process.env.NODE_ENV === 'production' 
        ? 'https://dongsheng.online/rssmd' 
        : 'http://localhost/rssmd',
      token: localStorage.getItem('token') || null,
      userInfo: null,
      theme: initialTheme
    }
  },
  mutations: {
    setToken(state, token) {
      state.token = token;
      if (token) {
        localStorage.setItem('token', token);
      } else {
        localStorage.removeItem('token');
      }
    },
    setUserInfo(state, userInfo) {
      state.userInfo = userInfo;
    },
    setTheme(state, theme) {
      state.theme = theme;
      localStorage.setItem('theme', theme);
      // 应用主题到 document
      if (theme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  },
  actions: {
    initializeInterceptors({ commit }, router) {
      // 添加统一请求头
      axios.interceptors.request.use(config => {
        config.headers['X-Request-Source'] = 'web';
        // 如果存在 token，添加到请求头（从 localStorage 读取最新值）
        const token = localStorage.getItem('token');
        if (token) {
          config.headers['Authorization'] = token;
        }
        return config;
      });

      // 添加响应拦截器，处理 401 错误
      axios.interceptors.response.use(
        response => {
          // 正常响应，直接返回
          return response;
        },
        error => {
          // 处理错误响应
          if (error.response && error.response.status === 401) {
            // 清除 token 和用户信息
            commit('setToken', null);
            commit('setUserInfo', null);
            
            // 如果当前不在登录页，跳转到登录页
            if (router && router.currentRoute.value.path !== '/admin/login') {
              router.push({
                path: '/admin/login',
                query: { redirect: router.currentRoute.value.fullPath }
              });
            }
          }
          return Promise.reject(error);
        }
      );
    }
  }
});

export default store;