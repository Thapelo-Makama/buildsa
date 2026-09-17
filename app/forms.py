from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, BooleanField, SubmitField,
                     TextAreaField, SelectField, FloatField)
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import User

PROVINCES = [
    ('', 'Select province'),
    ('Gauteng', 'Gauteng'),
    ('Western Cape', 'Western Cape'),
    ('KwaZulu-Natal', 'KwaZulu-Natal'),
    ('Eastern Cape', 'Eastern Cape'),
    ('Free State', 'Free State'),
    ('Limpopo', 'Limpopo'),
    ('Mpumalanga', 'Mpumalanga'),
    ('North West', 'North West'),
    ('Northern Cape', 'Northern Cape'),
]

CATEGORIES = [
    ('general', 'General Chat'),
    ('question', 'Question'),
    ('project', 'Project Showcase'),
    ('ad', 'Advertise My Services'),
    ('material', 'Material Discussion'),
]


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3, 64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    city = StringField('City / Town')
    province = SelectField('Province', choices=PROVINCES, validators=[Optional()])
    profession = StringField('Profession (e.g. Builder, Electrician)')
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, f):
        if User.query.filter_by(username=f.data).first():
            raise ValidationError('Username already taken.')

    def validate_email(self, f):
        if User.query.filter_by(email=f.data).first():
            raise ValidationError('Email already registered.')


class PostForm(FlaskForm):
    title = StringField('Title (optional)')
    content = TextAreaField('What do you want to share?', validators=[DataRequired()])
    category = SelectField('Category', choices=CATEGORIES, validators=[DataRequired()])
    province = SelectField('Province', choices=PROVINCES, validators=[Optional()])
    city = StringField('City / Town')
    image = FileField('Photo (optional)', validators=[FileAllowed(['png','jpg','jpeg','gif'], 'Images only')])
    video = FileField('Video (optional)', validators=[FileAllowed(['mp4','mov'], 'Videos only')])
    submit = SubmitField('Post')


class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Reply')


class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired()])
    recipient_id = SelectField('To', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Send')


class MaterialForm(FlaskForm):
    material_name = StringField('Material name', validators=[DataRequired()])
    price = FloatField('Price (R)', validators=[DataRequired()])
    unit = SelectField('Unit', choices=[
        ('per brick', 'per brick'),
        ('per bag', 'per bag'),
        ('per m2', 'per m²'),
        ('per m3', 'per m³'),
        ('per sheet', 'per sheet'),
        ('per item', 'per item'),
    ])
    supplier = StringField('Supplier / Store')
    province = SelectField('Province', choices=PROVINCES, validators=[Optional()])
    city = StringField('City / Town')
    notes = TextAreaField('Notes (optional)')
    submit = SubmitField('Submit Price')


class ProfileForm(FlaskForm):
    full_name = StringField('Full Name')
    phone_number = StringField('Phone Number')
    city = StringField('City')
    province = SelectField('Province', choices=PROVINCES, validators=[Optional()])
    profession = StringField('Profession')
    bio = TextAreaField('Bio')
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['png','jpg','jpeg'], 'Images only')])
    submit = SubmitField('Save Profile')
