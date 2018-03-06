# coding=utf-8
from flask import render_template, redirect, url_for, request, flash, session
from . import auth
from flask_login import login_required, logout_user, fresh_login_required
from ..models import User
from .forms import LoginForm, RegisterForm, Change_PasswordForm, Forget_PasswordForm, Reset_PasswordForm,Reset_MailForm
from flask_login import login_user
from .. import db
from flask_login import current_user
from ..email import send_email



@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
                return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remeber.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'错误的用户名或者密码')
    return render_template('auth/login.html', form=form)


@auth.route('/secret')
@login_required
def sercret():
    return '只有登陆的人能允许访问'


@auth.route('/logout', methods=['GET', 'POST'])
@fresh_login_required
def logout():
    logout_user()
    flash(u'已经退出登陆')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'confirm your account',
                   'auth/email/confirm', user=user, token=token)
        flash(u'验证邮件已发送')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash(u'你需要去邮箱验证你的账号')
    else:
        flash((u'验证页面无效或已经到期'))
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', user=current_user)


@auth.route('/confirm')
@login_required
def resend_confirm():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'confirm your account',
               'auth/email/confirm', user=current_user, token=token)
    flash(u'验证邮件已发送')
    return redirect(url_for('main.index'))


@auth.route('/change/password', methods=['GET', 'POST'])
@login_required
def Change_Password():
    form = Change_PasswordForm()
    if form.validate_on_submit():
        if current_user.verity_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'密码重设成功')
        else:
            flash(u'重设失败')

        return redirect(url_for('main.index'))
    return render_template('auth/changpassword.html', form=form)


@auth.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    form = Forget_PasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.username == form.username.data:
            token = user.generate_reset_token()
            send_email(user.email, u'修改密码',
                       'auth/email/forget_password', user=user, token=token)
            flash(u'验证邮件已发送')
    return render_template('auth/forgetpassword.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = Reset_PasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash(u'用户名不存在')
            return redirect(url_for('main.index'))
            print '修改'
        if user.reset_password(token,form.new_password.data):
            flash(u'密码修改成功')
            return redirect(url_for('auth.login'))
            print '修改成本'
    return render_template('auth/reset.html', form=form)

@auth.route('/reset_mail',methods = ['GET','POST'])
@login_required
def reset_mail():
    form = Reset_MailForm()
    if form.validate_on_submit():
        if current_user.verity_password(form.password.data):
            new_email = form.email2.data
            token = current_user.change_mail(new_email)
            send_email(current_user.email,u'修改邮箱',
                       'auth/email/change_email', user=current_user, token=token)
            flash(u'邮件发送成功')
            return redirect(url_for('auth.login'))
        else:
            flash(u'密码或邮箱错误')
    return render_template('auth/reset_mail.html',form=form)

@auth.route('/change_mail/<token>')
@login_required
def change_mail(token):
    if current_user.reset_mail(token):
        flash(u'邮箱修改成功')
    else:
        flash(u'修改失败')
    return redirect(url_for('auth.login'))

