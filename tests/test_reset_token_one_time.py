from datetime import datetime
from types import SimpleNamespace

import pytest

from mongo_auth.authenticate import Authenticate
from mongo_auth.exceptions import ResetError
import mongo_auth.authenticate as auth_module


class FakeUsersCollection:
    def __init__(self, state):
        self._state = state

    def find_one(self, query):
        user = self._state.get(query["email"])
        return dict(user) if user else None

    def update_one(self, query, update):
        email = query["email"]
        user = self._state.setdefault(email, {"email": email, "created": datetime.utcnow()})

        for key, value in update.get("$set", {}).items():
            user[key] = value

        for key in update.get("$unset", {}).keys():
            user.pop(key, None)

        return SimpleNamespace(modified_count=1)


class FakeDatabase:
    def __init__(self, state):
        self._users = FakeUsersCollection(state)

    def __getitem__(self, name):
        if name != "users":
            raise KeyError(name)
        return self._users


class FakeMongoClient:
    state = {}

    def __init__(self, _uri):
        pass

    def __getitem__(self, _db_name):
        return FakeDatabase(self.state)

    def close(self):
        return None


def test_reset_token_can_only_be_used_once(monkeypatch):
    FakeMongoClient.state = {"user@example.com": {"email": "user@example.com", "verified": True}}
    monkeypatch.setattr(auth_module, "MongoClient", FakeMongoClient)

    auth = Authenticate.__new__(Authenticate)
    auth.mongo_uri = "mongodb://fake"
    auth.db_name = "smartbids"

    token, _ = auth._create_password_reset_token("user@example.com")

    first_use = auth.reset_password_with_token("user@example.com", token, "NewPass123", "NewPass123")
    assert first_use is True

    with pytest.raises(ResetError, match="invalid|already used"):
        auth.reset_password_with_token("user@example.com", token, "AnotherPass123", "AnotherPass123")
