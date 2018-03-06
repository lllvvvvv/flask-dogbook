from flask import jsonify,request,url_for,g,current_app
from . import api
from .. import db
from ..models import Post,Permission,Comment
from .decorators import permission_required

@api.route('/posts/<int:id>/comments')
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    page = request.args.get('page',1,type=int)
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page,per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],error_out=False

    )
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments',id=id,page=page+1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_post_comments',id=id,page=page-1)
    return jsonify({
        'comments':[comment.to_json() for comment in comments],
        'prev':prev,
        'next':next,
        'count':pagination.total,
    })