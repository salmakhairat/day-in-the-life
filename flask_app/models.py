from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager
from . import config
from .utils import current_time
import base64


@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()


class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    confirmed = db.BooleanField(required=True)
    code = db.StringField(required=True)
    description = db.StringField(required=False, min_length=5, max_length=500)

    # Returns unique string identifying our object
    def get_id(self):
        return self.username

class Comment(db.Document):
    commenter = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    gif_url = db.StringField(required=False)
    # Each post must have a unique post-id of length 9
    # All comments under the same post should have the same post_id
    post_id = db.StringField(required=True)

class Post(db.Document):
    poster = db.ReferenceField(User, required=True)
    title = db.StringField(required=True, min_length=5, max_length=50)
    content = db.StringField(required=True, min_length=5, max_length=500)
    gif_url = db.StringField(required=False)
    date = db.StringField(required=True)
    post_id = db.StringField(required=False)

class Counter(db.Document):
    number = db.StringField(requried=True)