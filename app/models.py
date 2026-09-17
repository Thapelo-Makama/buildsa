from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    city = db.Column(db.String(80))
    province = db.Column(db.String(50))
    profession = db.Column(db.String(80))     # e.g. Builder, Electrician, Plumber
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(200))

    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)   # admin approved
    is_verified_builder = db.Column(db.Boolean, default=False)  # premium badge
    is_banned = db.Column(db.Boolean, default=False)

    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    materials = db.relationship('MaterialPrice', backref='submitter', lazy=True, cascade='all, delete-orphan')

    def set_password(self, p):
        self.password_hash = generate_password_hash(p)

    def check_password(self, p):
        return check_password_hash(self.password_hash, p)

    def unread_count(self):
        return Message.query.filter_by(recipient_id=self.id, is_read=False).count()

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(30), default='general')
    # general, question, project, ad, material

    image_path = db.Column(db.String(200))
    video_path = db.Column(db.String(200))

    province = db.Column(db.String(50))
    city = db.Column(db.String(80))

    is_pinned = db.Column(db.Boolean, default=False)
    is_removed = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    author = db.relationship('User', foreign_keys=[user_id], backref='comments')


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')


class MaterialPrice(db.Model):
    __tablename__ = 'material_prices'

    id = db.Column(db.Integer, primary_key=True)
    material_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))            # per brick, per bag, per m2
    supplier = db.Column(db.String(100))
    city = db.Column(db.String(80))
    province = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))


class Follow(db.Model):
    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    following_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    message = db.Column(db.Text)
    link = db.Column(db.String(200))
    type = db.Column(db.String(20), default='info')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(80), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    user = db.relationship('User', backref='activities')
