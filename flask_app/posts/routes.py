from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from .. import movie_client
from ..forms import CommentForm, SearchForm
from ..models import User, Comment, Post
from ..utils import current_time

posts = Blueprint("posts", __name__)

@posts.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    # TODO

    if form.validate_on_submit():
        return redirect(url_for("movies.query_results", query=form.search_query.data))

    return render_template("index.html", form=form)


@posts.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        results = movie_client.search(query)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("movies.index"))

    return render_template("query.html", results=results)


@posts.route("/posts/<post_id>", methods=["GET", "POST"])
def post_detail(post_id):
    try:
        result = Post.objects(post_id=post_id)
    except ValueError as e:
        return redirect(url_for("users.login"))

    form = CommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(
            commenter=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            post_id=post_id,
        )
        comment.save()

        return redirect(request.path)

    comments = Comment.objects(imdb_id=movie_id)

    return render_template(
        "post_detail.html", form=form, movie=result, comments=comments
    )


@posts.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    isUser = (user == current_user)

    form = PostForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        post = Post(
            poster=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            post_id= 0, #TODO
            title=form.title.data
        )
        post.save()

        return redirect(request.path)

    posts = Post.objects(poster=user)

    return render_template("user_detail.html", username=username, posts=posts, isUser=isUser)
