# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, current_app, send_file, abort
from datetime import datetime
import os
import re
import yaml
import hashlib
from pathlib import Path
import markdown
from markdown.extensions import toc, codehilite, tables, fenced_code
from model.blog_cache import get_cache

blog_bp = Blueprint('blog', __name__, url_prefix='/api/blog')

def get_blog_dir():
    """获取博客目录路径"""
    return current_app.config.get('BLOG_DIR', os.path.join(os.path.dirname(__file__), '..', 'data', 'blog'))

def parse_markdown_frontmatter(content):
    """解析markdown文件的frontmatter"""
    frontmatter = {}
    content_lines = content.split('\n')
    
    if content_lines and content_lines[0].strip() == '---':
        yaml_lines = []
        i = 1
        while i < len(content_lines) and content_lines[i].strip() != '---':
            yaml_lines.append(content_lines[i])
            i += 1
        
        if i < len(content_lines):
            try:
                frontmatter = yaml.safe_load('\n'.join(yaml_lines)) or {}
                content = '\n'.join(content_lines[i+1:])
            except yaml.YAMLError:
                pass
    
    return frontmatter, content

def extract_headings_from_html(html_content):
    """从HTML内容中提取标题信息，确保ID与HTML中的实际ID匹配"""
    headings = []
    
    # 匹配HTML标题标签
    pattern = r'<h([1-6])[^>]*id="([^"]*)"[^>]*>(.*?)</h[1-6]>'
    matches = re.findall(pattern, html_content, re.DOTALL)
    
    for match in matches:
        level = int(match[0])
        anchor_id = match[1]
        title_html = match[2]
        
        # 提取标题文本，去除HTML标签和永久链接
        title_text = re.sub(r'<a[^>]*>.*?</a>', '', title_html).strip()
        
        headings.append({
            'level': level,
            'title': title_text,
            'anchor': anchor_id,
            'line': 0  # 从HTML中提取，无法确定原始行号
        })
    
    return headings

