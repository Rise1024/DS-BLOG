import os
from flask import Flask
from config.config import get_config, logger
from model.models import init_redis  # 添加 Redis 连接导入
from auth.extensions import init_auth


app = Flask(__name__)

# 加载配置
cfg = get_config()
app.config.from_object(cfg)
# 日志配置
cfg.init_app(app)

# 初始化数据库
init_redis(app)

# 初始化认证工具
with app.app_context():
    init_auth()

# 注册蓝图
from routes.admin import admin_bp
from routes.mdpng import mdpng_bp
from routes.login import login_bp
from routes.rss import rss_bp
from routes.blog import blog_bp

app.register_blueprint(admin_bp)
app.register_blueprint(mdpng_bp)
app.register_blueprint(login_bp)
app.register_blueprint(rss_bp)
app.register_blueprint(blog_bp)


if __name__ == "__main__":
    # 生产环境安全设置
    if os.environ.get("FLASK_ENV") == "production":
        app.config.update(DEBUG=False)
    logger.info("启动应用...")
    app.run(
        host=app.config.get("FLASK_HOST", "0.0.0.0"),
        port=int(app.config.get("FLASK_PORT", 5000)),
        debug=app.config["DEBUG"],
    )
