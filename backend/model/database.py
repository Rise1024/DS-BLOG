"""
数据库模型定义
使用SQLAlchemy ORM
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()


def get_china_time():
    """获取北京时间"""
    return datetime.now(pytz.timezone("Asia/Shanghai"))


# 用户表
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(128), unique=True, nullable=True, index=True)  # 微信openid，可为空
    username = db.Column(db.String(64), unique=True, nullable=True, index=True)  # 用户名（用于后台登录）
    password_hash = db.Column(db.String(128), nullable=True)  # 密码哈希（用于后台登录）
    user_type = db.Column(db.String(16), default='wechat', nullable=False)  # wechat: 微信用户, web: 网页用户
    nickname = db.Column(db.String(64))
    avatar_url = db.Column(db.String(256))
    role = db.Column(db.String(64), default='user', nullable=False)  # user, admin
    created_at = db.Column(db.DateTime, default=get_china_time, nullable=False)
    last_login = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time, nullable=False)
    
    # 关系
    tokens = db.relationship('UserToken', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('QuestionFavorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_password=False):
        data = {
            'id': self.id,
            'openid': self.openid,
            'username': self.username,
            'user_type': self.user_type,
            'nickname': self.nickname,
            'avatar_url': self.avatar_url,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        if include_password:
            data['password_hash'] = self.password_hash
        return data
    
    def set_password(self, password):
        """设置密码（自动哈希）"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        from werkzeug.security import check_password_hash
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)


# 用户令牌表
class UserToken(db.Model):
    __tablename__ = 'user_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token = db.Column(db.String(256), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=get_china_time, nullable=False)


# 分类表（支持多级分类）
class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True, index=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=get_china_time, nullable=False)
    updated_at = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time, nullable=False)
    
    # 自引用关系
    parent = db.relationship('Category', remote_side=[id], backref='children')
    
    # 关系
    questions = db.relationship('Question', backref='category', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'question_count': self.questions.count() if self.questions else 0
        }


# 题目标签关联表（多对多）
question_tags = db.Table(
    'question_tags',
    db.Column('question_id', db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)


# 题目表
class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True, index=True)
    type = db.Column(db.String(20), nullable=False)  # 'short_answer', 'programming'
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)  # 题目内容（Markdown格式）
    answer = db.Column(db.Text, nullable=False)  # 答案（Markdown格式）
    explanation = db.Column(db.Text)  # 解析（Markdown格式）
    difficulty = db.Column(db.Integer, default=3, nullable=False)  # 1-5星
    created_at = db.Column(db.DateTime, default=get_china_time, nullable=False)
    updated_at = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time, nullable=False)
    
    # 关系
    tags = db.relationship('Tag', secondary=question_tags, backref='questions', lazy='dynamic')
    favorites = db.relationship('QuestionFavorite', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    article_relations = db.relationship('ArticleQuestionRelation', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_answer=False):
        relations = self.article_relations.all() if hasattr(self.article_relations, "all") else self.article_relations
        data = {
            'id': self.id,
            'category_id': self.category_id,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'difficulty': self.difficulty,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tags': [tag.name for tag in self.tags] if self.tags else [],
            'related_articles': [
                {
                    'id': relation.article.id,
                    'title': relation.article.title,
                    'category_id': relation.article.category_id,
                    'category': relation.article.category.name if relation.article.category else None
                }
                for relation in relations
            ]
        }
        if include_answer:
            data['answer'] = self.answer
            data['explanation'] = self.explanation
        return data


# 题目收藏表
class QuestionFavorite(db.Model):
    __tablename__ = 'question_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=get_china_time, nullable=False)
    
    # 唯一约束：一个用户只能收藏一次同一题目
    __table_args__ = (db.UniqueConstraint('user_id', 'question_id', name='uq_user_question_favorite'),)


# 标签表
class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    count = db.Column(db.Integer, default=0)  # 使用该标签的题目/文章数量
    created_at = db.Column(db.DateTime, default=get_china_time, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'count': self.count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# 文章表
class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)  # 摘要
    content = db.Column(db.Text, nullable=False)  # 文章内容（Markdown格式）
    category_id = db.Column(db.Integer, db.ForeignKey('blog_categories.id', ondelete='SET NULL'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=get_china_time, nullable=False)
    updated_at = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time, nullable=False)
    view_count = db.Column(db.Integer, default=0)
    order = db.Column(db.Integer, default=999999)
    
    # 关系
    category = db.relationship('BlogCategory', backref='articles', lazy='select')
    tags = db.relationship('Tag', secondary='article_tags', backref='articles', lazy='dynamic')
    question_relations = db.relationship('ArticleQuestionRelation', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_content=False):
        relations = self.question_relations.all() if hasattr(self.question_relations, "all") else self.question_relations
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category_id': self.category_id,
            'category': self.category.name if self.category else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'view_count': self.view_count,
            'order': self.order,
            'tags': [tag.name for tag in self.tags] if self.tags else [],
            'related_questions': [
                {
                    'id': relation.question.id,
                    'title': relation.question.title,
                    'type': relation.question.type,
                    'difficulty': relation.question.difficulty,
                    'tags': [tag.name for tag in relation.question.tags] if relation.question.tags else []
                }
                for relation in relations
            ]
        }
        if include_content:
            data['content'] = self.content
        return data


# 博客分类表（树形结构）
class BlogCategory(db.Model):
    __tablename__ = 'blog_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('blog_categories.id', ondelete='SET NULL'), nullable=True, index=True)
    description = db.Column(db.Text)  # 分类描述
    order = db.Column(db.Integer, default=0)  # 排序
    created_at = db.Column(db.DateTime, default=get_china_time, nullable=False)
    
    # 自引用关系
    parent = db.relationship('BlogCategory', remote_side=[id], backref='children')
    
    __table_args__ = (db.UniqueConstraint('parent_id', 'name', name='uq_blog_category_parent_name'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'description': self.description,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# 文章标签关联表（多对多）
article_tags = db.Table(
    'article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)


# 文章题目关联表
class ArticleQuestionRelation(db.Model):
    __tablename__ = 'article_question_relations'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=get_china_time, nullable=False)
    
    # 唯一约束：同一文章和题目只能关联一次
    __table_args__ = (db.UniqueConstraint('article_id', 'question_id', name='uq_article_question'),)


# 意见反馈表
class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    content = db.Column(db.Text, nullable=False)  # 反馈内容
    contact = db.Column(db.String(200))  # 联系方式（可选）
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, processed, closed
    created_at = db.Column(db.DateTime, default=get_china_time, nullable=False)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    # 关系
    user = db.relationship('User', backref='feedbacks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'contact': self.contact,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'user_nickname': self.user.nickname if self.user else None
        }

