"""
博客缓存模块
提供Redis缓存功能来优化博客性能
"""

import redis
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import current_app

logger = logging.getLogger(__name__)

class BlogCache:
    """博客缓存管理器"""

    def __init__(self, redis_client=None):
        """
        初始化缓存管理器

        Args:
            redis_client: Redis客户端实例，如果为None则创建新实例
        """
        if redis_client:
            self.redis_client = redis_client
        else:
            # 尝试连接Redis，如果失败则使用空实现
            try:
                self.redis_client = redis.Redis(
                    host=current_app.config.get('REDIS_HOST', 'localhost'),
                    port=current_app.config.get('REDIS_PORT', 6379),
                    db=current_app.config.get('REDIS_DB', 0),
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                # 测试连接
                self.redis_client.ping()
                logger.info("Redis连接成功")
            except Exception as e:
                logger.warning(f"Redis连接失败，使用内存缓存: {e}")
                self.redis_client = None

        # 缓存键前缀
        self.prefix = "blog:"

        # 缓存时间配置（秒）
        self.cache_ttl = {
            'categories': 3600,      # 分类列表缓存1小时
            'articles': 1800,        # 文章列表缓存30分钟
            'article_detail': 7200,  # 文章详情缓存2小时
            'article_html': 14400,   # 文章HTML缓存4小时
        }

    def _get_cache_key(self, category: str, *args) -> str:
        """
        生成缓存键

        Args:
            category: 缓存类别
            *args: 附加参数，用于生成唯一键

        Returns:
            str: 缓存键
        """
        if args:
            # 创建参数的哈希值以确保键的唯一性
            params_str = ":".join(str(arg) for arg in args)
            hash_str = hashlib.md5(params_str.encode()).hexdigest()[:8]
            return f"{self.prefix}{category}:{hash_str}"
        return f"{self.prefix}{category}"

    def get(self, key: str) -> Optional[Any]:
        """
        从缓存获取数据

        Args:
            key: 缓存键

        Returns:
            Any: 缓存的数据，如果不存在或Redis不可用则返回None
        """
        if not self.redis_client:
            return None

        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"缓存读取失败 {key}: {e}")

        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存数据

        Args:
            key: 缓存键
            value: 要缓存的数据
            ttl: 过期时间（秒），如果为None则使用默认时间

        Returns:
            bool: 是否设置成功
        """
        if not self.redis_client:
            return False

        try:
            data = json.dumps(value, ensure_ascii=False, default=str)
            if ttl:
                return self.redis_client.setex(key, ttl, data)
            else:
                return self.redis_client.set(key, data)
        except Exception as e:
            logger.error(f"缓存写入失败 {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            bool: 是否删除成功
        """
        if not self.redis_client:
            return False

        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"缓存删除失败 {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        按模式删除缓存

        Args:
            pattern: 模式，支持通配符*

        Returns:
            int: 删除的键数量
        """
        if not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"模式删除失败 {pattern}: {e}")
            return 0

    def get_categories(self) -> Optional[List[Dict[str, Any]]]:
        """
        获取分类列表缓存

        Returns:
            List[Dict]: 分类列表，如果缓存不存在则返回None
        """
        key = self._get_cache_key('categories')
        return self.get(key)

    def set_categories(self, categories: List[Dict[str, Any]]) -> bool:
        """
        设置分类列表缓存

        Args:
            categories: 分类列表

        Returns:
            bool: 是否设置成功
        """
        key = self._get_cache_key('categories')
        return self.set(key, categories, self.cache_ttl['categories'])

    def get_articles(self, category: str = '', search: str = '') -> Optional[List[Dict[str, Any]]]:
        """
        获取文章列表缓存

        Args:
            category: 分类名称
            search: 搜索关键词

        Returns:
            List[Dict]: 文章列表，如果缓存不存在则返回None
        """
        key = self._get_cache_key('articles', category, search)
        return self.get(key)

    def set_articles(self, articles: List[Dict[str, Any]], category: str = '', search: str = '') -> bool:
        """
        设置文章列表缓存

        Args:
            articles: 文章列表
            category: 分类名称
            search: 搜索关键词

        Returns:
            bool: 是否设置成功
        """
        key = self._get_cache_key('articles', category, search)
        return self.set(key, articles, self.cache_ttl['articles'])

    def get_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        """
        获取文章详情缓存

        Args:
            article_id: 文章ID

        Returns:
            Dict: 文章详情，如果缓存不存在则返回None
        """
        key = self._get_cache_key('article_detail', article_id)
        return self.get(key)

    def set_article(self, article_id: str, article: Dict[str, Any]) -> bool:
        """
        设置文章详情缓存

        Args:
            article_id: 文章ID
            article: 文章详情

        Returns:
            bool: 是否设置成功
        """
        key = self._get_cache_key('article_detail', article_id)
        return self.set(key, article, self.cache_ttl['article_detail'])

    def get_article_html(self, article_id: str, content_hash: str = '') -> Optional[str]:
        """
        获取文章HTML缓存

        Args:
            article_id: 文章ID
            content_hash: 内容哈希值，用于缓存验证

        Returns:
            str: HTML内容，如果缓存不存在则返回None
        """
        key = self._get_cache_key('article_html', article_id, content_hash)
        return self.get(key)

    def set_article_html(self, article_id: str, html_content: str, content_hash: str = '') -> bool:
        """
        设置文章HTML缓存

        Args:
            article_id: 文章ID
            html_content: HTML内容
            content_hash: 内容哈希值

        Returns:
            bool: 是否设置成功
        """
        key = self._get_cache_key('article_html', article_id, content_hash)
        return self.set(key, html_content, self.cache_ttl['article_html'])

    def invalidate_article_cache(self, article_id: str) -> int:
        """
        失效文章相关的所有缓存

        Args:
            article_id: 文章ID

        Returns:
            int: 删除的缓存键数量
        """
        count = 0

        # 删除文章详情缓存
        detail_pattern = f"{self.prefix}article_detail:*{article_id}*"
        count += self.delete_pattern(detail_pattern)

        # 删除文章HTML缓存
        html_pattern = f"{self.prefix}article_html:*{article_id}*"
        count += self.delete_pattern(html_pattern)

        return count

    def invalidate_category_cache(self, category: str = '') -> int:
        """
        失效分类相关的所有缓存

        Args:
            category: 分类名称，为空则失效所有分类缓存

        Returns:
            int: 删除的缓存键数量
        """
        count = 0

        if category:
            # 删除特定分类的文章列表缓存
            articles_pattern = f"{self.prefix}articles:*{category}*"
            count += self.delete_pattern(articles_pattern)
        else:
            # 删除所有分类和文章列表缓存
            categories_key = self._get_cache_key('categories')
            count += int(self.delete(categories_key))

            articles_pattern = f"{self.prefix}articles:*"
            count += self.delete_pattern(articles_pattern)

        return count

    def invalidate_all_cache(self) -> int:
        """
        失效所有博客相关缓存

        Returns:
            int: 删除的缓存键数量
        """
        pattern = f"{self.prefix}*"
        return self.delete_pattern(pattern)

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            Dict: 缓存统计信息
        """
        if not self.redis_client:
            return {
                'available': False,
                'message': 'Redis不可用'
            }

        try:
            info = self.redis_client.info()

            # 获取博客相关的缓存键数量
            blog_keys = self.redis_client.keys(f"{self.prefix}*")

            return {
                'available': True,
                'redis_version': info.get('redis_version'),
                'used_memory_human': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'blog_cache_keys': len(blog_keys),
                'cache_ttl_config': self.cache_ttl
            }
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {
                'available': False,
                'message': f'获取统计信息失败: {e}'
            }

    def warm_up_cache(self, scan_blog_directory_func, get_all_articles_func) -> Dict[str, Any]:
        """
        预热缓存

        Args:
            scan_blog_directory_func: 扫描博客目录的函数
            get_all_articles_func: 获取所有文章的函数

        Returns:
            Dict: 预热结果
        """
        if not self.redis_client:
            return {
                'success': False,
                'message': 'Redis不可用'
            }

        try:
            start_time = datetime.now()

            # 预热分类缓存
            categories = scan_blog_directory_func()
            category_list = [
                {
                    'name': name,
                    'count': len(articles),
                    'articles': articles
                }
                for name, articles in categories.items()
            ]
            self.set_categories(category_list)

            # 预热文章列表缓存
            all_articles = get_all_articles_func()
            self.set_articles(all_articles)

            # 为每个分类预热文章列表缓存
            for category_name in categories.keys():
                category_articles = categories[category_name]
                self.set_articles(category_articles, category_name)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            return {
                'success': True,
                'message': '缓存预热完成',
                'duration_seconds': duration,
                'categories_count': len(category_list),
                'articles_count': len(all_articles)
            }

        except Exception as e:
            logger.error(f"缓存预热失败: {e}")
            return {
                'success': False,
                'message': f'缓存预热失败: {e}'
            }

# 全局缓存实例
cache = None

def init_cache(app=None):
    """
    初始化缓存

    Args:
        app: Flask应用实例
    """
    global cache

    if app:
        with app.app_context():
            cache = BlogCache()
    else:
        cache = BlogCache()

    return cache

def get_cache() -> BlogCache:
    """
    获取缓存实例

    Returns:
        BlogCache: 缓存实例
    """
    global cache
    if cache is None:
        cache = BlogCache()
    return cache