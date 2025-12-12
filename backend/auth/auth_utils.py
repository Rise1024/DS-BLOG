from functools import wraps
from flask import request, jsonify
from model.database import User, UserToken
from auth.extensions import wx_auth
from config.config import logger
from datetime import datetime


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request_source = request.headers.get("X-Request-Source")
        if request_source == "web":
            return f(*args, **kwargs)
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "未提供认证token"}), 401

        result = wx_auth.verify_token(token)
        logger.info(f"Token验证结果: {result}")
        if result.get("code") != 200:
            return jsonify({"error": "无效的token"}), 401

        return f(*args, **kwargs)

    return decorated_function


def verify_admin_token(token):
    """验证管理员token"""
    if not token:
        return None
    
    # 查找token
    user_token = UserToken.query.filter_by(token=token).first()
    if not user_token:
        return None
    
    # 检查是否过期
    if user_token.expires_at < datetime.now():
        return None
    
    # 获取用户
    user = User.query.get(user_token.user_id)
    if not user or user.role != "admin":
        return None
    
    return user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"success": False, "error": "未提供认证令牌"}), 401

        # 先尝试验证管理员token（Web后台登录）
        user = verify_admin_token(token)
        if user:
            # 管理员token验证成功
            return f(*args, **kwargs)
        
        # 如果不是管理员token，尝试微信token验证（小程序）
        request_source = request.headers.get("X-Request-Source")
        if request_source == "web":
            return jsonify({"success": False, "error": "认证失败"}), 401
            
        result = wx_auth.verify_token(token)
        if result.get("code") != 200:
            return jsonify({"success": False, "error": "认证失败"}), 401

        user = User.query.get(result["user_id"])
        if not user or user.role != "admin":
            return jsonify({"success": False, "error": "需要管理员权限"}), 401

        return f(*args, **kwargs)

    return decorated_function
