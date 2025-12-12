from flask import Blueprint, request, jsonify
from auth.auth_utils import admin_required
from model.database import (
    db, User, Category, Question, Tag, Article, 
    ArticleQuestionRelation, QuestionFavorite, BlogCategory, Feedback
)
from config.config import logger
import math

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


def sync_question_article_relations(question, article_ids):
    """同步题目与文章的关联关系"""
    if article_ids is None:
        return
    
    # 正常化参数
    if not isinstance(article_ids, list):
        article_ids = []
    cleaned_ids = []
    for value in article_ids:
        try:
            cleaned_ids.append(int(value))
        except (TypeError, ValueError):
            continue
    
    # 删除旧的关联
    ArticleQuestionRelation.query.filter_by(question_id=question.id).delete()
    
    if not cleaned_ids:
        return
    
    # 只关联存在的文章
    valid_articles = Article.query.filter(Article.id.in_(cleaned_ids)).all()
    for article in valid_articles:
        relation = ArticleQuestionRelation(article_id=article.id, question_id=question.id)
        db.session.add(relation)


@admin_bp.route("/login", methods=["POST"])
def admin_login():
    """管理员登录"""
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return jsonify({"success": False, "error": "用户名和密码不能为空"}), 400
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({"success": False, "error": "用户名或密码错误"}), 401
        
        # 验证密码
        if not user.check_password(password):
            return jsonify({"success": False, "error": "用户名或密码错误"}), 401
        
        # 检查是否为管理员
        if user.role != "admin":
            return jsonify({"success": False, "error": "需要管理员权限"}), 403
        
        # 更新最后登录时间
        from datetime import datetime
        import pytz
        user.last_login = datetime.now(pytz.timezone("Asia/Shanghai"))
        db.session.commit()
        
        # 生成Token（使用JWT或简单token）
        import secrets
        import hashlib
        from datetime import datetime, timedelta
        
        # 创建token
        token_str = f"{user.id}:{user.username}:{datetime.now().isoformat()}"
        token = hashlib.sha256(token_str.encode()).hexdigest()
        
        # 保存token到数据库
        expires_at = datetime.now() + timedelta(days=7)  # 7天过期
        from model.database import UserToken
        user_token = UserToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        db.session.add(user_token)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "role": user.role
            },
            "expires_at": expires_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"管理员登录失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/users", methods=["GET"])
