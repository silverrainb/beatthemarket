from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from wtforms_components import EmailField, Email, Unique
from lib.util_wtforms import ModelForm
from beatthemarket.blueprints.user.models import User, db
from beatthemarket.blueprints.user.validations import ensure_identity_exists, \
    ensure_existing_password_matches


class LoginForm(FlaskForm):
    next = HiddenField()
    identity = StringField('Username or email',
                           [DataRequired(), Length(3, 254)])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])
    remember = BooleanField('Remember Me')


class BeginPasswordResetForm(FlaskForm):
    identity = StringField('Username or email',
                           [DataRequired(),
                            Length(3, 254),
                            ensure_identity_exists])


class PasswordResetForm(FlaskForm):
    reset_token = HiddenField()
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])


class RegisterForm(ModelForm):
    email = EmailField(validators=[
        DataRequired(),
        Email(),
        Unique(
            User.email,
            get_session=lambda: db.session
        )
    ])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])


class WelcomeForm(ModelForm):
    username_message = 'Letters, numbers and underscores only please.'

    username = StringField(validators=[
        Unique(
            User.username,
            get_session=lambda: db.session
        ),
        DataRequired(),
        Length(1, 16),
        # Part of the Python 3.7.x update included updating flake8 which means
        # we need to explicitly define our regex pattern with r'xxx'.
        Regexp(r'^\w+$', message=username_message)
    ])


class UpdateCredentials(ModelForm):
    current_password = PasswordField('Current password',
                                     [DataRequired(),
                                      Length(8, 128),
                                      ensure_existing_password_matches])

    email = EmailField(validators=[
        # Email(),
        Unique(
            User.email,
            get_session=lambda: db.session
        )
    ])
    password = PasswordField('Password', [Optional(), Length(8, 128)])