def scan_blog_directory():
    """扫描博客目录，获取所有分类和文章"""
    categories = {}
    blog_dir = get_blog_dir()
    
    if not os.path.exists(blog_dir):
        os.makedirs(blog_dir, exist_ok=True)
        return categories
    
    for category_name in os.listdir(blog_dir):
        category_path = os.path.join(blog_dir, category_name)
        if os.path.isdir(category_path):
            articles = []
            
            for filename in os.listdir(category_path):
                if filename.endswith('.md'):
                    file_path = os.path.join(category_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        frontmatter, markdown_content = parse_markdown_frontmatter(content)
                        
                        # 生成文章ID（基于文件路径）
                        article_id = f"{category_name}/{filename[:-3]}"
                        
                        # 提取文章信息
                        article_info = {
                            'id': article_id,
                            'title': frontmatter.get('title', filename[:-3]),
                            'description': frontmatter.get('description', ''),
                            'tags': frontmatter.get('tags', []),
                            'category': category_name,
                            'date': frontmatter.get('date', ''),
                            'createdAt': frontmatter.get('date', ''),
                            'updatedAt': frontmatter.get('date', ''),
                            'content': markdown_content,
                            'frontmatter': frontmatter,
                            'file_path': file_path,
                            'filename': filename
                        }
                        
                        # 生成摘要
                        if not article_info['description']:
                            # 从内容中提取摘要
                            plain_text = re.sub(r'[#*`\[\]]', '', markdown_content)
                            plain_text = re.sub(r'\n+', ' ', plain_text).strip()
                            article_info['description'] = plain_text[:200] + ('...' if len(plain_text) > 200 else '')
                        
                        articles.append(article_info)
                        
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                        continue
            
            # 按日期排序
            articles.sort(key=lambda x: x.get('date', ''), reverse=True)
            categories[category_name] = articles
    
    return categories

def get_all_articles():
    """获取所有文章"""
    categories = scan_blog_directory()
    all_articles = []
    
    for category_name, articles in categories.items():
        for article in articles:
            # 为列表显示准备数据
            list_article = {
                'id': article['id'],
                'title': article['title'],
                'description': article['description'],
                'tags': article['tags'],
                'category': article['category'],
                'createdAt': article['createdAt'],
                'updatedAt': article['updatedAt']
            }
            all_articles.append(list_article)
    
    return all_articles

def get_article_by_id(article_id):
    """根据ID获取文章详情"""
    categories = scan_blog_directory()
    
    for category_name, articles in categories.items():
        for article in articles:
            if article['id'] == article_id:
                return article
    
    return None

def convert_markdown_to_html(content, article_path=None):
    """将markdown转换为HTML，并处理图片路径"""
    # 先处理Mermaid代码块
    content = process_mermaid_blocks(content)
    
    md = markdown.Markdown(
        extensions=[
            'toc',
            'codehilite',
            'tables',
            'fenced_code',
            'attr_list'
        ],
        extension_configs={
            'toc': {
                'permalink': True,
                'permalink_title': '永久链接'
            }
        }
    )
    
    html_content = md.convert(content)
    
    # 处理图片路径
    if article_path:
        html_content = process_image_paths(html_content, article_path)
    
    return html_content

def process_mermaid_blocks(content):
    """处理Mermaid代码块，将其转换为HTML div"""
    import re
    
    # 匹配 ```mermaid 代码块
    pattern = r'```mermaid\n(.*?)\n```'
    
    def replace_mermaid(match):
        mermaid_code = match.group(1)
        # 生成唯一的ID
        import hashlib
        mermaid_id = hashlib.md5(mermaid_code.encode()).hexdigest()[:8]
        
        # 返回HTML div，包含Mermaid代码
        return f'<div class="mermaid" id="mermaid-{mermaid_id}">\n{mermaid_code}\n</div>'
    
    return re.sub(pattern, replace_mermaid, content, flags=re.DOTALL)

def process_image_paths(html_content, article_path):
    """处理HTML中的图片路径，将相对路径转换为API路径"""
    # 获取文章所在目录
    article_dir = os.path.dirname(article_path)
    blog_dir = get_blog_dir()
    
    # 匹配img标签中的src属性
    def replace_img_src(match):
        img_tag = match.group(0)
        src_match = re.search(r'src="([^"]*)"', img_tag)
        if src_match:
            src_path = src_match.group(1)
            # 如果是外部链接，保持不变
            if src_path.startswith(('http://', 'https://')):
                return img_tag
            # 如果已经是API路径，保持不变
            if src_path.startswith('/api/'):
                return img_tag
            
            # 处理博客内部路径
            if src_path.startswith('/'):
                # 特殊处理 /images/ 开头的路径，将其解析为文章目录下的images子目录
                if src_path.startswith('/images/'):
                    # 获取文章所在目录名（分类名）
                    category_name = os.path.basename(article_dir)
                    # 构建完整路径：分类名/images/文件名
                    image_filename = src_path[8:]  # 去掉 '/images/' 前缀
                    clean_path = f"{category_name}/images/{image_filename}"
                    api_path = f"/api/blog/images/{clean_path}"
                else:
                    # 其他以 / 开头的路径，去掉开头的 / 并直接使用
                    clean_path = src_path.lstrip('/')
                    api_path = f"/api/blog/images/{clean_path}"
            else:
                # 特殊处理 images/ 开头的相对路径，将其解析为文章目录下的images子目录
                if src_path.startswith('images/'):
                    # 获取文章所在目录名（分类名）
                    category_name = os.path.basename(article_dir)
                    # 构建完整路径：分类名/images/文件名
                    image_filename = src_path[7:]  # 去掉 'images/' 前缀
                    clean_path = f"{category_name}/images/{image_filename}"
                    api_path = f"/api/blog/images/{clean_path}"
                else:
                    # 其他相对路径，基于文章目录构建
                    full_image_path = os.path.join(article_dir, src_path)
                    relative_path = os.path.relpath(full_image_path, blog_dir)
                    api_path = f"/api/blog/images/{relative_path.replace(os.sep, '/')}"
            
            # 替换src属性
            new_img_tag = img_tag.replace(f'src="{src_path}"', f'src="{api_path}"')
            return new_img_tag
        return img_tag
    
    # 使用正则表达式替换所有img标签
    html_content = re.sub(r'<img[^>]*>', replace_img_src, html_content)
    
    return html_content

def extract_popular_tags(articles):
    """从文章列表中提取热门标签"""
    tag_counts = {}

    for article in articles:
        if article.get('tags'):
            for tag in article['tags']:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # 返回前3个最热门的标签
    return [tag for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]]

