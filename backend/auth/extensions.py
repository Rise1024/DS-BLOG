from auth.auth import Auth
from flask import current_app

wx_auth = None

def init_auth():
    global wx_auth
    wx_auth = Auth(
        app_id=current_app.config['WECHAT_APP_ID'],
        app_secret=current_app.config['WECHAT_APP_SECRET']
    )
