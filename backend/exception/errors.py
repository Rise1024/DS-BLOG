from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError

class APIError(Exception):
    def __init__(self, message, code=400, data=None):
        super().__init__()
        self.message = message
        self.code = code
        self.data = data

class AuthError(APIError):
    def __init__(self, message="认证失败", code=401):
        super().__init__(message=message, code=code)

class PermissionError(APIError):
    def __init__(self, message="权限不足", code=403):
        super().__init__(message=message, code=code)

class ValidationError(APIError):
    def __init__(self, message="参数验证失败", code=400):
        super().__init__(message=message, code=code)

class NotFoundError(APIError):
    def __init__(self, message="资源不存在", code=404):
        super().__init__(message=message, code=code)

def init_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = {
            'code': error.code,
            'message': error.message,
            'data': error.data
        }
        return jsonify(response), error.code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        response = {
            'code': error.code,
            'message': error.description,
            'data': None
        }
        return jsonify(response), error.code

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        response = {
            'code': 500,
            'message': '数据库操作失败',
            'data': None
        }
        app.logger.error(f'Database error: {str(error)}')
        return jsonify(response), 500

    @app.errorhandler(Exception)
    def handle_general_error(error):
        response = {
            'code': 500,
            'message': '服务器内部错误',
            'data': None
        }
        app.logger.error(f'Unexpected error: {str(error)}')
        return jsonify(response), 500