@blog_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    try:
        # 获取缓存实例
        cache = get_cache()

        # 尝试从缓存获取分类列表
        category_list = cache.get_categories()

        if category_list is not None:
            current_app.logger.info("从缓存获取分类列表")
            return jsonify({
                'success': True,
                'data': category_list,
                'cached': True
            })

        # 缓存未命中，从文件系统获取
        current_app.logger.info("缓存未命中，从文件系统获取分类列表")
        categories = scan_blog_directory()
        category_list = []

        for category_name, articles in categories.items():
            # 增强分类信息
            last_updated = max(
                (article.get('updatedAt') or article.get('createdAt') for article in articles),
                default=None
            )

            category_list.append({
                'name': category_name,
                'count': len(articles),
                'articles': articles,
                'description': f'{category_name}技术相关文章',
                'lastUpdated': last_updated,
                'featured': len(articles) > 10,  # 文章数量>10的设为精选
                'trending': len(articles) > 5,   # 文章数量>5的设为热门
                'views': len(articles) * 100,    # 模拟浏览量
                'popularTags': extract_popular_tags([article for article in articles])
            })

        # 设置缓存
        cache.set_categories(category_list)

        return jsonify({
            'success': True,
            'data': category_list,
            'cached': False
        })
    except Exception as e:
        current_app.logger.error(f"获取分类失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blog_bp.route('/articles', methods=['GET'])
def get_articles():
    """获取文章列表"""
    try:
        category = request.args.get('category', '')
        search = request.args.get('search', '')

        # 获取缓存实例
        cache = get_cache()

        # 尝试从缓存获取文章列表
        articles = cache.get_articles(category, search)

        if articles is not None:
            current_app.logger.info(f"从缓存获取文章列表: category={category}, search={search}")
            return jsonify({
                'success': True,
                'data': articles,
                'cached': True
            })

        # 缓存未命中，从文件系统获取
        current_app.logger.info(f"缓存未命中，从文件系统获取文章列表: category={category}, search={search}")

        if category:
            # 获取特定分类的文章
            categories = scan_blog_directory()
            if category in categories:
                articles = categories[category]
            else:
                articles = []
        else:
            # 获取所有文章
            articles = get_all_articles()

        # 搜索过滤
        if search:
            search_lower = search.lower()
            articles = [
                article for article in articles
                if (search_lower in article.get('title', '').lower() or
                    search_lower in article.get('description', '').lower() or
                    any(search_lower in tag.lower() for tag in article.get('tags', [])))
            ]

        # 增强文章信息
        for article in articles:
            if 'reading_time' not in article:
                # 估算阅读时间（按250字/分钟计算）
                content_length = len(article.get('content', ''))
                article['reading_time'] = max(1, content_length // 250)

            if 'word_count' not in article:
                article['word_count'] = len(article.get('content', ''))

        # 设置缓存
        cache.set_articles(articles, category, search)

        return jsonify({
            'success': True,
            'data': articles,
            'cached': False
        })
    except Exception as e:
        current_app.logger.error(f"获取文章列表失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blog_bp.route('/articles/<path:article_id>', methods=['GET'])
def get_article(article_id):
    """获取单篇文章"""
    try:
        # 获取缓存实例
        cache = get_cache()

        # 尝试从缓存获取文章详情
        article_detail = cache.get_article(article_id)

        if article_detail is not None:
            current_app.logger.info(f"从缓存获取文章详情: {article_id}")
            return jsonify({
                'success': True,
                'data': article_detail,
                'cached': True
            })

        # 缓存未命中，从文件系统获取
        current_app.logger.info(f"缓存未命中，从文件系统获取文章详情: {article_id}")

        article = get_article_by_id(article_id)
        if not article:
            return jsonify({
                'success': False,
                'error': '文章不存在'
            }), 404

        # 生成内容哈希，用于HTML缓存验证
        content_hash = hashlib.md5(article['content'].encode()).hexdigest()

        # 尝试从缓存获取HTML内容
        html_content = cache.get_article_html(article_id, content_hash)

        if html_content is None:
            # HTML缓存未命中，重新转换
            current_app.logger.info(f"HTML缓存未命中，重新转换: {article_id}")
            html_content = convert_markdown_to_html(article['content'], article['file_path'])
            # 缓存HTML内容
            cache.set_article_html(article_id, html_content, content_hash)

        # 从HTML中提取标题大纲
        headings = extract_headings_from_html(html_content)

        # 计算阅读时间和字数
        reading_time = max(1, len(article['content']) // 250)
        word_count = len(article['content'])

        # 构建文章详情
        article_detail = {
            'id': article['id'],
            'title': article['title'],
            'description': article['description'],
            'tags': article['tags'],
            'category': article['category'],
            'createdAt': article['createdAt'],
            'updatedAt': article['updatedAt'],
            'content': article['content'],
            'html_content': html_content,
            'headings': headings,
            'frontmatter': article['frontmatter'],
            'reading_time': reading_time,
            'word_count': word_count,
            'content_hash': content_hash
        }

        # 设置文章详情缓存
        cache.set_article(article_id, article_detail)

        return jsonify({
            'success': True,
            'data': article_detail,
            'cached': False
        })
    except Exception as e:
        current_app.logger.error(f"获取文章详情失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 缓存管理API
@blog_bp.route('/cache/stats', methods=['GET'])
def get_cache_stats():
    """获取缓存统计信息"""
    try:
        cache = get_cache()
        stats = cache.get_cache_stats()

        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blog_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """清理所有博客缓存"""
    try:
        cache = get_cache()
        cleared_count = cache.invalidate_all_cache()

        return jsonify({
            'success': True,
            'data': {
                'message': '缓存清理完成',
                'cleared_keys': cleared_count
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blog_bp.route('/cache/warmup', methods=['POST'])
def warmup_cache():
    """预热缓存"""
    try:
        cache = get_cache()
        result = cache.warm_up_cache(scan_blog_directory, get_all_articles)

        return jsonify({
            'success': result['success'],
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blog_bp.route('/search', methods=['GET'])
def search_articles():
    """搜索文章"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'success': False,
                'error': '搜索关键词不能为空'
            }), 400
        
        articles = get_all_articles()
        search_lower = query.lower()
        
        filtered_articles = [
            article for article in articles
            if (search_lower in article.get('title', '').lower() or
                search_lower in article.get('description', '').lower() or
                any(search_lower in tag.lower() for tag in article.get('tags', [])))
        ]
        
        return jsonify({
            'success': True,
            'data': filtered_articles
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blog_bp.route('/config', methods=['GET'])
def get_blog_config_api():
    """获取博客配置"""
    try:
        blog_dir = get_blog_dir()
        return jsonify({
            'success': True,
            'data': {
                'blog_dir': blog_dir,
                'message': '博客目录配置成功'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blog_bp.route('/images/<path:image_path>')
def serve_image(image_path):
    """提供图片文件服务"""
    try:
        blog_dir = get_blog_dir()
        # 构建完整的图片路径
        full_image_path = os.path.join(blog_dir, image_path)
        
        # 安全检查：确保图片路径在博客目录内
        if not os.path.abspath(full_image_path).startswith(os.path.abspath(blog_dir)):
            abort(403)
        
        # 检查文件是否存在
        if not os.path.exists(full_image_path) or not os.path.isfile(full_image_path):
            abort(404)
        
        # 检查文件扩展名
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'}
        file_ext = os.path.splitext(full_image_path)[1].lower()
        if file_ext not in allowed_extensions:
            abort(400)
        
        # 发送文件
        return send_file(full_image_path)
        
    except Exception as e:
        current_app.logger.error(f"Error serving image {image_path}: {str(e)}")
        abort(500)