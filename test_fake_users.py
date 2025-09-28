import pytest

fake_users = [
    {"name": "User 1", "id": "user1", "city": "San Francisco", "state": "CA"},
]

def test_fake_users_structure():
    assert len(fake_users) == 1
    user = fake_users[0]
    assert "name" in user
    assert "id" in user
    assert "city" in user
    assert "state" in user

def test_fake_users_data():
    user = fake_users[0]
    assert user["name"] == "User 1"
    assert user["id"] == "user1"
    assert user["city"] == "San Francisco"
    assert user["state"] == "CA"

def test_fake_users_types():
    user = fake_users[0]
    assert isinstance(user["name"], str)
    assert isinstance(user["id"], str)
    assert isinstance(user["city"], str)
    assert isinstance(user["state"], str)