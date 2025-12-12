"""
数据库初始化脚本
创建表结构和初始化示例数据
"""
import os
from datetime import datetime
import pytz
from model.database import db
from model.database import (
    User, Category, Question, Tag, Article, 
    ArticleQuestionRelation, QuestionFavorite, UserToken
)
from config.config import get_config


def init_sample_data():
    """初始化示例数据（已移除，如需初始化数据请使用独立脚本）"""
    pass


def init_admin_user():
    """初始化管理员用户（如果不存在）"""
    from model.database import User
    
    # 检查是否已存在管理员用户
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        print("管理员用户已存在")
        return admin_user
    
    # 创建默认管理员用户
    admin_user = User(
        username='admin',
        nickname='管理员',
        role='admin',
        user_type='web',  # 网页用户
        openid=None  # 后台登录不需要openid
    )
    admin_user.set_password('admin123')  # 默认密码
    
    db.session.add(admin_user)
    db.session.commit()
    
    print("✅ 已创建默认管理员用户: admin / admin123")
    print("⚠️  警告: 生产环境请立即修改默认密码！")
    
    return admin_user


def get_china_time():
    """获取北京时间"""
    return datetime.now(pytz.timezone("Asia/Shanghai"))


def init_database(app):
    """初始化数据库"""
    # 确保数据目录存在
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # 设置数据库URI
    db_path = os.path.join(data_dir, 'ds_blog.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化数据库
    db.init_app(app)
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 初始化管理员用户（如果不存在）
        init_admin_user()


