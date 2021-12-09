import pytest

from types import SimpleNamespace
import random
import string

from flask_app.forms import SearchForm, MovieReviewForm
from flask_app.models import User, Review
from tests.conftest import AuthActions


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200

    search = SimpleNamespace(search_query="guardians", submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data=form.data, follow_redirects=True)

    assert b"Guardians of the Galaxy" in response.data


@pytest.mark.parametrize(
    ("query", "message"), 
    (["", b"This field is required."], ["a", b"Too many results"], 
    ["sdfas", b"Movie not found"], ["a" * 102, b"Field must be between 1 and 100 characters long."])
)
def test_search_input_validation(client, query, message):
    resp = client.get("/")
    assert resp.status_code == 200

    search = SimpleNamespace(search_query=query, submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data=form.data, follow_redirects=True)

    assert message in response.data


def test_movie_review(client, auth):
    guardians_id = "tt2015381"
    url = f"/movies/{guardians_id}"
    resp = client.get(url)

    assert resp.status_code == 200

    auth.register()
    auth.login()

    comment = ''.join(random.choice(string.ascii_lowercase) for i in range(20))

    review = SimpleNamespace(text=comment, submit="Enter Comment")
    form = MovieReviewForm(formdata=None, obj=review)
    response = client.post(url, data=form.data, follow_redirects=True)

    assert bytes(comment, 'UTF-8') in response.data
    assert Review.objects(imdb_id=guardians_id).first()
    


@pytest.mark.parametrize(
    ("movie_id", "message"), 
    (["", 404], ["a123", 302], ["aaaa1234567", 302], ["aaaaaaaaa", 302])
)
def test_movie_review_redirects(client, movie_id, message):
    url = f"/movies/{movie_id}"
    resp = client.get(url)
    
    assert resp.status_code == message
    resp = client.get(url, follow_redirects=True)

    if message == 404:
        assert b"404" in resp.data
    elif message == 302:
        assert b"Incorrect IMDb ID." in resp.data


@pytest.mark.parametrize(
    ("comment", "message"), 
    (["", b"This field is required"], 
    ["aaa", b"Field must be between 5 and 500 characters long."],
    ['a' * 501, b"Field must be between 5 and 500 characters long."])
)
def test_movie_review_input_validation(client, auth, comment, message):
    guardians_id = "tt2015381"
    url = f"/movies/{guardians_id}"

    auth.register()
    auth.login()

    review = SimpleNamespace(text=comment, submit="Enter Comment")
    form = MovieReviewForm(formdata=None, obj=review)
    response = client.post(url, data=form.data, follow_redirects=False)

    assert message in response.data