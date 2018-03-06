#coding=utf-8
from flask import jsonify,request,g

from . import api
from app.exceptions import ValidationError

def fordibben(message):#403 禁止
    response = jsonify({'error':'forbidden','message':message})
    response.status_code = 403
    return response

def unauthorized(message):#401 未授权
    response = jsonify({'error':'unauthorized','message':message})
    response.status_code = 401
    return response

def bad_request(message): #400 坏请求
    response = jsonify({'errror':'bad request','message':message})
    response.status_code = 400
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.atgs[0])
