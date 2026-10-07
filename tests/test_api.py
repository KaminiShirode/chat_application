import pytest

from app import create_app, db
from app.models import User, Message
from unittest.mock import patch
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError

@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def create_test_users(client):
    response1 = client.post(
        "/users",
        json={
            "name": "Kamini",
            "email": "kamini@test.com"
        }
    )

    response2 = client.post(
        "/users",
        json={
            "name": "Anjali",
            "email": "anjali@test.com"
        }
    )

    return response1, response2


def test_create_user(client):
    response = client.post(
        "/users",
        json={
            "name": "Kamini",
            "email": "kamini@test.com"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["user"]["name"] == "Kamini"
    assert data["user"]["email"] == "kamini@test.com"


def test_get_users(client):
    create_test_users(client)

    response = client.get("/users")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2
    assert data[0]["name"] == "Kamini"
    assert data[1]["name"] == "Anjali"


def test_send_message(client):
    create_test_users(client)

    response = client.post(
        "/messages",
        json={
            "sender_id": 1,
            "receiver_id": 2,
            "message": "Hello Anjali!"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["data"]["sender_id"] == 1
    assert data["data"]["receiver_id"] == 2
    assert data["data"]["message"] == "Hello Anjali!"


def test_get_messages(client):
    create_test_users(client)

    client.post(
        "/messages",
        json={
            "sender_id": 1,
            "receiver_id": 2,
            "message": "Hello Anjali!"
        }
    )

    client.post(
        "/messages",
        json={
            "sender_id": 2,
            "receiver_id": 1,
            "message": "Hello Kamini!"
        }
    )

    response = client.get(
        "/messages?user1_id=1&user2_id=2"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2
    assert data[0]["message"] == "Hello Anjali!"
    assert data[1]["message"] == "Hello Kamini!"


def test_create_user_validation(client):
    response = client.post(
        "/users",
        json={
            "name": "Kamini"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Name and email are required"

from unittest.mock import patch


def test_get_users_with_mock(client, app):
    mock_users = [
        User(id=1, name="Kamini", email="kamini@test.com", created_at=datetime.now(timezone.utc)),
        User(id=2, name="Anjali", email="anjali@test.com", created_at=datetime.now(timezone.utc))
    ]

    with app.app_context():
        with patch("app.routes.User.query") as mock_query:
            mock_query.order_by.return_value.all.return_value = mock_users

            response = client.get("/users")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2
    assert data[0]["name"] == "Kamini"
    assert data[1]["name"] == "Anjali"

def test_create_user_database_error(client):
    with patch("app.routes.db.session.commit") as mock_commit:
        mock_commit.side_effect = SQLAlchemyError("Database error")

        response = client.post(
            "/users",
            json={
                "name": "Test User",
                "email": "test@example.com"
            }
        )

    assert response.status_code == 500

    data = response.get_json()

    assert data["error"] == "Database error"