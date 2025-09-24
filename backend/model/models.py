import redis
import json
import pytz
from datetime import datetime

# Redis 连接配置


def init_redis(app):
    global redis_conn
    redis_conn = redis.Redis(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        db=app.config["REDIS_DB"],
        password=app.config.get("REDIS_PASSWORD", None),
        decode_responses=True,
    )


# 全局键名常量
USER_ID_SEQ = "global:user_id"
HISTORY_ID_SEQ = "global:history_id"
FEEDBACK_ID_SEQ = "global:feedback_id"


def get_china_time():
    """获取北京时间（ISO格式字符串）"""
    return datetime.now(pytz.timezone("Asia/Shanghai")).isoformat()


class User:
    def __init__(self, id, openid, nickname, avatar_url, role, created_at, last_login):
        self.id = id
        self.openid = openid
        self.nickname = nickname
        self.avatar_url = avatar_url
        self.role = role
        self.created_at = created_at
        self.last_login = last_login

    @classmethod
    def create(cls, openid, nickname, avatar_url, role="user"):
        """创建新用户"""
        user_id = redis_conn.incr(USER_ID_SEQ)
        user_data = {
            "id": user_id,
            "openid": openid,
            "nickname": nickname,
            "avatar_url": avatar_url,
            "role": role,
            "created_at": get_china_time(),
            "last_login": get_china_time(),
        }

        pipeline = redis_conn.pipeline()
        pipeline.hset(f"user:{user_id}", mapping=user_data)
        pipeline.set(f"user:openid:{openid}", user_id)
        pipeline.execute()
        return user_id

    @classmethod
    def get(cls, user_id):
        """根据ID获取用户对象"""
        user_data = redis_conn.hgetall(f"user:{user_id}")
        if user_data:
            # 转换数据类型
            user_data["id"] = int(user_data["id"])
            user_data["openid"] = str(user_data["openid"])
            user_data["nickname"] = str(user_data["nickname"])
            user_data["avatar_url"] = str(user_data["avatar_url"])
            user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
            user_data["last_login"] = datetime.fromisoformat(user_data["last_login"])
            return cls(**user_data)
        return None

    @classmethod
    def getAll(self):
        users = []
        for key in redis_conn.scan_iter("user:*"):
            if key.count(":") == 1:
                user_id = key.split(":")[1]
                user = User.get(user_id)
                if user:
                    users.append(
                        {
                            "id": user.id,
                            "openid": user.openid,
                            "nickname": user.nickname,
                            "avatar_url": user.avatar_url,
                            "role": user.role,
                            "created_at": user.created_at.isoformat(),
                            "last_login": user.last_login.isoformat(),
                        }
                    )
        return users

    @classmethod
    def updateRole(self, user_id, role):
        user = User.get(user_id)
        if user:
            user.role = role
            pipeline = redis_conn.pipeline()
            pipeline.hset(f"user:{user_id}", mapping=user)
        return user

    @classmethod
    def get_by_openid(cls, openid):
        """通过openid获取用户"""
        user_id = redis_conn.get(f"user:openid:{openid}")
        return cls.get(user_id) if user_id else None


class UserToken:
    @classmethod
    def create(cls, user_id, token, expires_at):
        """创建用户令牌"""
        pipeline = redis_conn.pipeline()
        pipeline.hset(
            f"token:{token}",
            mapping={
                "user_id": user_id,
                "token": token,
                "expires_at": expires_at.isoformat(),
                "created_at": get_china_time(),
            },
        )
        pipeline.sadd(f"user:{user_id}:tokens", token)
        pipeline.execute()

    @classmethod
    def get(cls, token):
        """获取令牌详情"""
        return redis_conn.hgetall(f"token:{token}")


class HistoryRecord:
    @classmethod
    def create(cls, user_id, article_id, style, image_urls):
        """创建历史记录"""
        history_id = redis_conn.incr(HISTORY_ID_SEQ)
        record_data = {
            "id": history_id,
            "user_id": user_id,
            "article_id": article_id,
            "style": style,
            "image_urls": json.dumps(image_urls),
            "created_at": get_china_time(),
            "is_deleted": "0",
        }

        pipeline = redis_conn.pipeline()
        pipeline.hset(f"history:{history_id}", mapping=record_data)
        pipeline.zadd(
            f"user:{user_id}:history", {history_id: datetime.now().timestamp()}
        )
        pipeline.execute()
        return history_id

    @classmethod
    def get_user_history(cls, user_id):
        """获取用户历史记录"""
        history_ids = redis_conn.zrevrange(f"user:{user_id}:history", 0, -1)
        return [redis_conn.hgetall(f"history:{hid}") for hid in history_ids]


class Feedback:
    @classmethod
    def create(cls, user_id, content, contact=None):
        """创建反馈记录"""
        feedback_id = redis_conn.incr(FEEDBACK_ID_SEQ)
        feedback_data = {
            "id": feedback_id,
            "user_id": user_id,
            "content": content,
            "contact": contact or "",
            "created_at": get_china_time(),
        }

        pipeline = redis_conn.pipeline()
        pipeline.hset(f"feedback:{feedback_id}", mapping=feedback_data)
        pipeline.sadd(f"user:{user_id}:feedbacks", feedback_id)
        pipeline.execute()
        return feedback_id


class UserStatistics:
    @classmethod
    def update_stats(cls, date, stats_data):
        """更新用户统计信息"""
        key = f"stats:{date.isoformat()}"
        pipeline = redis_conn.pipeline()
        pipeline.hincrby(
            key, "total_generations", stats_data.get("total_generations", 0)
        )
        pipeline.hincrby(key, "total_images", stats_data.get("total_images", 0))
        pipeline.hsetnx(key, "created_at", get_china_time())
        pipeline.hset(key, "updated_at", get_china_time())
        pipeline.execute()


class Rss:
    @classmethod
    def get_rss_data(cls, rss_name):
        """获取RSS数据"""
        key = f"rss:data:{rss_name}"
        return redis_conn.get(key)
