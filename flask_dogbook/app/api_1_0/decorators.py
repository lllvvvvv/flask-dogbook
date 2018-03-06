#coding=utf-8
from functools import wraps
from errors import fordibben
from flask import jsonify

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_funtion(*args,**kwargs):
            if not g.current_user.can(permission):
                return fordibben(u'账号权限不足')
            return f(*args,**kwargs)
        return decorated_funtion
    return decorator
