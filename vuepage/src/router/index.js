import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Editor from '../views/Editor.vue';
import RssPanel from '../views/RssPanel.vue';
import Blog from '../views/Blog/index.vue';
import BlogReader from '../views/BlogReader.vue';
import BlogArticle from '../views/Blog/Article.vue';
import BlogEditor from '../views/Blog/Editor.vue';

const routes = [
  {
    path: '/',
    name: 'RssPanel',
    component: RssPanel
  },
  
  {
    path: '/home',
    name: 'Home',
    component: Home
  },
  
  {
    path: '/editor',
    name: 'Editor',
    component: Editor
  },
  
  {
    path: '/blog',
    name: 'Blog',
    component: Blog
  },

  {
    path: '/blog/reader/:category',
    name: 'BlogReader',
    component: BlogReader
  },

  {
    path: '/blog/article/:id',
    name: 'BlogArticle',
    component: BlogArticle
  },
  
  {
    path: '/blog/editor',
    name: 'BlogEditor',
    component: BlogEditor
  },
  
  {
    path: '/blog/editor/:id',
    name: 'BlogEditorEdit',
    component: BlogEditor
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;