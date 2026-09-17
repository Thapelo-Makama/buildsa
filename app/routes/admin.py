from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from app.models import (db, User, Post, MaterialPrice, Message,
                        Notification, ActivityLog, Comment)

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.user_dashboard'))
        return f(*a, **kw)
    return wrapper


@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    pending = User.query.filter_by(is_verified=False, is_admin=False).count()
    return render_template('admin/dashboard.html',
        total_users=User.query.count(),
        total_posts=Post.query.filter_by(is_removed=False).count(),
        total_materials=MaterialPrice.query.count(),
        total_messages=Message.query.count(),
        pending_users=pending,
        recent_users=User.query.order_by(User.created_at.desc()).limit(8).all(),
        recent_activities=ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(15).all())


@admin_bp.route('/users')
@login_required
@admin_required
def admin_users():
    pending = User.query.filter_by(is_verified=False, is_admin=False) \
                        .order_by(User.created_at.desc()).all()
    verified = User.query.filter_by(is_verified=True) \
                         .order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', pending=pending, users=verified)


@admin_bp.route('/user/<int:uid>/approve', methods=['POST'])
@login_required
@admin_required
def approve_user(uid):
    u = User.query.get_or_404(uid)
    u.is_verified = True
    u.approved_at = datetime.utcnow()
    db.session.add(Notification(
        user_id=u.id, title='Account approved!',
        message='You can now post, message, and use BuildSA.',
        type='success'))
    db.session.commit()
    flash(f'{u.username} approved.', 'success')
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/user/<int:uid>/reject', methods=['POST'])
@login_required
@admin_required
def reject_user(uid):
    u = User.query.get_or_404(uid)
    if u.is_admin:
        flash('Cannot delete admin.', 'danger')
        return redirect(url_for('admin.admin_users'))
    db.session.delete(u)
    db.session.commit()
    flash('User rejected and removed.', 'success')
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/user/<int:uid>/verify-badge', methods=['POST'])
@login_required
@admin_required
def toggle_verified_badge(uid):
    u = User.query.get_or_404(uid)
    u.is_verified_builder = not u.is_verified_builder
    status = 'granted' if u.is_verified_builder else 'removed'
    flash(f'Verified builder badge {status} for {u.username}.', 'success')
    db.session.commit()
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/user/<int:uid>/ban', methods=['POST'])
@login_required
@admin_required
def ban_user(uid):
    u = User.query.get_or_404(uid)
    if u.is_admin or u.id == current_user.id:
        flash('Cannot ban this user.', 'danger')
        return redirect(url_for('admin.admin_users'))
    u.is_banned = not u.is_banned
    db.session.commit()
    flash(f'{u.username} {"banned" if u.is_banned else "unbanned"}.', 'success')
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/user/<int:uid>/make-admin', methods=['POST'])
@login_required
@admin_required
def make_admin(uid):
    u = User.query.get_or_404(uid)
    u.is_admin = not u.is_admin
    u.is_verified = True
    db.session.commit()
    flash(f'Admin status updated for {u.username}.', 'success')
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/posts')
@login_required
@admin_required
def admin_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/posts.html', posts=posts)


@admin_bp.route('/post/<int:pid>/remove', methods=['POST'])
@login_required
@admin_required
def remove_post(pid):
    p = Post.query.get_or_404(pid)
    p.is_removed = not p.is_removed
    db.session.commit()
    flash('Post visibility updated.', 'success')
    return redirect(url_for('admin.admin_posts'))


@admin_bp.route('/post/<int:pid>/pin', methods=['POST'])
@login_required
@admin_required
def pin_post(pid):
    p = Post.query.get_or_404(pid)
    p.is_pinned = not p.is_pinned
    db.session.commit()
    flash('Pin updated.', 'success')
    return redirect(url_for('admin.admin_posts'))


@admin_bp.route('/post/<int:pid>/delete', methods=['POST'])
@login_required
@admin_required
def delete_post(pid):
    p = Post.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect(url_for('admin.admin_posts'))


@admin_bp.route('/materials')
@login_required
@admin_required
def admin_materials():
    materials = MaterialPrice.query.order_by(MaterialPrice.created_at.desc()).all()
    return render_template('admin/materials.html', materials=materials)


@admin_bp.route('/materials/<int:mid>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_material(mid):
    m = MaterialPrice.query.get_or_404(mid)
    db.session.delete(m)
    db.session.commit()
    flash('Price entry removed.', 'success')
    return redirect(url_for('admin.admin_materials'))


@admin_bp.route('/activity')
@login_required
@admin_required
def admin_activity():
    acts = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(200).all()
    return render_template('admin/activity.html', activities=acts)
