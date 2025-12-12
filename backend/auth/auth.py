import os
import requests
import jwt
from datetime import datetime, timedelta
from model.database import db, User, UserToken
from config.config import logger


class WXAuthError(Exception):
    pass


class Auth:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.wx_auth_url = "https://api.weixin.qq.com/sns/jscode2session"
        self.jwt_secret = os.environ.get("JWT_SECRET_KEY") or "your-jwt-secret-key"

    def get_wx_session_info(self, code):
        """获取微信session信息"""
        try:
            response = requests.get(
                self.wx_auth_url,
                params={
                    "appid": self.app_id,
                    "secret": self.app_secret,
                    "js_code": code,
                    "grant_type": "authorization_code",
                },
            )
            data = response.json()

            if "errcode" in data:
                raise WXAuthError(f"微信认证失败：{data['errmsg']}")

            return data
        except Exception as e:
            raise WXAuthError(f"微信认证请求失败：{str(e)}")

    def get_or_create_user(self, openid, user_info):
        """获取或创建用户 (SQLite版本)"""
        user = User.query.filter_by(openid=openid).first()
        if not user:
            user = User(
                openid=openid,
                nickname=user_info.get("nickName"),
                avatar_url=user_info.get("avatarUrl"),
                role="user",
                user_type="wechat"  # 微信用户
            )
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
        else:
            # 更新最后登录时间
            user.last_login = datetime.utcnow()
            db.session.commit()
        return user

    def verify_token(self, token):
        """验证JWT token (SQLite版本)"""
        try:
            # 从数据库获取 token 信息
            user_token = UserToken.query.filter_by(token=token).first()
            if not user_token:
                return {"error": "token_not_found", "code": 401}

            # 检查是否过期
            if user_token.expires_at < datetime.utcnow():
                return {"error": "token_expired", "code": 401}

            # 验证 JWT token
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
                stored_user_id = user_token.user_id
                payload_user_id = payload["user_id"]
                
                # 验证 user_id 一致性
                if payload_user_id != stored_user_id:
                    return {"error": "token_user_mismatch", "code": 401}
                return {"user_id": payload["user_id"], "code": 200}
            except jwt.ExpiredSignatureError:
                return {"error": "token_expired", "code": 401}
            except jwt.InvalidTokenError:
                return {"error": "token_invalid", "code": 401}
        except Exception as e:
            logger.error(f"Token 验证异常: {str(e)}")
            return {"error": "verification_failed", "code": 401}

    def create_token(self, user_id):
        """创建令牌 (SQLite版本)"""
        expires_at = datetime.utcnow() + timedelta(days=7)
        token = jwt.encode(
            {"user_id": user_id, "exp": expires_at}, self.jwt_secret, algorithm="HS256"
        )
        
        # 保存到数据库
        user_token = UserToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        db.session.add(user_token)
        db.session.commit()
        
        return token, expires_at
