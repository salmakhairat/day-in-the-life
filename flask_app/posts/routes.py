from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from .. import tenor_client
from ..forms import CommentForm, SearchForm, PostForm
from ..models import User, Comment, Post, Counter
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
        post = Post.objects(post_id=post_id).first()
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

    return render_template("post_detail.html", form=form, post=post, comments=comments, title=post.title)


@posts.route("/user/<username>",  methods=['GET', 'POST'])
def user_detail(username):
    user = User.objects(username=username).first()
    isUser = (user == current_user)

    form = PostForm()
    if form.validate_on_submit() and current_user.is_authenticated:

        url = None
        if form.gifQuery.data:
            url = tenor_client.get_url(tenor_client.search(form.gifQuery.data))

        counter = Counter.objects().first()

        if counter is None:
            counter = Counter (
                number= str(0)
            )
            counter.save()

        new_number = str(int(counter.number) + 1)
        post = Post(
            poster=current_user._get_current_object(),
            content=form.content.data,
            date=current_time(),
            post_id= new_number,
            title=form.title.data,
            gif_url = url
        )
        post.save()

        counter.modify(number=new_number)
        counter.save()

        return redirect(request.path)

    posts = Post.objects(poster=user)

    return render_template("user_detail.html", username=username, posts=posts, isUser=isUser, form=form, title=username)

@posts.route("/about")
def about():
    return render_template("about.html", title="about")
