"""
意见反馈相关API路由
"""
from flask import Blueprint, request, jsonify
from model.database import db, Feedback
from auth.auth_utils import login_required
from config.config import logger

feedback_bp = Blueprint("feedback", __name__, url_prefix="/api/v1/feedback")


@feedback_bp.route("", methods=["POST"])
@login_required
def create_feedback():
    """创建意见反馈"""
    try:
        from auth.extensions import wx_auth
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"success": False, "error": "未提供认证token"}), 401
        
        result = wx_auth.verify_token(token)
        if result.get("code") != 200:
            return jsonify({"success": False, "error": "无效的token"}), 401
        
        user_id = result.get("user_id")
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "请求数据不能为空"}), 400
        
        content = data.get("content", "").strip()
        if not content:
            return jsonify({"success": False, "error": "反馈内容不能为空"}), 400
        
        contact = data.get("contact", "").strip()
        
        # 创建反馈记录
        feedback = Feedback(
            user_id=user_id,
            content=content,
            contact=contact if contact else None,
            status='pending'
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        logger.info(f"用户 {user_id} 提交了意见反馈，ID: {feedback.id}")
        
        return jsonify({
            "success": True,
            "data": {
                "id": feedback.id,
                "message": "反馈提交成功，感谢您的反馈！"
            }
        }), 201
        
    except Exception as e:
        logger.error(f"创建反馈失败: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

