from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
import os, uuid
from werkzeug.utils import secure_filename
from app.models import (db, Post, MaterialPrice, Message,
                        Notification, Follow, ActivityLog, User)
from app.forms import ProfileForm, PostForm
from flask import current_app

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/user')
@login_required
def user_dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))

    posts = Post.query.filter_by(user_id=current_user.id) \
                      .order_by(Post.created_at.desc()).limit(5).all()
    my_materials = MaterialPrice.query.filter_by(user_id=current_user.id) \
                                     .order_by(MaterialPrice.created_at.desc()).limit(5).all()
    notifications = Notification.query.filter_by(
        user_id=current_user.id, is_read=False).all()
    unread_msgs = Message.query.filter_by(
        recipient_id=current_user.id, is_read=False).count()

    # Recent posts from following
    following_ids = [f.following_id for f in Follow.query.filter_by(follower_id=current_user.id).all()]
    follow_feed = []
    if following_ids:
        follow_feed = Post.query.filter(Post.user_id.in_(following_ids)) \
                                .order_by(Post.created_at.desc()).limit(5).all()

    return render_template('dashboard/user_dashboard.html',
                           posts=posts,
                           my_materials=my_materials,
                           notifications=notifications,
                           unread_msgs=unread_msgs,
                           follow_feed=follow_feed)


@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.phone_number = form.phone_number.data
        current_user.city = form.city.data
        current_user.province = form.province.data
        current_user.profession = form.profession.data
        current_user.bio = form.bio.data

        if form.profile_picture.data:
            f = form.profile_picture.data
            ext = f.filename.rsplit('.', 1)[1].lower()
            fname = f"avatar_{uuid.uuid4().hex}.{ext}"
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], fname)
            f.save(path)
            current_user.profile_picture = fname

        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('dashboard.user_dashboard'))

    return render_template('dashboard/edit_profile.html', form=form)


@dashboard_bp.route('/u/<username>')
@login_required
def view_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id, is_removed=False) \
                      .order_by(Post.created_at.desc()).all()
    following = Follow.query.filter_by(follower_id=current_user.id,
                                       following_id=user.id).first() is not None
    followers_count = Follow.query.filter_by(following_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()

    return render_template('dashboard/view_profile.html',
                           user=user, posts=posts,
                           is_following=following,
                           followers_count=followers_count,
                           following_count=following_count)


@dashboard_bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user.id == current_user.id:
        flash('You cannot follow yourself.', 'warning')
        return redirect(url_for('dashboard.view_profile', username=username))

    existing = Follow.query.filter_by(follower_id=current_user.id,
                                      following_id=user.id).first()
    if existing:
        db.session.delete(existing)
        flash(f'Unfollowed {user.username}.', 'info')
    else:
        db.session.add(Follow(follower_id=current_user.id, following_id=user.id))
        db.session.add(Notification(
            user_id=user.id,
            title='New follower',
            message=f'{current_user.username} started following you.',
            type='info'))
        flash(f'Now following {user.username}.', 'success')

    db.session.commit()
    return redirect(url_for('dashboard.view_profile', username=username))


@dashboard_bp.route('/notifications/read', methods=['POST'])
@login_required
def mark_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False) \
                      .update({'is_read': True})
    db.session.commit()
    return redirect(url_for('dashboard.user_dashboard'))
