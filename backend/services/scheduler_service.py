from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import SchedulerNotRunningError
from apscheduler.triggers.interval import IntervalTrigger
import requests
from config.config import logger


class SchedulerService:
    def __init__(self, config):
        self.scheduler = BackgroundScheduler(daemon=False)
        self.config = config
        self._setup_tasks()

    def _setup_tasks(self):
        rss_configs = self.config.RSS_CONFIG
        for config in rss_configs:
            self._add_rss_task(config["url"], config["name"])

    def _add_rss_task(self, rss_url, rss_name):
        def task_wrapper():
            logger.info(f"开始执行RSS任务: {rss_name}")  # 新增日志
            try:
                headers = {
                    "Authorization": f"Bearer {self.config.API_KEY}",
                    "Content-Type": "application/json",
                }
                data = {
                    "inputs": {"rssUrl": rss_url, "rssName": rss_name},
                    "response_mode": "blocking",
                    "user": "ds1",
                }
                response = requests.post(
                    self.config.API_URL, headers=headers, json=data
                )
                response.raise_for_status()
                logger.info(f"成功执行RSS任务: {rss_name}")
            except Exception as e:
                logger.error(f"RSS任务执行失败: {rss_name}, 错误: {str(e)}")

        self.scheduler.add_job(
            func=task_wrapper,
            trigger=IntervalTrigger(seconds=self.config.SCHEDULE_INTERVAL),
            id=f"rss_task_{rss_name}",
            max_instances=1,  # 关键参数：同一任务最多1个实例
            misfire_grace_time=5,  # 关键参数：超时立即放弃
        )

    def start(self):
        self.scheduler.start()
        logger.info("RSS定时调度器已启动")
        logger.info(f"当前活跃任务数: {len(self.scheduler.get_jobs())}")

    def shutdown(self):
        if self.scheduler.running:
            try:
                logger.info("正在关闭调度器...")
                # 修改关闭逻辑，添加 wait=False 参数
                self.scheduler.shutdown(wait=False)
                logger.info("调度器已安全关闭")
            except SchedulerNotRunningError:
                pass
