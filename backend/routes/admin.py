from flask import Blueprint, request, jsonify
from auth.auth_utils import admin_required
from model.models import User

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/api/users", methods=["GET"])
@admin_required
def get_users():
    return jsonify({"success": True, "users": User.getAll()}), 200


@admin_bp.route("/api/user/role", methods=["PUT"])
@admin_required
def update_user_role():
    data = request.get_json()
    user_id = data.get("userId")
    new_role = data.get("role")

    if not user_id or not new_role:
        return jsonify({"success": False, "message": "缺少必要参数"}), 400

    if new_role not in ["admin", "user"]:
        return jsonify({"success": False, "message": "无效的角色值"}), 400

    # 直接操作Redis哈希表更新角色
    user = User.updateRole(user_id, new_role)
    return jsonify({"success": True})
