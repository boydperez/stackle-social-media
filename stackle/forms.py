import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField 
from wtforms.validators import InputRequired, Length, EqualTo, Email, ValidationError, DataRequired
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed, FileRequired

from stackle.models import Account


class SignupForm(FlaskForm):
    """ Generates a signup form. """

    name = StringField("Name", validators=[InputRequired(message="Please enter your name"), \
        Length(min=1, max=100, message="Name should be between 1 to 100 characters")])
    username = StringField("Username", validators=[InputRequired(message="username required"), Length(min=4, max=20,\
        message="username should be between 4 to 20 characters")])
    email = StringField("Email", validators=[InputRequired(message="email no required"), \
        Email(message="Enter valid email")])
    password = PasswordField("Password", validators=[InputRequired(message="Really planning to leave that blank?"), \
        Length(min=4, max=200, message="Password should be minimum 4 characters long")])
    confirm_password = PasswordField("Confirm Password", validators=[EqualTo('password', message="Passwords should match")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        """
        Validate username. 
        """
        user = Account.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError('Username is taken')

        if not re.match('^[a-zA-Z0-9_.-]+$', username.data):
            raise ValidationError('Username can contain alphanumerics and an _ , - and .')

    def validate_email(self, email):
        """
        Validate email. 
        """
        user = Account.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('Email is in use')


class LoginForm(FlaskForm):
    """ Generates a login form. """

    username = StringField("Username", validators=[InputRequired(message="username required"), Length(min=4, max=20,\
        message="username should be between 4 to 20 characters")])
    password = PasswordField("Password", validators=[InputRequired(message="Really planning to leave that blank?")])
    submit = SubmitField("Login")
    

class UpdateForm(FlaskForm):
    """ Generates an update form. """

    name = StringField("Name", validators=[InputRequired(message="Please enter your name"), \
        Length(min=1, max=100, message="Name should be between 1 to 100 characters")])
    username = StringField("Username", validators=[InputRequired(message="username required"), Length(min=4, max=20,\
        message="username should be between 4 to 20 characters")])
    email = StringField("Email", validators=[InputRequired(message="email no required"), \
        Email(message="Enter valid email")])
    
    submit = SubmitField("Update")

    def validate_username(self, username):
        """
        Validate username. 
        """
        user = None
        if username.data != current_user.username:
            user = Account.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is taken')

    def validate_email(self, email):
        """
        Validate email. 
        """
        user = None
        if email.data != current_user.email:
            user = Account.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is in use')



class PostForm(FlaskForm):
    """ Form to upload new posts. """
    post_content = StringField('Title', validators=[DataRequired(), Length(min=1, max=250, message="max characters allowed: 250")])
    # TODO: Add FileField
    image_file = FileField('image', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Post')