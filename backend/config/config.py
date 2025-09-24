import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger("rss_app")


load_dotenv()


class Config:
    # 基础配置
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "your-jwt-secret-key"

    REDIS_HOST = os.environ.get("REDIS_HOST") or "localhost"
    REDIS_PORT = os.environ.get("REDIS_PORT") or 6379
    REDIS_DB = os.environ.get("REDIS_DB") or 0
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
    REDIS_TIMEOUT = 3600  # 连接超时时间（秒）

    # 微信小程序配置
    WECHAT_APP_ID = os.environ.get("WECHAT_APP_ID") or "test_app_id"
    WECHAT_APP_SECRET = os.environ.get("WECHAT_APP_SECRET") or "test_secret"

    # Dify API配置
    API_URL = os.environ.get("DIFY_API_URL") or "test-dify-api-url"
    API_KEY = os.environ.get("DIFY_API_KEY") or "test-dify-api-key"
    SCHEDULE_INTERVAL = int(
        os.environ.get("SCHEDULE_INTERVAL", 3600)
    )  # 默认每1小时执行一次
    RSS_CONFIG = [
        {
            "url": "https://rsshub.rssforever.com/github/trending/daily/any",
            "name": "github_daily",
            "description": "GitHub每日热门",
        },
        {
            "url": "https://rsshub.rssforever.com/github/trending/weekly/any",
            "name": "github_weekly",
            "description": "GitHub每周热门",
        },
        {
            "url": "https://rsshub.rssforever.com/github/trending/monthly/any",
            "name": "github_monthly",
            "description": "GitHub每月热门",
        },
    ]

    # 服务器配置
    FLASK_HOST = os.environ.get("FLASK_HOST") or "0.0.0.0"
    FLASK_PORT = os.environ.get("FLASK_PORT") or 5000
    SERVER_URL = os.environ.get("SERVER_URL") or "http://localhost:5000"
    DEBUG = os.environ.get("DEBUG", "true").lower() in ("true", "1")

    # 日志配置
    LOG_DIR = "logs"
    LOG_FILE = "app.log"
    LOG_MAX_BYTES = 1024 * 1024 * 10  # 1MB
    LOG_BACKUP_COUNT = 10

    # 博客配置
    BLOG_DIR = os.environ.get("BLOG_DIR") or "/Users/ht/Documents/DS/blog"

    # 图片输出配置
    OUTPUT_IMAGES_DIR = os.environ.get("OUTPUT_IMAGES_DIR") or "output_images/mdTpng"

    UPLOAD_FOLDER = os.environ.get("UPLOAD_BACKPNG_FOLDER") or "output_images/uploads"
    OUTPUT_FOLDER = os.environ.get("OUTPUT_BACKPNG_FOLDER") or "output_images/processed"

    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")
    MINIO_SECURE = os.environ.get("MINIO_SECURE", "true").lower() in ("true", "1")
    CDN_DOMAIN = os.getenv("CDN_DOMAIN")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging import StreamHandler

        console_handler = StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)


class ProductionConfig(Config):
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging.handlers import RotatingFileHandler

        os.makedirs(cls.LOG_DIR, exist_ok=True)

        file_handler = RotatingFileHandler(
            os.path.join(cls.LOG_DIR, cls.LOG_FILE),
            maxBytes=cls.LOG_MAX_BYTES,
            backupCount=cls.LOG_BACKUP_COUNT,
        )
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        # 新增：配置Werkzeug访问日志
        werkzeug_logger = logging.getLogger("werkzeug")
        werkzeug_logger.addHandler(file_handler)
        werkzeug_logger.setLevel(logging.INFO)


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


# 根据环境变量选择配置
def get_config():
    env = os.getenv("FLASK_ENV", "development").lower()
    return config.get(env, config["default"])
