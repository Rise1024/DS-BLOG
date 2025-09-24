# mdTnpg 部署文档

## 1 系统依赖安装
```bash
# 更新系统包
 apt update && apt upgrade -y

# 安装基础开发工具和依赖
 apt install build-essential python3 python3-dev python3-venv -y

# 安装 Chrome 浏览器（用于 Playwright）
 apt install chromium-browser chromium-chromedriver -y
```

## 2. Python 环境配置

```bash
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 依赖
pip install playwright

python -m playwright install chromium


```

## 3 应用配置

### 3.1 环境变量配置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
vim .env
```

配置文件关键项说明：
```ini
# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password

# 微信小程序配置
WECHAT_APP_ID=<your_app_id>
WECHAT_APP_SECRET=<your_app_secret>

# 服务器配置
SERVER_URL=https://your-domain.com
```


## 4. 服务配置


### 4.1 Gunicorn 配置

```bash

pip install gunicorn

```
创建 `gunicorn.conf.py`：
```python
import multiprocessing

# 服务器配置
bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000

# 进程配置
pidfile = "/opt/backend/rss/gunicorn.pid"

# 日志配置
accesslog = "/opt/backend/rss/logs/access.log"
errorlog = "/opt/backend/rss/logs/error.log"
loglevel = "info"

# 工作目录
chdir = "/opt/backend/rss"

# 用户配置
user = "root"
group = "root"
```

### 4.2 Systemd 服务配置
创建服务文件 `/etc/systemd/system/rss.service`：
```ini
[Unit]
Description=RSS Markdown Converter

[Service]
User=root
Group=root
WorkingDirectory=/opt/backend/rss
Environment="PATH=/opt/backend/rss/myenv/bin"
ExecStart=/opt/backend/rss/myenv/bin/gunicorn -c gunicorn.conf.py app:app

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 4.3 启动服务
```bash
#重新加载systemd守护进程：
systemctl daemon-reload
# 启动并启用服务
systemctl start rss

systemctl enable rss
# 检查服务状态
systemctl status rss

```