import os
import time
from config.config import get_config, logger
from services.scheduler_service import SchedulerService

# 加载配置
cfg = get_config()

# 初始化日志
cfg.init_app(None)  # 传递None避免Flask依赖
logger.info("独立调度器启动")

# 创建调度器实例
scheduler = SchedulerService(config=cfg)

if __name__ == "__main__":
    # 生产环境设置
    if os.environ.get("FLASK_ENV") == "production":
        logger.info("生产环境配置生效")

    logger.info("启动调度任务...")
    try:
        scheduler.start()
        logger.info("调度器已成功启动")
        while True:
            try:
                time.sleep(86400)  # 永久阻塞直到信号中断
            except KeyboardInterrupt:
                break
    finally:
        scheduler.shutdown()
        logger.info("调度器已安全停止")
