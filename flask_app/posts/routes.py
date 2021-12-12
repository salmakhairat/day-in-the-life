from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from .. import tenor_client
from ..forms import CommentForm, SearchForm, PostForm
from ..models import User, Comment, Post
from ..utils import current_time

posts = Blueprint("posts", __name__)

@posts.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for("posts.query_results", query=form.search_query.data))

    return render_template("index.html", form=form)


@posts.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    # I have no idea if this code works but it's worth a shot
    all_users = User.objects()
    results = [user for user in all_users if user.username.startswith(query)]

    return render_template("query.html", results=results)


@posts.route("/posts/<post_id>", methods=["GET", "POST"])
def post_detail(post_id):
    try:
        result = Post.objects(post_id=post_id)
    except ValueError as e:
        return redirect(url_for("users.login"))

    form = CommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:

        # Tenor query
        url = None
        if form.gifQuery.data:
            url = tenor_client.get_url(tenor_client.search(form.gifQuery.data))

        comment = Comment(
            commenter=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            post_id=post_id,
            gif_url = url
        )
        comment.save()

        return redirect(request.path)

    comments = Comment.objects(post_id=post_id)

    return render_template("post_detail.html", form=form, post=result, comments=comments)


@posts.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    isUser = (user == current_user)

    form = PostForm()
    if form.validate_on_submit() and current_user.is_authenticated:

        url = None
        if form.gifQuery.data:
            url = tenor_client.get_url(tenor_client.search(form.gifQuery.data))

        post = Post(
            poster=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            post_id= 0, #TODO here's the problem we need some global counter to keep track of # of posts so each post gets a unique id
            title=form.title.data,
            gif_url = url
        )
        post.save()

        return redirect(request.path)

    posts = Post.objects(poster=user)

    return render_template("user_detail.html", username=username, posts=posts, isUser=isUser)
