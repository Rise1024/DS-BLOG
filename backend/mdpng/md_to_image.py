#!/usr/bin/env python3
import io
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minio import Minio, S3Error
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import os
import re
from config.config import logger, get_config as Config
from playwright.sync_api import sync_playwright
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from mdpng.html_templates import CoverTemplate, ContentTemplate
from mdpng.style_presets import STYLE_PRESETS

# 默认配置
CONFIG = {
    "image_size": {"width": 1080, "height": 1920},  # 图片的宽度和高度
    # "theme": STYLE_PRESETS["carbon"]["theme"]  # 默认使用Carbon风格
    # "theme": STYLE_PRESETS["notion"]["theme"]  # 默认使用Carbon风格
    "theme": STYLE_PRESETS["xiaohongshu"]["theme"],  # 默认使用Carbon风格
    "minio": {
        "endpoint": Config().MINIO_ENDPOINT,
        "access_key": Config().MINIO_ACCESS_KEY,
        "secret_key": Config().MINIO_SECRET_KEY,
        "bucket_name": Config().MINIO_BUCKET_NAME,
        "secure": Config().MINIO_SECURE,
    },
}


def parse_markdown(content):
    """解析Markdown文件为封面和多个主题片段"""

    # 查找文档中所有标题
    all_headers = re.findall(r"(#{1,6})\s+", content)
    if not all_headers:
        return content, [content] if content.strip() else []

    # 确定最高级别的标题（#号最少的）
    min_level = min(len(h) for h in all_headers)

    # 提取最高级别标题及其内容作为封面
    sections = re.split(f"(?=\n#{{{min_level}}}\s+)", content)
    cover = sections[0].strip() if sections else ""

    # 查找次高级别的标题
    next_level_headers = [h for h in all_headers if len(h) == min_level + 1]
    if not next_level_headers:
        # 如果没有次级标题，则按最高级标题分割
        content_sections = sections
    else:
        # 按次级标题分割内容
        content_sections = re.split(f"(?=\n#{{{min_level + 1}}}\s+)", content)

    return cover, [s.strip() for s in content_sections if s.strip()]


def md_to_images_file(filename, user_id, article_id, preview_mode=False):
    logger.info(f"开始解析Markdown文件: {filename}")
    with open(filename, "r") as f:
        content = f.read()
    logger.debug(f"成功读取文件内容，文件大小: {len(content)} 字节")
    md_to_images(content, user_id, article_id, preview_mode)


def md_to_images(content, user_id, article_id, preview_mode=False):
    """主转换函数"""
    logger.info("开始执行Markdown到图片的转换")

    # 检查配置项
    if "minio" not in CONFIG or "image_size" not in CONFIG:
        raise ValueError("配置文件中缺少必要的配置项：minio 或 image_size")

    cover, sections = parse_markdown(content)
    logger.info(f"解析完成，共获取到 {len(sections)} 个内容片段")

    # 使用 with 语句确保 Playwright 资源自动释放
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, args=["--allow-file-access-from-files"]
        )
        context = browser.new_context(viewport=CONFIG["image_size"], bypass_csp=True)
        page = context.new_page()

        try:
            logger.info("开始生成内容图片")
            sections_to_process = sections[:2] if preview_mode else sections
            image_urls = []
            for i, section in enumerate(sections_to_process):
                logger.debug(f"处理第 {i} 个内容片段")
                html = (
                    generate_cover_html(section) if i == 0 else generate_html(section)
                )
                logger.debug("生成HTML内容完成")

                try:
                    timeout = CONFIG.get("timeout", 60000)  # 默认60秒
                    page.set_content(html, timeout=timeout)
                    page.wait_for_load_state("networkidle", timeout=timeout)
                    page.wait_for_timeout(2000)  # 额外等待

                    # 动态调整页面高度
                    content_height = page.evaluate(
                        """() => {
                        const body = document.body;
                        const html = document.documentElement;
                        return Math.max(
                            body.scrollHeight, body.offsetHeight,
                            html.clientHeight, html.scrollHeight, html.offsetHeight
                        );
                    }"""
                    )

                    min_height = 800
                    max_height = CONFIG["image_size"]["height"]
                    adjusted_height = min(max(content_height, min_height), max_height)

                    page.set_viewport_size(
                        {
                            "width": CONFIG["image_size"]["width"],
                            "height": adjusted_height,
                        }
                    )

                    image_data = page.screenshot(full_page=True)
                    object_name = f"{user_id}/{article_id}/note_{i+1:02d}.png"

                    logger.info(f"开始上传第 {i+1} 张图片: {object_name}")
                    image_url = upload_to_minio(image_data, object_name)
                    image_urls.append(image_url)
                    logger.info(f"成功上传第 {i+1} 张图片到MinIO: {image_url}")
                except Exception as e:
                    logger.error(f"处理第 {i+1} 个片段时发生错误: {str(e)}")
                    continue
        finally:
            # 确保页面和上下文关闭（可选）
            page.close()
            context.close()

    logger.info("图片生成完成，浏览器已关闭")
    return image_urls


