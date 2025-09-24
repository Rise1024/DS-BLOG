# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from config.config import logger
from config.config import get_config as Config
import requests
from concurrent.futures import ThreadPoolExecutor
from model.models import Rss


# 创建蓝图
rss_bp = Blueprint("rss", __name__)

executor = ThreadPoolExecutor(max_workers=5)


def _execute_rss_task(config):
    try:
        headers = {
            "Authorization": f"Bearer {Config().API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "inputs": {"rssUrl": config["url"], "rssName": config["name"]},
            "response_mode": "blocking",
            "user": "ds1",
        }
        response = requests.post(Config().API_URL, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f'手动执行RSS任务成功: {config["name"]}')
        return True
    except Exception as e:
        logger.error(f'手动执行RSS任务失败: {config["name"]}, 错误: {str(e)}')
        return False


@rss_bp.route("/trigger-rss", methods=["POST"])
def trigger_rss():
    # 获取所有RSS配置
    rss_configs = Config().RSS_CONFIG

    # 提交异步任务
    futures = [executor.submit(_execute_rss_task, config) for config in rss_configs]
    results = [f.result() for f in futures]

    success_count = sum(results)
    return (
        jsonify(
            {
                "message": "任务已触发",
                "total_tasks": len(results),
                "success_count": success_count,
                "failure_count": len(results) - success_count,
            }
        ),
        200,
    )


@rss_bp.route("/rss", methods=["GET"])
def get_data():
    try:
        rss_configs = Config().RSS_CONFIG
        logger.info("RSS配置数据获取成功")
        return jsonify(rss_configs), 200
    except Exception as e:
        logger.error(f"数据获取失败: {str(e)}")
        return jsonify({"error": "数据获取失败"}), 500


@rss_bp.route("/rss/<rssName>", methods=["GET"])
def get_rss_data(rssName):
    try:
        data = Rss.get_rss_data(rssName)
        if data:
            return data, 200
        else:
            logger.error(f"未找到RSS数据: {rssName}")
            return "未找到数据", 404
    except Exception as e:
        logger.error(f"获取RSS数据失败: {rssName}, 错误: {str(e)}")
        return "服务器错误", 500
