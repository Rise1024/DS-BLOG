"""
博客相关API路由（数据库版本）
"""
from flask import Blueprint, request, jsonify, current_app
from model.database import db, Article, Tag, ArticleQuestionRelation, Question, BlogCategory
from model.blog_cache import get_cache
from config.config import logger
import markdown
import re
import hashlib
import math
from markdown.extensions import toc, codehilite, tables, fenced_code

blog_bp = Blueprint("blog", __name__, url_prefix="/api/v1/blog")


def convert_markdown_to_html(content):
    """将markdown转换为HTML"""
    # 处理Mermaid代码块
    content = process_mermaid_blocks(content)

    md = markdown.Markdown(
        extensions=["toc", "codehilite", "tables", "fenced_code", "attr_list"],
        extension_configs={"toc": {"permalink": True, "permalink_title": "永久链接"}},
    )

    html_content = md.convert(content)

    # 处理文章内部链接
    html_content = process_article_links(html_content)

    return html_content


def process_mermaid_blocks(content):
    """处理Mermaid代码块，将其转换为HTML div"""
    pattern = r"```mermaid\s*\n(.*?)```"

    def replace_mermaid(match):
        mermaid_code = match.group(1).strip()
        mermaid_id = hashlib.md5(mermaid_code.encode()).hexdigest()[:8]
        return f'<div class="mermaid" id="mermaid-{mermaid_id}">\n{mermaid_code}\n</div>'

    return re.sub(pattern, replace_mermaid, content, flags=re.DOTALL)


def process_article_links(html_content):
    """处理HTML中的文章内部链接"""
    def replace_link_href(match):
        a_tag = match.group(0)
        href_match = re.search(r'href="([^"]*)"', a_tag)
        if href_match:
            href = href_match.group(1)
            
            # 处理内部文章链接（格式：/blog/article/{id}）
            if href.startswith('/blog/article/') or href.startswith('article/'):
                article_id = href.split('/')[-1]
                new_a_tag = a_tag.replace(
                    f'href="{href}"',
                    f'href="#" data-article-id="{article_id}" class="internal-article-link"'
                )
                return new_a_tag
        
        return a_tag

    html_content = re.sub(r"<a[^>]*>", replace_link_href, html_content)
    return html_content


def extract_headings_from_html(html_content):
    """从HTML内容中提取标题信息"""
    headings = []
    pattern = r'<h([1-6])[^>]*id="([^"]*)"[^>]*>(.*?)</h[1-6]>'
    matches = re.findall(pattern, html_content, re.DOTALL)
    
    for match in matches:
        level = int(match[0])
        anchor_id = match[1]
        title_html = match[2]
        title_text = re.sub(r"<a[^>]*>.*?</a>", "", title_html).strip()
        
        headings.append({
            "level": level,
            "title": title_text,
            "anchor": anchor_id,
            "line": 0
        })
    
    return headings


