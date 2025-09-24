from functools import wraps
from flask import request, jsonify
from model.models import User
from auth.extensions import wx_auth
from config.config import logger


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


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request_source = request.headers.get("X-Request-Source")
        if request_source == "web":
            return f(*args, **kwargs)
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"success": False, "message": "未提供认证令牌"}), 401

        result = wx_auth.verify_token(token)
        if result.get("code") != 200:
            return jsonify({"success": False, "message": "认证失败"}), 401

        user = User.query.get(result["user_id"])
        if not user or user.role != "admin":
            return jsonify({"success": False, "message": "需要管理员权限"}), 401

        return f(*args, **kwargs)

    return decorated_function
