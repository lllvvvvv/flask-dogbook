# coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[DataRequired(), Length(8, 16), ])
    remeber = BooleanField(u'记住账号')
    submit = SubmitField(u'登陆')


class RegisterForm(FlaskForm):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 16)])
    password = PasswordField(u'密码(至少八位)', validators=[DataRequired(), Length(8, 16),
                                                      EqualTo('password2', message=u'两次密码必须相同')])
    password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            return ValidationError(u'邮箱已注册，请重新输入')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            return ValidationError(u'用户名已注册，请重新输入')


class Change_PasswordForm(FlaskForm):
    old_password = PasswordField(u'旧密码', validators=[DataRequired(), Length(8 - 16)])
    new_password = PasswordField(u'新密码', validators=[DataRequired(), Length(8 - 16),
                                                     EqualTo('new_password2', message=u'两次密码必须相同')])
    new_password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'提交')

    def validate_password(self, old_password, newpassword):
        if old_password == newpassword:
            return ValidationError(u'新密码与原密码相同，请使用不同密码')

class Forget_PasswordForm(FlaskForm):
    username = StringField(u'用户名',validators=[DataRequired()])
    email = StringField(u'邮箱',validators=[DataRequired(),Email()])
    submit = SubmitField(u'提交')

class Reset_PasswordForm(FlaskForm):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    new_password = PasswordField(u'新密码', validators=[DataRequired(), Length(8 - 16),
                                                     EqualTo('new_password2', message=u'两次密码必须相同')])
    new_password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'提交')

class Reset_MailForm(FlaskForm):
    password = PasswordField(u'密码', validators=[DataRequired(), Length(8, 16), ])
    email2 = StringField(u'新邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField(u'提交')