@blog_bp.route("/categories", methods=["GET"])
def get_categories():
    """获取所有分类（基于新的树形结构）"""
    try:
        cache = get_cache()
        cache_key = "blog:categories"
        clear_cache = request.args.get("clear_cache", "false").lower() == "true"
        
        if clear_cache:
            cache.delete(cache_key)
            logger.info("已清除分类缓存")
        
        cached_data = cache.get(cache_key)
        if cached_data and not clear_cache:
            logger.info("从缓存获取分类列表")
            return jsonify({"success": True, "data": cached_data, "cached": True})

        # 从 blog_categories 表获取所有分类（树形结构）
        all_categories = BlogCategory.query.order_by(BlogCategory.order, BlogCategory.id).all()
        
        # 构建分类字典
        category_dict = {}
        root_categories = []
        
        # 第一遍：创建所有分类节点
        for cat in all_categories:
            category_dict[cat.id] = {
                'id': cat.id,
                'name': cat.name,
                'description': cat.description,
                'order': cat.order,
                'parent_id': cat.parent_id,
                'children': [],
                'items': [],
                'count': 0
            }
        
        # 第二遍：建立父子关系
        for cat in all_categories:
            cat_data = category_dict[cat.id]
            if cat.parent_id is None:
                root_categories.append(cat_data)
            else:
                if cat.parent_id in category_dict:
                    category_dict[cat.parent_id]['children'].append(cat_data)
                else:
                    logger.warning(f"分类 {cat.id} 的父分类 {cat.parent_id} 不存在")
        
        # 第三遍：统计文章数量并添加文章列表
        articles = Article.query.all()
        for article in articles:
            if article.category_id and article.category_id in category_dict:
                cat_data = category_dict[article.category_id]
                cat_data['count'] += 1
                cat_data['items'].append({
                    'id': article.id,
                    'title': article.title,
                    'category_id': article.category_id
                })
        
        # 递归计算总数量（包括子分类的文章）
        def count_total(cat_data):
            total = cat_data['count']
            for child in cat_data['children']:
                total += count_total(child)
            cat_data['total_count'] = total
            return total
        
        for cat_data in root_categories:
            count_total(cat_data)
        
        # 递归转换分类数据，确保子分类也包含 items
        def convert_category_data(cat_data):
            result = {
                "name": cat_data['name'],
                "id": cat_data['id'],
                "count": cat_data['count'],
                "total_count": cat_data.get('total_count', cat_data['count']),
                "items": cat_data['items'],
                "children": [],
                "description": cat_data.get('description') or f"{cat_data['name']}相关文章",
                "order": cat_data.get('order', 0),
                "lastUpdated": None,  # 可以后续添加
                "featured": False,
                "trending": False,
                "latest": False,
                "views": cat_data.get('total_count', cat_data['count']) * 100,
                "popularTags": []
            }
            # 递归处理子分类
            if cat_data['children']:
                result['children'] = [convert_category_data(child) for child in cat_data['children']]
            return result
        
        # 转换为列表格式（保持向后兼容）
        category_list = []
        for cat_data in root_categories:
            category_list.append(convert_category_data(cat_data))

        # 根据配置设置分类标签
        featured_categories = current_app.config.get("BLOG_FEATURED_CATEGORIES", [])
        trending_categories = current_app.config.get("BLOG_TRENDING_CATEGORIES", [])
        latest_count = current_app.config.get("BLOG_LATEST_COUNT", 1)
        
        for category in category_list:
            if category["name"] in featured_categories:
                category["featured"] = True
            if category["name"] in trending_categories:
                category["trending"] = True
        
        # 设置最新标签
        categories_with_date = [c for c in category_list if c.get("lastUpdated")]
        if categories_with_date:
            categories_with_date.sort(key=lambda x: x["lastUpdated"], reverse=True)
            for i in range(min(latest_count, len(categories_with_date))):
                for category in category_list:
                    if category["name"] == categories_with_date[i]["name"]:
                        category["latest"] = True
                        break
        
        # 缓存2小时
        cache.set(cache_key, category_list, 7200)

        return jsonify({"success": True, "data": category_list, "cached": False})
    except Exception as e:
        logger.error(f"获取分类失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@blog_bp.route("/articles", methods=["GET"])
def get_articles():
    """获取文章列表"""
    try:
        category = request.args.get("category", "")
        search = request.args.get("search", "")
        tag = request.args.get("tag", "")
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 20, type=int)
        
        # 构建查询
        query = Article.query
        
        # 分类筛选（支持 category_id 或 category 名称）
        category_id = request.args.get("category_id", type=int)
        if category_id:
            query = query.filter_by(category_id=category_id)
        elif category:
            # 如果传入的是分类名称，先查找分类 ID
            blog_category = BlogCategory.query.filter_by(name=category).first()
            if blog_category:
                query = query.filter_by(category_id=blog_category.id)
            else:
                # 如果找不到分类，返回空结果
                query = query.filter(Article.id == -1)  # 永远不匹配的条件
        
        # 标签筛选
        if tag:
            tag_obj = Tag.query.filter_by(name=tag).first()
            if tag_obj:
                query = query.filter(Article.tags.contains(tag_obj))

        # 搜索（标题和描述）
        if search:
            query = query.filter(
                db.or_(
                    Article.title.like(f"%{search}%"),
                    Article.description.like(f"%{search}%")
                )
            )
        
        # 总数
        total = query.count()
        
        # 分页
        articles = query.order_by(Article.order, Article.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        result = [a.to_dict(include_content=False) for a in articles]
        
        # 估算阅读时间
        for article_data, article_obj in zip(result, articles):
            if article_obj.content:
                article_data["reading_time"] = max(1, len(article_obj.content) // 250)
                article_data["word_count"] = len(article_obj.content)

        return jsonify({
            "success": True, 
            "data": result,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": math.ceil(total / page_size) if page_size > 0 else 0
            }
        })
    except Exception as e:
        logger.error(f"获取文章列表失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@blog_bp.route("/articles/<int:article_id>", methods=["GET"])
def get_article(article_id):
    """获取单篇文章"""
    try:
        cache = get_cache()
        cache_key = f"blog:article:{article_id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info(f"从缓存获取文章详情: {article_id}")
            return jsonify({"success": True, "data": cached_data, "cached": True})

        # 从数据库获取
        article = Article.query.get_or_404(article_id)
        
        # 增加浏览量
        article.view_count += 1
        db.session.commit()
        
        # 生成内容哈希
        content_hash = hashlib.md5(article.content.encode()).hexdigest() if article.content else ""
        
        # 转换Markdown为HTML（如果未缓存或内容已更新）
        cache_html_key = f"blog:article_html:{article_id}:{content_hash}"
        html_content = cache.get(cache_html_key)
        
        if not html_content:
            html_content = convert_markdown_to_html(article.content)
            # 缓存HTML内容（8小时）
            cache.set(cache_html_key, html_content, 28800)

        # 从HTML中提取标题大纲
        headings = extract_headings_from_html(html_content)

        # 计算阅读时间和字数
        reading_time = max(1, len(article.content) // 250) if article.content else 0
        word_count = len(article.content) if article.content else 0
        
        # 获取关联的题目
        related_questions = []
        relations = ArticleQuestionRelation.query.filter_by(article_id=article_id).all()
        for relation in relations:
            question = relation.question
            related_questions.append({
                "id": question.id,
                "title": question.title,
                "type": question.type,
                "difficulty": question.difficulty,
                "tags": [tag.name for tag in question.tags] if question.tags else []
            })

        # 构建文章详情
        article_detail = {
            "id": article.id,
            "title": article.title,
            "description": article.description,
            "tags": [tag.name for tag in article.tags] if article.tags else [],
            "category_id": article.category_id,
            "category": article.category.name if article.category else None,
            "createdAt": article.created_at.isoformat() if article.created_at else None,
            "updatedAt": article.updated_at.isoformat() if article.updated_at else None,
            "content": article.content,
            "html_content": html_content,
            "headings": headings,
            "reading_time": reading_time,
            "word_count": word_count,
            "view_count": article.view_count,
            "related_questions": related_questions
        }

        # 缓存文章详情（4小时）
        cache.set(cache_key, article_detail, 14400)

        return jsonify({"success": True, "data": article_detail, "cached": False})
    except Exception as e:
        logger.error(f"获取文章详情失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@blog_bp.route("/tags", methods=["GET"])
def get_tags():
    """获取标签列表"""
    try:
        tags = Tag.query.order_by(Tag.count.desc(), Tag.name).all()
        result = [tag.to_dict() for tag in tags]
        return jsonify({"success": True, "data": result})
    except Exception as e:
        logger.error(f"获取标签列表失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@blog_bp.route("/search", methods=["GET"])
def search_articles():
    """搜索文章（仅搜索标题和标签）"""
    try:
        query_str = request.args.get("q", "").strip()
        if not query_str:
            return jsonify({"success": False, "error": "搜索关键词不能为空"}), 400
        
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 20, type=int)
        
        # 搜索文章（标题和描述）
        articles_query = Article.query.filter(
            db.or_(
                Article.title.like(f"%{query_str}%"),
                Article.description.like(f"%{query_str}%")
            )
        )
        
        total = articles_query.count()
        articles = articles_query.order_by(Article.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # 搜索标签
        tags = Tag.query.filter(Tag.name.like(f"%{query_str}%")).limit(10).all()
        
        result = {
            "articles": [a.to_dict(include_content=False) for a in articles],
            "tags": [tag.to_dict() for tag in tags],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": math.ceil(total / page_size) if page_size > 0 else 0
            }
        }
        
        return jsonify({"success": True, "data": result})
    except Exception as e:
        logger.error(f"搜索失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# 缓存管理API
@blog_bp.route("/cache/stats", methods=["GET"])
def get_cache_stats():
    """获取缓存统计信息"""
    try:
        cache = get_cache()
        stats = cache.get_cache_stats()
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@blog_bp.route("/cache/clear", methods=["POST"])
def clear_cache():
    """清理所有博客缓存"""
    try:
        cache = get_cache()
        cleared_count = cache.invalidate_all_cache()
        return jsonify({
                "success": True,
            "data": {"message": "缓存清理完成", "cleared_keys": cleared_count}
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
