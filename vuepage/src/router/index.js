import { createRouter, createWebHistory } from 'vue-router';
import store from '../store';
import Blog from '../views/Blog/index.vue';
import BlogReader from '../views/BlogReader.vue';
import BlogArticle from '../views/Blog/Article.vue';
import BlogEditor from '../views/Blog/Editor.vue';
import QuestionBank from '../views/QuestionBank/index.vue';
import QuestionList from '../views/QuestionBank/QuestionList.vue';
import QuestionDetail from '../views/QuestionBank/QuestionDetail.vue';
import Admin from '../views/Admin/index.vue';
import AdminLogin from '../views/Admin/Login.vue';
import AdminQuestions from '../views/Admin/Questions.vue';
import AdminQuestionEditor from '../views/Admin/QuestionEditor.vue';
import AdminArticles from '../views/Admin/Articles.vue';
import AdminCategories from '../views/Admin/Categories.vue';
import AdminTags from '../views/Admin/Tags.vue';
import AdminBlogCategories from '../views/Admin/BlogCategories.vue';

const routes = [
  {
    path: '/',
    name: 'QuestionBank',
    component: QuestionBank
  },
  
  {
    path: '/question-bank',
    name: 'QuestionBankHome',
    component: QuestionBank
  },
  
  {
    path: '/question-bank/category/:categoryId',
    name: 'QuestionList',
    component: QuestionList
  },
  
  {
    path: '/question-bank/question/:id',
    name: 'QuestionDetail',
    component: QuestionDetail
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

  // 管理后台登录
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLogin
  },

  // 管理后台路由
  {
    path: '/admin',
    component: Admin,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/admin/questions'
      },
      {
        path: 'questions',
        name: 'AdminQuestions',
        component: AdminQuestions
      },
      {
        path: 'questions/new',
        name: 'AdminQuestionNew',
        component: AdminQuestionEditor
      },
      {
        path: 'questions/edit/:id',
        name: 'AdminQuestionEdit',
        component: AdminQuestionEditor
      },
      {
        path: 'categories',
        name: 'AdminCategories',
        component: AdminCategories
      },
      {
        path: 'articles',
        name: 'AdminArticles',
        component: AdminArticles
      },
      {
        path: 'articles/new',
        name: 'AdminArticleNew',
        component: BlogEditor
      },
      {
        path: 'articles/edit/:id',
        name: 'AdminArticleEdit',
        component: BlogEditor
      },
      {
        path: 'tags',
        name: 'AdminTags',
        component: AdminTags
      },
      {
        path: 'blog-categories',
        name: 'AdminBlogCategories',
        component: AdminBlogCategories
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 全局路由守卫
router.beforeEach((to, from, next) => {
  // 检查是否需要登录
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查是否有 token
    if (!store.state.token) {
      // 未登录，跳转到登录页
      next({
        path: '/admin/login',
        query: { redirect: to.fullPath }
      });
    } else {
      // 已登录，允许访问
      next();
    }
  } else {
    // 不需要登录的页面，直接访问
    next();
  }
});

export default router;