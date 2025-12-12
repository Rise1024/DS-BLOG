import os
from flask import Flask
from config.config import get_config, logger
from model.models import init_redis  # Redis连接（用于缓存）
from model.init_db import init_database  # SQLite数据库初始化
from auth.extensions import init_auth


app = Flask(__name__)

# 加载配置
cfg = get_config()
app.config.from_object(cfg)
# 日志配置
cfg.init_app(app)

# 初始化Redis（用于缓存）
init_redis(app)

# 初始化SQLite数据库
init_database(app)

# 初始化认证工具
with app.app_context():
    init_auth()

# 注册蓝图
from routes.admin import admin_bp
from routes.login import login_bp
from routes.blog import blog_bp
from routes.question_bank import question_bank_bp
from routes.mermaid import mermaid_bp
from routes.feedback import feedback_bp

app.register_blueprint(admin_bp)
app.register_blueprint(login_bp)
app.register_blueprint(blog_bp)
app.register_blueprint(question_bank_bp)
app.register_blueprint(mermaid_bp)
app.register_blueprint(feedback_bp)


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