@admin_required
def get_users():
    try:
        # 支持通过查询参数过滤用户类型
        user_type = request.args.get("user_type", "wechat")
        
        # 构建查询
        query = User.query
        if user_type:
            query = query.filter_by(user_type=user_type)
        
        users = query.all()
        result = [user.to_dict() for user in users]
        return jsonify({"success": True, "users": result}), 200
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/users/<int:user_id>/role", methods=["PUT"])
@admin_required
def update_user_role(user_id):
    try:
        data = request.get_json()
        new_role = data.get("role")

        if not new_role:
            return jsonify({"success": False, "error": "缺少必要参数"}), 400

        if new_role not in ["admin", "user"]:
            return jsonify({"success": False, "error": "无效的角色值"}), 400

        user = User.query.get_or_404(user_id)
        user.role = new_role
        db.session.commit()
        
        return jsonify({"success": True, "data": user.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== 分类管理 ====================

@admin_bp.route("/categories", methods=["GET"])
@admin_required
def get_categories():
    """获取所有分类"""
    try:
        categories = Category.query.order_by(Category.order, Category.id).all()
        result = [cat.to_dict() for cat in categories]
        return jsonify({"success": True, "data": result})
    except Exception as e:
        logger.error(f"获取分类列表失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/categories", methods=["POST"])
@admin_required
def create_category():
    """创建分类"""
    try:
        data = request.get_json()
        category = Category(
            name=data.get("name"),
            description=data.get("description", ""),
            parent_id=data.get("parent_id"),
            order=data.get("order", 0)
        )
        db.session.add(category)
        db.session.commit()
        return jsonify({"success": True, "data": category.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建分类失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/categories/<int:category_id>", methods=["PUT"])
@admin_required
def update_category(category_id):
    """更新分类"""
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        if "name" in data:
            category.name = data["name"]
        if "description" in data:
            category.description = data["description"]
        if "parent_id" in data:
            category.parent_id = data["parent_id"]
        if "order" in data:
            category.order = data["order"]
        
        db.session.commit()
        return jsonify({"success": True, "data": category.to_dict()})
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新分类失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/categories/<int:category_id>", methods=["DELETE"])
@admin_required
def delete_category(category_id):
    """删除分类"""
    try:
        category = Category.query.get_or_404(category_id)
        # 检查是否有子分类
        if category.children:
            return jsonify({"success": False, "error": "该分类下存在子分类，无法删除"}), 400
        # 检查是否有题目
        if category.questions.count() > 0:
            return jsonify({"success": False, "error": "该分类下存在题目，无法删除"}), 400
        
        db.session.delete(category)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除分类失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== 题目管理 ====================

@admin_bp.route("/questions", methods=["GET"])
@admin_required
def get_questions():
    """获取题目列表"""
    try:
        category_id = request.args.get("category_id", type=int)
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 20, type=int)
        
        query = Question.query
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        total = query.count()
        questions = query.order_by(Question.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        result = [q.to_dict(include_answer=True) for q in questions]
        
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
        logger.error(f"获取题目列表失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/questions", methods=["POST"])
@admin_required
def create_question():
    """创建题目"""
    try:
        data = request.get_json()
        question = Question(
            category_id=data.get("category_id"),
            type=data.get("type"),  # 'short_answer' or 'programming'
            title=data.get("title"),
            content=data.get("content"),
            answer=data.get("answer"),
            explanation=data.get("explanation", ""),
            difficulty=data.get("difficulty", 3)
        )
        db.session.add(question)
        db.session.flush()
        
        # 处理标签
        if "tags" in data:
            for tag_name in data["tags"]:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name, count=0)
                    db.session.add(tag)
                question.tags.append(tag)
                tag.count += 1
        
        # 处理关联文章
        related_article_ids = data.get("related_article_ids")
        sync_question_article_relations(question, related_article_ids)
        
        db.session.commit()
        return jsonify({"success": True, "data": question.to_dict(include_answer=True)}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建题目失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/questions/<int:question_id>", methods=["GET"])
@admin_required
def get_question(question_id):
    """获取单个题目详情"""
    try:
        question = Question.query.get_or_404(question_id)
        return jsonify({"success": True, "data": question.to_dict(include_answer=True)})
    except Exception as e:
        logger.error(f"获取题目详情失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/questions/<int:question_id>", methods=["PUT"])
@admin_required
def update_question(question_id):
    """更新题目"""
    try:
        question = Question.query.get_or_404(question_id)
        data = request.get_json()
        
        if "category_id" in data:
            question.category_id = data["category_id"]
        if "type" in data:
            question.type = data["type"]
        if "title" in data:
            question.title = data["title"]
        if "content" in data:
            question.content = data["content"]
        if "answer" in data:
            question.answer = data["answer"]
        if "explanation" in data:
            question.explanation = data["explanation"]
        if "difficulty" in data:
            question.difficulty = data["difficulty"]
        
        # 处理标签
        if "tags" in data:
            # 移除旧标签
            for tag in question.tags.all():
                tag.count -= 1
                question.tags.remove(tag)
            
            # 添加新标签
            for tag_name in data["tags"]:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name, count=0)
                    db.session.add(tag)
                question.tags.append(tag)
                tag.count += 1
        
        # 处理关联文章
        if "related_article_ids" in data:
            sync_question_article_relations(question, data.get("related_article_ids"))
        
        db.session.commit()
        return jsonify({"success": True, "data": question.to_dict(include_answer=True)})
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新题目失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/questions/<int:question_id>", methods=["DELETE"])
@admin_required
def delete_question(question_id):
    """删除题目"""
    try:
        question = Question.query.get_or_404(question_id)
        
        # 更新标签计数
        for tag in question.tags.all():
            tag.count -= 1
        
        db.session.delete(question)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除题目失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== 文章管理 ====================

@admin_bp.route("/articles", methods=["GET"])
@admin_required
def get_articles():
    """获取文章列表"""
    try:
        category = request.args.get("category")
        category_id = request.args.get("category_id", type=int)
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 20, type=int)
        
        query = Article.query
        # 分类筛选（支持 category_id 或 category 名称）
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
        
        total = query.count()
        articles = query.order_by(Article.order, Article.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        result = [a.to_dict(include_content=False) for a in articles]
        
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


@admin_bp.route("/articles/options", methods=["GET"])
@admin_required
def get_article_options():
    """为关联选择提供文章选项"""
    try:
        search = request.args.get("q", "").strip()
        limit = request.args.get("limit", 100, type=int)
        
        query = Article.query
        if search:
            query = query.filter(Article.title.like(f"%{search}%"))
        
        articles = query.order_by(Article.created_at.desc()).limit(max(1, min(limit, 500))).all()
        data = [
            {
                "id": article.id,
                "title": article.title,
                "category_id": article.category_id,
                "category": article.category.name if article.category else None
            }
            for article in articles
        ]
        return jsonify({"success": True, "data": data})
    except Exception as e:
        logger.error(f"获取文章选项失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/articles", methods=["POST"])
@admin_required
def create_article():
    """创建文章"""
    try:
        data = request.get_json()
        article = Article(
            title=data.get("title"),
            description=data.get("description", ""),
            content=data.get("content"),
            category_id=data.get("category_id"),
            order=data.get("order", 999999)
        )
        db.session.add(article)
        db.session.flush()
        
        # 处理标签
        if "tags" in data:
            for tag_name in data["tags"]:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name, count=0)
                    db.session.add(tag)
                article.tags.append(tag)
                tag.count += 1
        
        # 处理关联题目
        if "question_ids" in data:
            for question_id in data["question_ids"]:
                relation = ArticleQuestionRelation(
                    article_id=article.id,
                    question_id=question_id
                )
                db.session.add(relation)
        
        db.session.commit()
        return jsonify({"success": True, "data": article.to_dict(include_content=True)}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建文章失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/articles/<int:article_id>", methods=["GET"])
@admin_required
def get_article(article_id):
    """获取单个文章详情"""
    try:
        article = Article.query.get_or_404(article_id)
        return jsonify({"success": True, "data": article.to_dict(include_content=True)})
    except Exception as e:
        logger.error(f"获取文章详情失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/articles/<int:article_id>", methods=["PUT"])
@admin_required
def update_article(article_id):
    """更新文章"""
    try:
        article = Article.query.get_or_404(article_id)
        data = request.get_json()
        
        if "title" in data:
            article.title = data["title"]
        if "description" in data:
            article.description = data["description"]
        if "content" in data:
            article.content = data["content"]
        if "category_id" in data:
            article.category_id = data.get("category_id")
        if "order" in data:
            article.order = data["order"]
        
        # 处理标签
        if "tags" in data:
            # 移除旧标签
            for tag in article.tags.all():
                tag.count -= 1
                article.tags.remove(tag)
            
            # 添加新标签
            for tag_name in data["tags"]:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name, count=0)
                    db.session.add(tag)
                article.tags.append(tag)
                tag.count += 1
        
        # 处理关联题目
        if "question_ids" in data:
            # 删除旧关联
            ArticleQuestionRelation.query.filter_by(article_id=article_id).delete()
            
            # 添加新关联
            for question_id in data["question_ids"]:
                relation = ArticleQuestionRelation(
                    article_id=article_id,
                    question_id=question_id
                )
                db.session.add(relation)
        
        db.session.commit()
        return jsonify({"success": True, "data": article.to_dict(include_content=True)})
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新文章失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/articles/<int:article_id>", methods=["DELETE"])
@admin_required
def delete_article(article_id):
    """删除文章"""
    try:
        article = Article.query.get_or_404(article_id)
        
        # 更新标签计数
        for tag in article.tags.all():
            tag.count -= 1
        
        db.session.delete(article)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除文章失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== 关联管理 ====================

@admin_bp.route("/articles/<int:article_id>/questions", methods=["GET"])
@admin_required
def get_article_questions(article_id):
    """获取文章关联的题目"""
    try:
        article = Article.query.get_or_404(article_id)
        relations = ArticleQuestionRelation.query.filter_by(article_id=article_id).all()
        
        result = [{
            "id": rel.question_id,
            "title": rel.question.title,
            "type": rel.question.type,
            "difficulty": rel.question.difficulty
        } for rel in relations]
        
        return jsonify({"success": True, "data": result})
    except Exception as e:
        logger.error(f"获取文章关联题目失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/articles/<int:article_id>/questions", methods=["POST"])
@admin_required
def add_article_question(article_id):
    """为文章添加关联题目"""
    try:
        data = request.get_json()
        question_id = data.get("question_id")
        
        if not question_id:
            return jsonify({"success": False, "error": "缺少question_id"}), 400
        
        # 检查是否已存在
        existing = ArticleQuestionRelation.query.filter_by(
            article_id=article_id,
            question_id=question_id
        ).first()
        
        if existing:
            return jsonify({"success": False, "error": "关联已存在"}), 400
        
        relation = ArticleQuestionRelation(
            article_id=article_id,
            question_id=question_id
        )
        db.session.add(relation)
        db.session.commit()
        
        return jsonify({"success": True, "data": {"id": relation.id}}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"添加文章关联题目失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/articles/<int:article_id>/questions/<int:question_id>", methods=["DELETE"])
@admin_required
def remove_article_question(article_id, question_id):
    """移除文章关联的题目"""
    try:
        relation = ArticleQuestionRelation.query.filter_by(
            article_id=article_id,
            question_id=question_id
        ).first_or_404()
        
        db.session.delete(relation)
        db.session.commit()
        
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"移除文章关联题目失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== 博客分类管理 ====================

@admin_bp.route("/blog-categories", methods=["GET"])
@admin_required
def get_blog_categories():
    """获取所有博客分类（树形结构）"""
    try:
        # 获取所有分类
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
        
        # 第三遍：统计文章数量
        article_counts = db.session.query(
            Article.category_id,
            db.func.count(Article.id).label('count')
        ).filter(
            Article.category_id.isnot(None)
        ).group_by(Article.category_id).all()
        
        for category_id, count in article_counts:
            if category_id in category_dict:
                category_dict[category_id]['count'] = count
        
        # 递归计算总数量（包括子分类的文章）
        def count_total(cat_data):
            total = cat_data['count']
            for child in cat_data['children']:
                total += count_total(child)
            cat_data['total_count'] = total
            return total
        
        for cat_data in root_categories:
            count_total(cat_data)
        
        return jsonify({"success": True, "data": root_categories})
    except Exception as e:
        logger.error(f"获取博客分类失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/blog-categories", methods=["POST"])
@admin_required
def create_blog_category():
    """创建博客分类"""
    try:
        data = request.get_json()
        category_name = data.get("name")
        parent_id = data.get("parent_id")
        description = data.get("description", "")
        order = data.get("order", 0)
        
        if not category_name:
            return jsonify({"success": False, "error": "分类名称不能为空"}), 400
        
        # 如果指定了 parent_id，检查父分类是否存在
        if parent_id is not None:
            parent_category = BlogCategory.query.get(parent_id)
            if not parent_category:
                return jsonify({"success": False, "error": "父分类不存在"}), 400
        
        # 检查分类是否已存在（同一父分类下不能重名）
        existing = BlogCategory.query.filter_by(
            name=category_name,
            parent_id=parent_id
        ).first()
        if existing:
            return jsonify({"success": False, "error": "该分类已存在"}), 400
        
        # 创建分类
        blog_category = BlogCategory(
            name=category_name,
            parent_id=parent_id,
            description=description,
            order=order
        )
        db.session.add(blog_category)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": blog_category.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建博客分类失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/blog-categories/<int:category_id>", methods=["PUT"])
@admin_required
def update_blog_category(category_id):
    """更新博客分类"""
    try:
        category = BlogCategory.query.get_or_404(category_id)
        data = request.get_json()
        
        # 获取新的 parent_id（如果提供的话，否则使用当前的）
        new_parent_id = data.get("parent_id", category.parent_id)
        
        # 检查循环引用：不能将父分类设置为自己的子分类
        if new_parent_id is not None:
            # 检查 new_parent_id 是否是当前分类的子分类（包括子分类的子分类）
            def is_descendant(cat_id, ancestor_id):
                """检查 cat_id 是否是 ancestor_id 的后代"""
                if cat_id == ancestor_id:
                    return True
                parent = BlogCategory.query.get(cat_id)
                if parent and parent.parent_id:
                    return is_descendant(parent.parent_id, ancestor_id)
                return False
            
            if is_descendant(new_parent_id, category_id):
                return jsonify({"success": False, "error": "不能将父分类设置为自己的子分类"}), 400
        
        if "name" in data:
            # 检查新名称是否在同一父分类下已存在（使用新的 parent_id）
            existing = BlogCategory.query.filter_by(
                name=data["name"],
                parent_id=new_parent_id
            ).filter(BlogCategory.id != category_id).first()
            if existing:
                return jsonify({"success": False, "error": "该分类名称已存在"}), 400
            category.name = data["name"]
        
        if "parent_id" in data:
            category.parent_id = data["parent_id"]
        
        if "description" in data:
            category.description = data["description"]
        
        if "order" in data:
            category.order = data["order"]
        
        db.session.commit()
        return jsonify({"success": True, "data": category.to_dict()})
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新博客分类失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/blog-categories/<int:category_id>", methods=["DELETE"])
@admin_required
def delete_blog_category(category_id):
    """删除博客分类（将相关文章 category_id 置为 NULL，并删除分类记录）"""
    try:
        category = BlogCategory.query.get_or_404(category_id)
        
        # 检查是否有子分类
        children_count = BlogCategory.query.filter_by(parent_id=category_id).count()
        if children_count > 0:
            return jsonify({"success": False, "error": f"该分类下有 {children_count} 个子分类，请先删除子分类"}), 400
        
        # 统计相关文章数量
        articles_count = Article.query.filter_by(category_id=category_id).count()
        
        # 更新文章：将 category_id 置为 NULL
        Article.query.filter_by(category_id=category_id).update({Article.category_id: None})
        
        # 删除分类记录（由于外键约束，子分类的 parent_id 会自动设为 NULL）
        db.session.delete(category)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "updated_count": articles_count,
                "deleted_categories_count": 1
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除博客分类失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== 意见反馈管理 ====================

@admin_bp.route("/feedbacks", methods=["GET"])
@admin_required
def get_feedbacks():
    """获取意见反馈列表（管理员）"""
    try:
        status = request.args.get("status")  # pending, processed, closed
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 20, type=int)
        
        query = Feedback.query
        
        # 状态筛选
        if status:
            query = query.filter_by(status=status)
        
        total = query.count()
        feedbacks = query.order_by(Feedback.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        result = [f.to_dict() for f in feedbacks]
        
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
        logger.error(f"获取反馈列表失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/feedbacks/<int:feedback_id>", methods=["PUT"])
@admin_required
def update_feedback_status(feedback_id):
    """更新反馈状态（管理员）"""
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "请求数据不能为空"}), 400
        
        status = data.get("status")
        if status not in ['pending', 'processed', 'closed']:
            return jsonify({"success": False, "error": "无效的状态值"}), 400
        
        from datetime import datetime
        import pytz
        
        feedback.status = status
        if status in ['processed', 'closed']:
            feedback.processed_at = datetime.now(pytz.timezone("Asia/Shanghai"))
        else:
            feedback.processed_at = None
        
        db.session.commit()
        
        logger.info(f"管理员更新了反馈 {feedback_id} 的状态为 {status}")
        
        return jsonify({
            "success": True,
            "data": feedback.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新反馈状态失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
