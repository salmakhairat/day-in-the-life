from flask import session, request
import pytest

from types import SimpleNamespace

from flask_app.forms import RegistrationForm, UpdateUsernameForm
from flask_app.models import User


def test_register(client, auth):
    """ Test that registration page opens up """
    resp = client.get("/register")
    assert resp.status_code == 200

    response = auth.register()

    assert response.status_code == 200
    user = User.objects(username="test").first()

    assert user is not None


@pytest.mark.parametrize(
    ("username", "email", "password", "confirm", "message"),
    (
        ("test", "test@email.com", "test", "test", b"Username is taken"),
        ("p" * 41, "test@email.com", "test", "test", b"Field must be between 1 and 40"),
        ("username", "test", "test", "test", b"Invalid email address."),
        ("username", "test@email.com", "test", "test2", b"Field must be equal to"),
    ),
)
def test_register_validate_input(auth, username, email, password, confirm, message):
    if message == b"Username is taken":
        auth.register()

    response = auth.register(username, email, password, confirm)

    assert message in response.data


def test_login(client, auth):
    """ Test that login page opens up """
    resp = client.get("/login")
    assert resp.status_code == 200

    auth.register()
    response = auth.login()

    with client:
        client.get("/")
        assert session["_user_id"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"), 
    (
    ["", "123", b"This field is required"], ["aaron", "", b"This field is required"],
    ["asdf", "test", b"Login failed. Check your username and/or password"],
    ["test", "asdf", b"Login failed. Check your username and/or password"]
    )
)
def test_login_input_validation(auth, username, password, message):
    auth.register()
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.register()
    resp = auth.login()
    assert resp.status_code == 200
    auth.logout()
    assert resp.status_code == 200


def test_change_username(client, auth):
    auth.register()
    auth.login()
    resp = client.get("/account")
    assert resp.status_code == 200
    new_name = "aaronshav"

    update = SimpleNamespace(username=new_name, submit="Update Username")
    form = UpdateUsernameForm(formdata=None, obj=update)
    client.post("/account", data=form.data, follow_redirects=True)
    response = auth.login(new_name, "test")
    assert bytes(new_name, 'UTF-8') in response.data

    user = User.objects(username=new_name).first()
    assert user is not None


def test_change_username_taken(client, auth):
    auth.register("aaron", "aaron@gmail.com", "1234", "1234")
    auth.register("aaron2", "aaron2@gmail.com", "1234", "1234")

    auth.login("aaron", "1234")

    update = SimpleNamespace(username="aaron2", submit="Update Username")
    form = UpdateUsernameForm(formdata=None, obj=update)
    response = client.post("/account", data=form.data, follow_redirects=True)

    assert b"That username is already taken" in response.data



@pytest.mark.parametrize(
    ("new_username", "message"), 
    (['', b"This field is required."], ['a' * 41, b"Field must be between 1 and 40 characters long."])
)
def test_change_username_input_validation(client, auth, new_username, message):
    auth.register()
    auth.login()

    update = SimpleNamespace(username=new_username, submit="Update Username")
    form = UpdateUsernameForm(formdata=None, obj=update)
    response = client.post("/account", data=form.data, follow_redirects=True)

    assert message in response.data