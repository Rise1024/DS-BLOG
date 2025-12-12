from flask import Blueprint, request, jsonify
from auth.extensions import wx_auth
from config.config import logger

# 创建蓝图
login_bp = Blueprint("login", __name__, url_prefix="/api/v1")


@login_bp.route("/login", methods=["POST"])
def login():
    try:
        code = request.json.get("code")
        user_info = request.json.get("userInfo")

        if not code or not user_info:
            return jsonify({"error": "缺少必要的登录信息"}), 400

        # 获取微信session信息
        session_info = wx_auth.get_wx_session_info(code)

        # 获取或创建用户
        user = wx_auth.get_or_create_user(session_info["openid"], user_info)

        # 创建token
        token, expires_at = wx_auth.create_token(user.id)

        return jsonify(
            {
                "success": True,
                "token": token,
                "userId": user.id,
                "role": user.role,
                "expires_at": expires_at.isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"登录过程中发生错误: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
