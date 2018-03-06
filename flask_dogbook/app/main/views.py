# coding=utf-8
from flask import render_template, session, url_for, redirect, abort, flash, request, current_app, make_response
from app.decorators import admin_required, permission_required
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, Change_AvatarForm, PostForm, CommentForm
from .. import db
from ..models import User, Permission, Role, Post, Comment
from flask_login import login_required, current_user


@main.route('/<name>', methods=['GET', 'POST'])
def username():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['know'] = False
            # if app.config['FLASKY_ADMIN']:
            #  send_mail(app.config['FLASKY_ADMIN'],'new user','mail/template',user=user)
        else:
            session['know'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.username'))
    return render_template('name.html', name=session.get('name'), form=form, know=session.get('know', False))


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "aa"


@main.route('/mo')
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def ffr():
    return "ccc"


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(u"您的资料已更新")
        return redirect(url_for('.user', username=current_user.username))
    form.name = current_user.name
    form.location = current_user.location
    form.about_me = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash(u'此简介已更新')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role
    form.name.dara = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/change-avatar', methods=['GET', 'POST'])
@login_required
def change_avatar():
    form = Change_AvatarForm()
    if form.validate_on_submit():
        avatar = request.files['avatar']
        fname = avatar.filename
        UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
        ALLOWED_FORMAT = ['png', 'pdf', 'jpeg', 'gif', 'jpg', 'JPG']
        flag = '.' in fname and fname.rsplit('.', 1)[1] in ALLOWED_FORMAT
        if not flag:
            flash(u'文件格式错误')
            return redirect(url_for('.change_avatar'))
        avatar.save(u'{}{}_{}'.format(UPLOAD_FOLDER, current_user.username, fname))
        current_user.avatar = u'/static/avatar/{}_{}'.format(current_user.username, fname)
        db.session.add(current_user)
        flash(u'头像已更新')
        return redirect(url_for('.user', username=current_user.username))
    return render_template('avatar.html', form=form)


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, show_followed=show_followed, pagination=pagination)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp



@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash(u'博客修改成功')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')  # 关注用户
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'错误的用户')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(u'你已经关注他了')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash(u'成功关注 {}'.format(username))
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')  # 取消关注
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'错误的用户')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash(u'你没有关注他了')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash(u'成功取消关注{}'.format(username))
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')  # 粉丝总人数
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'错误的用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False
    )
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title=u"你的粉丝",
                           endpoint='.followers', pagination=pagination, follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'错误的用户')
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWING_PER_PAGE'],
        error_out=False
    )
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title=u'你关注的人',
                           endpoint='.followed-by', pagination=pagination, follows=follows)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash(u'评论成功')
        return redirect(url_for('main.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagenation = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagenation.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagenation=pagenation)

@main.route('/moderate')#管理评论
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page',1,type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html',comments=comments,
                           pagination=pagination,page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page',1,type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled=True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page',1,type=int)))