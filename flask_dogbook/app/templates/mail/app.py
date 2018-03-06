#coding=utf-8
from flask import Flask,render_template,session,redirect,url_for,Request,flash
from flask_script import Manager,Shell
from flask_bootstrap import Bootstrap
import os
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
from flask_mail import Mail,Message
from threading import Thread

app = Flask(__name__)

app.config['SECRET_KEY'] = 'aaaaaaaaa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:lvcheng18@localhost/blog'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'lllvvvvvcheng@163.com'
app.config['MAIL_PASSWORD'] = 'lvcheng18'
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[新用户]'   #主题前缀
app.config['FLASKY_MAIL_SENDER'] = 'FLASKY admin <lllvvvvvcheng@163.com>'  #发件人
app.config['FLASKY_ADMIN'] = 'lllvvvvvcheng@163.com'

manager = Manager(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)
mail = Mail(app)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    users = db.relationship('User',backref = 'role',lazy = 'dynamic')

    def __repr__(self):
        return '<Role %r>' %self.name


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' %self.username



class NameForm(FlaskForm):
    name = StringField(u"请输入你的名字",validators=[DataRequired()])
    submit = SubmitField(u'提交')

def send_async_mail(app,msg):
    with app.app_context():
        mail.send(msg)


def make_shell_context():      #回调函数，在shell中直接导入对象
    return dict(app=app,db=db,User=User,Role=Role)
manager.add_command("shell",Shell(make_context=make_shell_context))


def send_mail(to,subject,template,**kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,
                  sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template+ '.txt',**kwargs)
    msg.html = render_template(template+ '.html',**kwargs)
    thr = Thread(target=send_async_mail,args=[app,msg])
    thr.start()
    return thr


@app.route('/',methods=['GET','POST'])
def username():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['know'] = False
            if app.config['FLASKY_ADMIN']:
                send_mail(app.config['FLASKY_ADMIN'],'new user','mail/template',user=user)
        else:
            session['know'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('username'))
    return render_template('name.html',name=session.get('name'),form=form,know=session.get('know',False))

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"),404

if __name__ == '__main__':
    manager.run()