# coding=utf-8
from wtforms import SubmitField, StringField, TextAreaField,BooleanField,SelectField,FileField
from wtforms.validators import DataRequired, Length,Email,ValidationError
from flask_wtf import FlaskForm
from app.models import Role,User
from flask_pagedown.fields import PageDownField


class NameForm(FlaskForm):
    name = StringField(u"请输入你的名字", validators=[DataRequired()])
    submit = SubmitField(u'提交')


class EditProfileForm(FlaskForm):
    name = StringField(u"真实名字", validators=[Length(0, 64)])
    location = StringField(u"位置", validators=[Length(0, 64)])
    about_me = TextAreaField(u"简介")
    sbumit = SubmitField(u'提交')

class EditProfileAdminForm(FlaskForm):
    email = StringField(u'邮箱',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField(u'用户名',validators=[DataRequired(),Length(1,64)])
    confirmed = BooleanField('confirmed')
    role = SelectField('Role',coerce=int)
    name = StringField(u'真实姓字',validators=[Length(0,64)])
    location = StringField(u'位置',validators=[Length(0,64)])
    about_me = TextAreaField(u"简介")
    sbumit = SubmitField(u'提交')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self,field):
        if field.data != self.user.email and \
            User.query.filter_by(email=field.data).first():
            raise ValidationError('email alread register')

    def validate_username(self,field):
        if field.data != self.username and \
            User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')

class Change_AvatarForm(FlaskForm):
    avatar = FileField(u'头像')
    sbumit = SubmitField(u'提交')

#博客文章表单
class PostForm(FlaskForm):
    body = PageDownField(u"有什么新鲜事想告诉大家？",validators=[DataRequired()])
    sbumit = SubmitField(u'提交')


class CommentForm(FlaskForm):#评论表单
    body = StringField(u'',validators=[DataRequired()])
    submit = SubmitField(u'提交')