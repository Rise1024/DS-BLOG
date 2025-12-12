import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import store from './store'

// 初始化主题
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
  document.documentElement.classList.add('dark');
} else if (savedTheme === 'light') {
  document.documentElement.classList.remove('dark');
} else {
  // 如果没有保存的主题，使用系统偏好
  const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  if (systemPrefersDark) {
    document.documentElement.classList.add('dark');
  }
}

const app = createApp(App);
app.use(router);
app.use(store);

// 初始化 axios 拦截器（需要传入 router）
store.dispatch('initializeInterceptors', router);

app.mount('#app');