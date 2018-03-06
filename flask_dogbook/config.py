#coding=utf-8
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'AAAAA'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASKY_MAIL_SENDER = 'lllvvvvvcheng@163.com'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or 'lllvvvvvcheng@163.com'
    FLASKY_MAIL_SUBJECT_PREFIX = u''
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getcwd() + '/app/static/avatar/'
    FLASKY_POSTS_PER_PAGE = 10
    FLASKY_FOLLOWERS_PER_PAGE = 10
    FLASKY_FOLLOWING_PER_PAGE =10
    FLASKY_COMMENTS_PER_PAGE = 10
    FLASKY_POSTS_PER_PAGE = 10
    FLASKY_COMMENTS_PER_PAGE = 10

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DUBUG =True
    MAIL_SERVER  ='smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'lllvvvvvcheng@163.com'
    MAIL_PASSWORD = 'lvcheng18'
    SQLALCHEMY_DATABASE_URI= 'mysql://root:lvcheng18@localhost/blog'

class TestingConfig(Config):
    TESTING = True
   # SQLALCHEMY_DATABASE_URI = 'mysql://root:lvcheng18@localhost/dogbook'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:lvcheng18@localhost/blog'

config = {
    'development' : DevelopmentConfig,
    'testing' : TestingConfig,
    'production' : ProductionConfig,

    'default' : DevelopmentConfig
}
