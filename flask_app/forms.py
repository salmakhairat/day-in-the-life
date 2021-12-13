from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import (
    InputRequired,
    DataRequired,
    NumberRange,
    Length,
    Email,
    EqualTo,
    ValidationError,
)


from .models import User


class SearchForm(FlaskForm):
    search_query = StringField(
        "Query", validators=[InputRequired(), Length(min=1, max=100)]
    )
    submit = SubmitField("Search")


class CommentForm(FlaskForm):
    text = TextAreaField(
        "Comment", validators=[InputRequired(), Length(min=5, max=500)]
    )
    gifQuery = StringField("Gif")
    submit = SubmitField("Enter Comment")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is taken")

    def validate_password(self, password):
        if len(password.data) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        if len(password.data) > 32:
            raise ValidationError("Password must be at most 32 characters long")
        if not any(c.isupper() for c in password.data):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in password.data):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not any(c.isnumeric() for c in password.data):
            raise ValidationError("Password must contain at least one number.")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class UpdateUsernameForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    submit = SubmitField("Update Username")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.objects(username=username.data).first()
            if user is not None:
                raise ValidationError("That username is already taken")

class UpdateDescriptionForm(FlaskForm):
    desc = TextAreaField("Description", validators=[InputRequired(), Length(min=5, max=500)])
    desc_submit = SubmitField("Update Description")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), Length(min=5, max=50)])
    content = TextAreaField(
        "Content", validators=[InputRequired(), Length(min=5, max=500)]
    )
    gifQuery = StringField("Gif")
    submit = SubmitField("Enter Post")

class EmailVerificationForm(FlaskForm):
    code = StringField("Code", validators=[InputRequired(), Length(min=6, max=6)])
    username = StringField("Username", validators=[InputRequired(), Length(min=1, max=40)])
    submit = SubmitField("Enter")

    #def validate_code(self, code):
    #    user = User.objects(username=username.data).first()
    #    if code.data != user.code:
    #        raise ValidationError("Code does not match sent code")

class UpdateProfilePicForm(FlaskForm):
    picture = FileField('New Profile Picture', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images Only!')])
    picture_submit = SubmitField("Update Picture")