from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, current_app, abort)
from flask_login import login_required, current_user
import os, uuid
from werkzeug.utils import secure_filename
from app.models import db, Post, Comment, User, Notification
from app.forms import PostForm, CommentForm

feed_bp = Blueprint('feed', __name__)


@feed_bp.route('/')
@login_required
def feed():
    category = request.args.get('category', '')
    province = request.args.get('province', '')

    q = Post.query.filter_by(is_removed=False)
    if category:
        q = q.filter_by(category=category)
    if province:
        q = q.filter_by(province=province)

    posts = q.order_by(Post.is_pinned.desc(), Post.created_at.desc()).all()
    return render_template('feed/feed.html', posts=posts,
                           category=category, province=province)


@feed_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        image_name = None
        video_name = None

        if form.image.data:
            f = form.image.data
            ext = f.filename.rsplit('.', 1)[1].lower()
            image_name = f"post_{uuid.uuid4().hex}.{ext}"
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_name))

        if form.video.data:
            f = form.video.data
            ext = f.filename.rsplit('.', 1)[1].lower()
            video_name = f"post_{uuid.uuid4().hex}.{ext}"
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], video_name))

        post = Post(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            province=form.province.data,
            city=form.city.data,
            image_path=image_name,
            video_path=video_name,
            user_id=current_user.id,
        )
        db.session.add(post)
        db.session.commit()
        flash('Post published!', 'success')
        return redirect(url_for('feed.feed'))

    return render_template('feed/create_post.html', form=form)


@feed_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.is_removed and not current_user.is_admin:
        abort(404)

    form = CommentForm()
    if form.validate_on_submit():
        c = Comment(content=form.content.data,
                    post_id=post.id,
                    user_id=current_user.id)
        db.session.add(c)
        db.session.commit()

        if post.user_id != current_user.id:
            db.session.add(Notification(
                user_id=post.user_id,
                title='New comment on your post',
                message=f'{current_user.username} commented on "{post.title or post.content[:40]}"',
                link=url_for('feed.view_post', post_id=post.id),
                type='info'))
            db.session.commit()

        flash('Comment added!', 'success')
        return redirect(url_for('feed.view_post', post_id=post.id))

    return render_template('feed/view_post.html', post=post, form=form)


@feed_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('feed.feed'))


@feed_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    c = Comment.query.get_or_404(comment_id)
    if c.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    post_id = c.post_id
    db.session.delete(c)
    db.session.commit()
    flash('Comment deleted.', 'info')
    return redirect(url_for('feed.view_post', post_id=post_id))
