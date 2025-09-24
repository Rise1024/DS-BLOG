import datetime
import io
import json
from flask import (
    Blueprint,
    abort,
    current_app,
    request,
    jsonify,
    send_file,
    send_from_directory,
)
from minio import Minio, S3Error
from auth.auth_utils import login_required
from mdpng.md_to_image import md_to_images, CONFIG, STYLE_PRESETS
import os
from config.config import logger
from model.models import Feedback, HistoryRecord, UserStatistics

# 创建蓝图
mdpng_bp = Blueprint("mdpng", __name__)


@mdpng_bp.route("/preview", methods=["POST"])
@login_required
def preview_markdown():
    try:
        logger.info("接收到新的预览请求")
        # 获取上传的Markdown内容和样式
        markdown_content = request.json.get("content")
        style = request.json.get("style", "carbon")
        watermark = request.json.get("watermark")  # 获取水印文本

        if not markdown_content:
            logger.warning("请求中未提供Markdown内容")
            return jsonify({"error": "未提供Markdown内容"}), 400

        # 验证样式是否有效
        if style not in STYLE_PRESETS:
            logger.warning(f"请求中提供了无效的样式: {style}")
            return jsonify({"error": "无效的样式选择"}), 400

        logger.info(f"使用样式 {style} 开始处理预览请求")

        # 设置选择的样式
        CONFIG["theme"] = STYLE_PRESETS[style]["theme"].copy()  # 创建主题配置的副本

        # 如果提供了自定义水印，则更新水印配置
        if watermark:
            CONFIG["theme"]["watermark"] = watermark
            logger.info(f"使用自定义水印: {watermark}")

        # 获取用户ID和文章标识
        user_id = str(request.json.get("user_id", "anonymous"))
        article_id = request.json.get(
            "article_id", str(datetime.datetime.now(datetime.timezone.utc).timestamp())
        )

        # 执行转换并获取MinIO URLs
        image_urls = md_to_images(markdown_content, user_id, article_id, True)

        if not image_urls:
            return jsonify({"error": "预览图片生成失败"}), 500

        # 构建预览图片URL
        host_image_urls = [
            f'{current_app.config["SERVER_URL"]}/files/{image_file}'
            for image_file in image_urls
        ]

        logger.info(f"转换完成，生成了 {len(host_image_urls)} 张预览图片")
        return jsonify({"success": True, "images": host_image_urls})

    except Exception as e:
        logger.error(f"预览过程中发生错误: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@mdpng_bp.route("/convert", methods=["POST"])
@login_required
def convert_markdown():
    try:
        logger.info("接收到新的转换请求")
        # 获取上传的Markdown内容和样式
        markdown_content = request.json.get("content")
        style = request.json.get("style", "carbon")
        watermark = request.json.get("watermark")  # 获取水印文本

        if not markdown_content:
            logger.warning("请求中未提供Markdown内容")
            return jsonify({"error": "未提供Markdown内容"}), 400

        # 验证样式是否有效
        if style not in STYLE_PRESETS:
            logger.warning(f"请求中提供了无效的样式: {style}")
            return jsonify({"error": "无效的样式选择"}), 400

        logger.info(f"使用样式 {style} 开始处理转换请求")

        # 设置选择的样式
        CONFIG["theme"] = STYLE_PRESETS[style]["theme"].copy()  # 创建主题配置的副本

        # 如果提供了自定义水印，则更新水印配置
        if watermark:
            CONFIG["theme"]["watermark"] = watermark
            logger.info(f"使用自定义水印: {watermark}")

        # 生成时间戳作为article_id
        user_id = str(request.json.get("user_id", "anonymous"))
        article_id = request.json.get(
            "article_id", str(datetime.datetime.now(datetime.timezone.utc).timestamp())
        )
        # 记录开始时间
        start_time = datetime.datetime.now(datetime.timezone.utc)

        image_urls = md_to_images(markdown_content, user_id, article_id, False)
        # 计算生成时间
        end_time = datetime.datetime.now(datetime.timezone.utc)
        generation_time = (end_time - start_time).total_seconds()
        logger.info(f"图片生成完成，耗时: {generation_time:.2f}秒")

        if not image_urls:
            return jsonify({"error": "图片生成失败"}), 500

        # 构建预览图片URL
        host_image_urls = [
            f'{current_app.config["SERVER_URL"]}/files/{image_file}'
            for image_file in image_urls
        ]

        # 保存记录到Redis
        history_id = HistoryRecord.create(
            user_id=user_id,
            article_id=article_id,
            style=style,
            image_urls=host_image_urls,
        )

        # 更新统计数��
        today = datetime.datetime.utcnow().date()
        stats_data = {
            "total_generations": 1,
            "total_images": len(host_image_urls),
            "active_users": 1,  # 需要额外实现活跃用户统计逻辑
        }
        UserStatistics.update_stats(today, stats_data)

        logger.info(f"转换完成，生成了 {len(host_image_urls)} 张图片")
        return jsonify(
            {"success": True, "images": host_image_urls, "article_id": article_id}
        )

    except Exception as e:
        logger.error(f"转换过程中发生错误: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@mdpng_bp.route("/files/<path:filepath>")
def serve_image(filepath):
    try:
        # 初始化MinIO客户端
        client = Minio(
            current_app.config["MINIO_ENDPOINT"],
            access_key=current_app.config["MINIO_ACCESS_KEY"],
            secret_key=current_app.config["MINIO_SECRET_KEY"],
            secure=current_app.config["MINIO_SECURE"],
        )

        # 从MinIO获取文件
        response = client.get_object(current_app.config["MINIO_BUCKET_NAME"], filepath)
        image_data = io.BytesIO(response.data)

        # 返回图片数据
        return send_file(image_data, mimetype="image/png", as_attachment=False)
    except S3Error as e:
        logger.error(f"MinIO文件获取失败: {str(e)}")
        abort(404)
    finally:
        response.close()
        response.release_conn()


@mdpng_bp.route("/api/history", methods=["POST"])
@login_required
def get_history():
    try:
        user_id = request.json.get("userId")
        # 从Redis获取历史记录
        records = HistoryRecord.get_user_history(user_id)

        grouped_records = {}
        for record in records:
            # 转换Redis返回的字符串类型值
            article_id = record["article_id"]
            created_at = datetime.datetime.fromisoformat(record["created_at"])

            if article_id not in grouped_records:
                grouped_records[article_id] = {
                    "article_id": article_id,
                    "created_at": created_at.strftime("%Y年%m月%d日%H时%M分%S秒"),
                    "style": record["style"],
                    "image_urls": json.loads(record["image_urls"]),  # 解析JSON字符串
                }

        return jsonify({"success": True, "data": list(grouped_records.values())})
    except Exception as e:
        logger.error(f"获取历史记录失败: {str(e)}")
        return jsonify({"success": False, "error": "获取历史记录失败"}), 500


@mdpng_bp.route("/api/feedback", methods=["POST"])
@login_required
def submit_feedback():
    try:
        user_id = request.json.get("userId")
        content = request.json.get("content")
        contact = request.json.get(
            "contact",
        )

        if not content:
            return jsonify({"success": False, "error": "反馈内容不能为空"}), 400

        # 创建反馈记录
        Feedback.create(user_id, content, contact)

        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"提交反馈失败: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "提交反馈失败"}), 500
