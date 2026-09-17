from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, Message, User
from app.forms import MessageForm

messages_bp = Blueprint('messages', __name__)


@messages_bp.route('/')
@login_required
def inbox():
    # Conversations: unique users the current user has messaged with
    sent = db.session.query(Message.recipient_id).filter_by(sender_id=current_user.id)
    received = db.session.query(Message.sender_id).filter_by(recipient_id=current_user.id)
    partner_ids = {r[0] for r in sent.union(received).all()}

    partners = User.query.filter(User.id.in_(partner_ids)).all() if partner_ids else []

    # Mark everything as read
    Message.query.filter_by(recipient_id=current_user.id, is_read=False) \
                 .update({'is_read': True})
    db.session.commit()

    return render_template('feed/inbox.html', partners=partners)


@messages_bp.route('/chat/<username>', methods=['GET', 'POST'])
@login_required
def chat(username):
    partner = User.query.filter_by(username=username).first_or_404()
    if partner.id == current_user.id:
        flash('You cannot message yourself.', 'warning')
        return redirect(url_for('messages.inbox'))

    form = MessageForm()
    form.recipient_id.choices = [(partner.id, partner.username)]

    if form.validate_on_submit():
        msg = Message(
            content=form.content.data,
            sender_id=current_user.id,
            recipient_id=partner.id,
        )
        db.session.add(msg)
        db.session.commit()
        return redirect(url_for('messages.chat', username=partner.username))

    # Load thread
    thread = Message.query.filter(
        db.or_(
            db.and_(Message.sender_id == current_user.id, Message.recipient_id == partner.id),
            db.and_(Message.sender_id == partner.id, Message.recipient_id == current_user.id),
        )
    ).order_by(Message.timestamp.asc()).all()

    # Mark received as read
    Message.query.filter_by(sender_id=partner.id, recipient_id=current_user.id, is_read=False) \
                 .update({'is_read': True})
    db.session.commit()

    return render_template('feed/chat.html',
                           partner=partner, thread=thread, form=form)


@messages_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_message():
    form = MessageForm()
    users = User.query.filter(User.id != current_user.id,
                              User.is_verified == True,
                              User.is_banned == False).all()
    form.recipient_id.choices = [(u.id, f'{u.username} ({u.profession or "Member"})') for u in users]

    if form.validate_on_submit():
        target = User.query.get(form.recipient_id.data)
        if not target:
            flash('User not found.', 'danger')
            return redirect(url_for('messages.new_message'))
        return redirect(url_for('messages.chat', username=target.username))

    return render_template('feed/new_message.html', form=form)
