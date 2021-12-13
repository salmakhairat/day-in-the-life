from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user

from .. import bcrypt, mail
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, EmailVerificationForm, UpdateDescriptionForm, UpdateProfilePicForm
from ..models import User
from flask_mail import Message
from ..utils import gen_code
from werkzeug.utils import secure_filename

import io
import base64

def get_b64_img(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image


users = Blueprint("users", __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("posts.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed,
                    confirmed=False, code=gen_code(),
                    profile_pic=None)
        user.save()

        msg = Message(f"Your verification code is {user.code}",
                      sender="dayinthelife.cmsc388jproject@gmail.com",
                      recipients=[user.email])
        mail.send(msg)

        return redirect(url_for("users.verify"))

    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("posts.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
            if not user.confirmed:
                return render_template("verify", title="Verify", form=form)
            login_user(user)
            return redirect(url_for("users.account"))
        else:
            flash("Login failed. Check your username and/or password")
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Login", form=form)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("posts.index"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    username_form = UpdateUsernameForm()
    desc_form = UpdateDescriptionForm()
    picture_form = UpdateProfilePicForm()

    if username_form.validate_on_submit():
        current_user.modify(username=username_form.username.data)
        current_user.save()
        return redirect(url_for("users.account"))

    if desc_form.validate_on_submit():
        current_user.modify(description=desc_form.desc.data)
        current_user.save()
        return redirect(url_for("users.account"))

    if picture_form.validate_on_submit():
        img = picture_form.picture.data
        filename = secure_filename(img.filename)
        content_type = f'images/{filename[-3:]}'

        if current_user.profile_pic.get() is None:
            current_user.profile_pic.put(img.stream, content_type=content_type)
        else:
            current_user.profile_pic.replace(img.stream, content_type=content_type)
        current_user.save()
        return redirect(url_for('users.account'))

    return render_template(
        "account.html",
        title="Account",
        username_form=username_form, desc_form=desc_form, picture_form=picture_form,
        image=get_b64_img(current_user.username)
    )


@users.route("/verify", methods=["GET", "POST"])
def verify():
    verify_form = EmailVerificationForm()
    if verify_form.validate_on_submit():
        user = User.objects(username=verify_form.username.data).first()
        if verify_form.code.data != user.code:
            return redirect(url_for("users.verify"))

        user.modify(confirmed=True)
        user.save()
        return redirect(url_for("users.login"))

    return render_template("verify.html", form=verify_form)