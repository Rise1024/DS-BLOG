"""
题库相关API路由
"""
from flask import Blueprint, request, jsonify, current_app
from model.database import db, Category, Question, Tag, QuestionFavorite
from model.blog_cache import get_cache
from auth.auth_utils import login_required
from config.config import logger
import math

question_bank_bp = Blueprint("question_bank", __name__, url_prefix="/api/v1/question-bank")


@question_bank_bp.route("/categories", methods=["GET"])
def get_categories():
    """获取题库分类列表"""
    try:
        cache = get_cache()
        cache_key = f"question_bank:categories"
        
        # 检查是否需要清除缓存（可以通过查询参数控制）
        clear_cache = request.args.get("clear_cache", "false").lower() == "true"
        if clear_cache:
            cache.delete(cache_key)
            logger.info("已清除分类缓存")
        
        cached_data = cache.get(cache_key)
        
        if cached_data and not clear_cache:
            logger.info("从缓存获取分类列表")
            return jsonify({"success": True, "data": cached_data, "cached": True})
        
        # 从数据库获取
        categories = Category.query.order_by(Category.order, Category.id).all()
        
        if not categories:
            logger.warning("数据库中没有分类数据")
            return jsonify({"success": True, "data": [], "cached": False})
        
        # 构建分类树
        category_dict = {}
        root_categories = []
        
        # 第一遍：创建所有分类节点
        for cat in categories:
            cat_data = cat.to_dict()
            cat_data['children'] = []
            category_dict[cat.id] = cat_data
        
        # 第二遍：建立父子关系
        for cat in categories:
            cat_data = category_dict[cat.id]
            if cat.parent_id is None:
                root_categories.append(cat_data)
            else:
                if cat.parent_id in category_dict:
                    category_dict[cat.parent_id]['children'].append(cat_data)
                else:
                    logger.warning(f"分类 {cat.id} 的父分类 {cat.parent_id} 不存在")
        
        # 计算每个分类的题目总数（包括子分类），并添加题目列表
        def count_questions(cat_data, cat_id):
            # 获取该分类下的题目
            questions = Question.query.filter_by(category_id=cat_id).all()
            current_count = len(questions)
            
            # 如果是叶子分类（没有子分类），添加题目列表作为 items
            if not cat_data.get('children') or len(cat_data['children']) == 0:
                cat_data['items'] = [
                    {
                        'id': q.id,
                        'title': q.title,
                        'type': q.type,
                        'difficulty': q.difficulty
                    }
                    for q in questions
                ]
            
            # 递归处理子分类，累加子分类的题目数
            total_count = current_count
            for child in cat_data.get('children', []):
                child_cat = Category.query.get(child['id'])
                if child_cat:
                    total_count += count_questions(child, child_cat.id)
            
            # question_count 是当前分类的题目数
            cat_data['question_count'] = current_count
            # total_question_count 是包括子分类的总数
            cat_data['total_question_count'] = total_count
            return total_count
        
        for cat_data in root_categories:
            root_cat = Category.query.get(cat_data['id'])
            if root_cat:
                count_questions(cat_data, root_cat.id)
        
        result = root_categories
        
        # 缓存5分钟
        cache.set(cache_key, result, 300)
        
        return jsonify({"success": True, "data": result, "cached": False})
    except Exception as e:
        logger.error(f"获取分类列表失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@question_bank_bp.route("/questions", methods=["GET"])
def get_questions():
    """获取题目列表"""
    try:
        category_id = request.args.get("category_id", type=int)
        tag = request.args.get("tag")
        difficulty = request.args.get("difficulty", type=int)
        search = request.args.get("search", "").strip()
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 20, type=int)
        
        # 构建查询
        query = Question.query
        
        # 分类筛选
        if category_id:
            # 包括子分类
            category_ids = [category_id]
            children = Category.query.filter_by(parent_id=category_id).all()
            category_ids.extend([c.id for c in children])
            query = query.filter(Question.category_id.in_(category_ids))
        
        # 标签筛选
        if tag:
            tag_obj = Tag.query.filter_by(name=tag).first()
            if tag_obj:
                query = query.filter(Question.tags.contains(tag_obj))
        
        # 难度筛选
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        # 搜索
        if search:
            query = query.filter(
                db.or_(
                    Question.title.like(f"%{search}%"),
                    Question.content.like(f"%{search}%")
                )
            )
        
        # 总数
        total = query.count()
        
        # 分页
        questions = query.order_by(Question.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        result = [q.to_dict(include_answer=False) for q in questions]
        
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


@question_bank_bp.route("/questions/<int:question_id>", methods=["GET"])
def get_question(question_id):
    """获取题目详情"""
    try:
        show_answer = request.args.get("show_answer", "false").lower() == "true"
        
        question = Question.query.get_or_404(question_id)
        
        result = question.to_dict(include_answer=show_answer)
        
        # 获取相关文章
        related_articles = []
        relations = question.article_relations.all() if hasattr(question.article_relations, "all") else question.article_relations
        for relation in relations:
            article = relation.article
            related_articles.append({
                "id": article.id,
                "title": article.title,
                "description": article.description,
                "category_id": article.category_id,
                "category": article.category.name if article.category else None
            })
        result['related_articles'] = related_articles
        
        # 获取相邻题目（同分类）
        prev_question = Question.query.filter(
            Question.category_id == question.category_id,
            Question.id < question_id
        ).order_by(Question.id.desc()).first()
        
        next_question = Question.query.filter(
            Question.category_id == question.category_id,
            Question.id > question_id
        ).order_by(Question.id.asc()).first()
        
        result['navigation'] = {
            "prev": prev_question.id if prev_question else None,
            "next": next_question.id if next_question else None
        }
        
        return jsonify({"success": True, "data": result})
    except Exception as e:
        logger.error(f"获取题目详情失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@question_bank_bp.route("/questions/<int:question_id>/favorite", methods=["POST"])
@login_required
def toggle_favorite(question_id):
    """收藏/取消收藏题目"""
    try:
        # 获取用户ID（从token中）
        from auth.extensions import wx_auth
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"success": False, "error": "未提供认证token"}), 401
        
        result = wx_auth.verify_token(token)
        if result.get("code") != 200:
            return jsonify({"success": False, "error": "无效的token"}), 401
        
        user_id = result.get("user_id")
        question = Question.query.get_or_404(question_id)
        
        # 检查是否已收藏
        favorite = QuestionFavorite.query.filter_by(
            user_id=user_id,
            question_id=question_id
        ).first()
        
        if favorite:
            # 取消收藏
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({"success": True, "data": {"favorited": False}})
        else:
            # 添加收藏
            favorite = QuestionFavorite(user_id=user_id, question_id=question_id)
            db.session.add(favorite)
            db.session.commit()
            return jsonify({"success": True, "data": {"favorited": True}})
    except Exception as e:
        logger.error(f"收藏操作失败: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@question_bank_bp.route("/questions/<int:question_id>/favorite", methods=["GET"])
@login_required
def check_favorite(question_id):
    """检查是否已收藏"""
    try:
        from auth.extensions import wx_auth
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"success": False, "error": "未提供认证token"}), 401
        
        result = wx_auth.verify_token(token)
        if result.get("code") != 200:
            return jsonify({"success": False, "error": "无效的token"}), 401
        
        user_id = result.get("user_id")
        favorite = QuestionFavorite.query.filter_by(
            user_id=user_id,
            question_id=question_id
        ).first()
        
        return jsonify({"success": True, "data": {"favorited": favorite is not None}})
    except Exception as e:
        logger.error(f"检查收藏状态失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@question_bank_bp.route("/favorites", methods=["GET"])
@login_required
def get_favorites():
    """获取当前用户的收藏列表"""
    try:
        from auth.extensions import wx_auth
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"success": False, "error": "未提供认证token"}), 401
        
        result = wx_auth.verify_token(token)
        if result.get("code") != 200:
            return jsonify({"success": False, "error": "无效的token"}), 401
        
        user_id = result.get("user_id")
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 20, type=int)
        
        # 获取收藏的题目ID列表
        favorites = QuestionFavorite.query.filter_by(user_id=user_id)\
            .order_by(QuestionFavorite.created_at.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size).all()
        
        total = QuestionFavorite.query.filter_by(user_id=user_id).count()
        
        # 获取题目详情
        question_ids = [f.question_id for f in favorites]
        questions = Question.query.filter(Question.id.in_(question_ids)).all()
        
        # 构建题目字典，保持顺序
        question_dict = {q.id: q.to_dict() for q in questions}
        result = []
        for favorite in favorites:
            if favorite.question_id in question_dict:
                question_data = question_dict[favorite.question_id]
                question_data['favorited_at'] = favorite.created_at.isoformat() if favorite.created_at else None
                result.append(question_data)
        
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
        logger.error(f"获取收藏列表失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@question_bank_bp.route("/tags", methods=["GET"])
def get_tags():
    """获取标签列表"""
    try:
        tags = Tag.query.order_by(Tag.count.desc(), Tag.name).all()
        result = [tag.to_dict() for tag in tags]
        return jsonify({"success": True, "data": result})
    except Exception as e:
        logger.error(f"获取标签列表失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@question_bank_bp.route("/search", methods=["GET"])
def search_questions():
    """搜索题目和标签"""
    try:
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"success": False, "error": "搜索关键词不能为空"}), 400
        
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 20, type=int)
        
        # 搜索题目
        questions_query = Question.query.filter(
            db.or_(
                Question.title.like(f"%{query}%"),
                Question.content.like(f"%{query}%")
            )
        )
        
        total = questions_query.count()
        questions = questions_query.order_by(Question.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # 搜索标签
        tags = Tag.query.filter(Tag.name.like(f"%{query}%")).limit(10).all()
        
        result = {
            "questions": [q.to_dict(include_answer=False) for q in questions],
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


