from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app.models import db, User, ActivityLog, Notification
from app.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.user_dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))
        if user.is_banned:
            flash('Your account has been banned.', 'danger')
            return redirect(url_for('auth.login'))
        if not user.is_verified:
            flash('Your account is awaiting admin approval.', 'warning')
            return redirect(url_for('auth.login'))

        user.last_login = datetime.utcnow()
        db.session.add(ActivityLog(
            user_id=user.id, action='login',
            ip_address=request.remote_addr))
        db.session.commit()

        login_user(user, remember=form.remember_me.data)
        flash(f'Welcome back, {user.username}!', 'success')

        if user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('dashboard.user_dashboard'))

    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.user_dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            phone_number=form.phone_number.data,
            city=form.city.data,
            province=form.province.data,
            profession=form.profession.data,
            is_verified=False,
            is_active=True,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Notify all admins
        for adm in User.query.filter_by(is_admin=True).all():
            db.session.add(Notification(
                user_id=adm.id,
                title='New builder awaiting approval',
                message=f'{user.full_name or user.username} registered.',
                link=url_for('admin.admin_users'),
                type='info'))
        db.session.commit()

        flash('Registration successful! Please wait for admin approval.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    db.session.add(ActivityLog(
        user_id=current_user.id, action='logout',
        ip_address=request.remote_addr))
    db.session.commit()
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('index'))