def generate_cover_html(content):
    """生成封面HTML"""
    md = MarkdownIt().use(footnote_plugin).use(tasklists_plugin)
    html_content = md.render(content)
    # 使用ContentTemplate生成HTML
    cover_template = CoverTemplate()
    return cover_template.generate(html_content, CONFIG)


def generate_html(content):
    # 添加图片路径处理
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 替换 Markdown 中的图片相对路径为绝对路径
    def replace_image_path(match):
        img_alt = match.group(1)
        img_path = match.group(2)
        if img_path.startswith("./"):
            img_path = img_path[2:]
        # 使用 data URL 方式嵌入图片
        abs_path = os.path.join(base_dir, img_path)
        if os.path.exists(abs_path):
            with open(abs_path, "rb") as img_file:
                import base64

                img_data = base64.b64encode(img_file.read()).decode("utf-8")
                img_ext = os.path.splitext(img_path)[1][1:]  # 获取文件扩展名（去掉点）
                return f"![{img_alt}](data:image/{img_ext};base64,{img_data})"
        return f"![{img_alt}]({img_path})"  # 如果文件不存在，保持原路径

    content = re.sub(r"!\[(.*?)\]\((\.?/?.*?)\)", replace_image_path, content)

    # 使用 MarkdownIt 渲染 Markdown
    md = MarkdownIt().use(footnote_plugin).use(tasklists_plugin)
    html_content = md.render(content)

    # 使用 Pygments 为代码块添加语法高亮
    def highlight_code(match):
        code = match.group(1)
        lexer = get_lexer_by_name("python", stripall=True)
        formatter = HtmlFormatter(style=CONFIG["theme"]["code_theme"])
        return highlight(code, lexer, formatter)

    html_content = re.sub(
        r"<pre><code>(.*?)</code></pre>", highlight_code, html_content, flags=re.DOTALL
    )

    formatter = HtmlFormatter(style=CONFIG["theme"]["code_theme"])
    css_code = formatter.get_style_defs(".highlight")

    # 使用ContentTemplate生成HTML
    content_template = ContentTemplate()
    return content_template.generate(html_content, CONFIG, css_code)


def upload_to_minio(image_data, object_name):
    """上传文件到MinIO"""
    client = Minio(
        CONFIG["minio"]["endpoint"],
        access_key=CONFIG["minio"]["access_key"],
        secret_key=CONFIG["minio"]["secret_key"],
        secure=CONFIG["minio"]["secure"],
    )

    try:
        # 确保存储桶存在
        if not client.bucket_exists(CONFIG["minio"]["bucket_name"]):
            client.make_bucket(CONFIG["minio"]["bucket_name"])

        # 使用字节流上传
        image_stream = io.BytesIO(image_data)
        image_stream.seek(0)

        client.put_object(
            CONFIG["minio"]["bucket_name"],
            object_name,
            image_stream,
            length=len(image_data),
            content_type="image/png",
        )
        return f"{object_name}"

    except S3Error as exc:
        logger.error(f"MinIO上传失败: {exc}")
        raise
