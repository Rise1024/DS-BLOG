# DS-BLOG

这是一个个人博客项目，支持 RSS 内容获取、多种样式主题、批量转换和在线预览、Markdown 转图片等功能。

## 🌟 项目特性

### 核心功能
- **RSS 内容获取**: 自动获取订阅的 RSS 内容并转换为图片
- **Markdown 转图片**: 将 Markdown 内容渲染为高质量 PNG 图片
- **多种样式主题**: 支持 Carbon、GitHub、Monokai、Dracula、Nord 等多种代码风格
- **批量处理**: 支持批量转换和下载多张图片
- **在线预览**: 实时预览转换效果
- **水印功能**: 支持自定义水印文本

### 多端支持
- **Web 前端**: 现代化的 Vue.js 单页应用
- **微信小程序**: 移动端便捷访问
- **后端 API**: 高性能 Python Flask 服务

## 🏗️ 项目架构

```
mdTnpg/
├── backend/          # Python Flask 后端服务
├── vuepage/          # Vue.js Web 前端
└── miniprogram/      # 微信小程序
```

## 🛠️ 技术栈

### 后端 (Python)
- **Flask**: Web 框架
- **Playwright**: 浏览器自动化，HTML 渲染
- **MarkdownIt**: Markdown 解析和渲染
- **Pygments**: 代码语法高亮
- **MinIO**: 对象存储服务
- **Redis**: 缓存和历史记录
- **SQLite**: 数据存储

### Web 前端 (Vue.js)
- **Vue 3**: 前端框架
- **Vuex**: 状态管理
- **Vue Router**: 路由管理
- **Axios**: HTTP 客户端
- **Markdown-it**: Markdown 渲染
- **Vite**: 构建工具

### 微信小程序
- **原生小程序框架**
- **Towxml**: Markdown 渲染组件
- **自定义组件**: 登录模态框、自定义提示等

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Redis
- MinIO (可选，用于图片存储)

### 后端部署

1. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

2. **配置环境**
```bash
# 复制并编辑配置文件
cp config/config.example.py config/config.py
```

3. **启动服务**
```bash
# 开发模式
python app.py

# 生产模式
gunicorn -c gunicorn.conf.py app:app
```

### Web 前端部署

1. **安装依赖**
```bash
cd vuepage
npm install
```

2. **配置后端地址**
```javascript
// src/store/index.js
const serverUrl = 'http://localhost:5000' // 修改为实际后端地址
```

3. **启动开发服务器**
```bash
npm run dev
```

4. **构建生产版本**
```bash
npm run build
```

### 微信小程序部署

1. **配置项目**
```bash
cd miniprogram
# 使用微信开发者工具打开项目
```

2. **修改配置**
```javascript
// app.js 中修改后端地址
const serverUrl = 'https://your-backend-domain.com'
```

3. **上传发布**
- 使用微信开发者工具上传代码
- 在微信公众平台发布

## 📖 使用指南

### Web 端使用

1. **RSS 内容获取**
   - 访问首页，选择 RSS 源
   - 查看渲染后的内容
   - 点击"一键生成图片"跳转到编辑器

2. **Markdown 编辑**
   - 在编辑器中输入或粘贴 Markdown 内容
   - 选择样式主题和水印设置
   - 点击"预览"查看效果
   - 点击"生成图片"创建最终图片

3. **图片下载**
   - 单张下载：点击图片下方的下载按钮
   - 批量下载：点击"一键下载全部"按钮

### 小程序使用

1. **登录授权**
   - 首次使用需要微信授权登录

2. **功能使用**
   - RSS 内容浏览
   - Markdown 转图片
   - 历史记录查看
   - 反馈提交

## 🔧 配置说明

### 后端配置 (config/config.py)

```python
# 服务器配置
SERVER_URL = "http://localhost:5000"
DEBUG = True

# MinIO 配置
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "your-access-key"
MINIO_SECRET_KEY = "your-secret-key"
MINIO_BUCKET_NAME = "mdpng"

# RSS 配置
RSS_CONFIG = [
    {
        "name": "示例RSS",
        "url": "https://example.com/rss",
        "description": "示例RSS源描述"
    }
]
```

### 前端配置

```javascript
// vuepage/src/store/index.js
const serverUrl = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend-domain.com' 
  : 'http://localhost:5000'
```

## 📁 项目结构

### 后端结构
```
backend/
├── app.py                 # 主应用入口
├── routes/                # API 路由
│   ├── mdpng.py          # 图片转换接口
│   ├── rss.py            # RSS 相关接口
│   └── admin.py          # 管理接口
├── mdpng/                # 核心转换模块
│   ├── md_to_image.py    # Markdown 转图片
│   ├── style_presets.py  # 样式预设
│   └── html_templates.py # HTML 模板
├── model/                # 数据模型
├── auth/                 # 认证模块
├── config/               # 配置文件
└── services/             # 业务服务
```

### 前端结构
```
vuepage/
├── src/
│   ├── views/            # 页面组件
│   │   ├── RssPanel.vue  # RSS 面板
│   │   ├── Editor.vue    # 编辑器
│   │   └── Home.vue      # 首页
│   ├── components/       # 通用组件
│   ├── store/            # 状态管理
│   └── router/           # 路由配置
├── public/               # 静态资源
└── package.json          # 依赖配置
```

## 🎨 设计系统

项目采用统一的设计系统，包含：

- **颜色系统**: 主色调、辅助色、语义色
- **字体系统**: 字体族、字号、字重
- **间距系统**: 统一的间距规范
- **组件规范**: 按钮、输入框、卡片等组件样式
- **响应式设计**: 支持多设备适配

详细设计规范请参考 `vuepage/DESIGN_SYSTEM.md`。

## 🔒 安全特性

- **用户认证**: 支持登录验证
- **API 限流**: 防止恶意请求
- **输入验证**: 严格的数据验证
- **错误处理**: 完善的异常处理机制

## 📊 性能优化

- **图片缓存**: MinIO 对象存储
- **异步处理**: 后台任务队列
- **前端优化**: 代码分割、懒加载
- **CDN 支持**: 静态资源加速

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目主页: [GitHub Repository](https://github.com/Rise1024/mdTnpg)
- 问题反馈: [Issues](https://github.com/Rise1024/mdTnpg/issues)
- 功能建议: [Discussions](https://github.com/Rise1024/mdTnpg/discussions)

## 🙏 致谢

感谢以下开源项目的支持：

- [Playwright](https://playwright.dev/) - 浏览器自动化
- [Markdown-it](https://markdown-it.github.io/) - Markdown 解析
- [Vue.js](https://vuejs.org/) - 前端框架
- [Flask](https://flask.palletsprojects.com/) - Web 框架

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！



