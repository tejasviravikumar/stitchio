from types import SimpleNamespace

import jwt
import pytest

from app.core import security

SECRET = "x" * 40


@pytest.fixture(autouse=True)
def fake_settings(monkeypatch):
    monkeypatch.setattr(security, "get_settings", lambda: SimpleNamespace(supabase_jwt_secret=SECRET, supabase_url=""))


def test_valid_token():
    token = jwt.encode({"sub": "user-1", "aud": "authenticated"}, SECRET, algorithm="HS256")
    assert security.decode_supabase_token(token)["sub"] == "user-1"


def test_wrong_secret_rejected():
    token = jwt.encode({"sub": "u", "aud": "authenticated"}, "y" * 40, algorithm="HS256")
    with pytest.raises(security.AuthError):
        security.decode_supabase_token(token)


def test_wrong_audience_rejected():
    token = jwt.encode({"sub": "u", "aud": "other"}, SECRET, algorithm="HS256")
    with pytest.raises(security.AuthError):
        security.decode_supabase_token(token)


def test_garbage_rejected():
    with pytest.raises(security.AuthError):
        security.decode_supabase_token("not-a-token")
