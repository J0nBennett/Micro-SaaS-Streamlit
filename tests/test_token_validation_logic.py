from types import SimpleNamespace

from mongo_auth.authenticate import Authenticate
import mongo_auth.authenticate as auth_module


class FakeCookieManager:
    def get(self, _name):
        return "cookie-token"


def _build_auth():
    auth = Authenticate.__new__(Authenticate)
    auth.cookie_name = "test-cookie"
    auth.cookie_manager = FakeCookieManager()
    return auth


def test_check_cookie_requires_name_and_email(monkeypatch):
    fake_st = SimpleNamespace(
        session_state={
            "logout": False,
            "name": None,
            "email": None,
            "authentication_status": None,
        }
    )
    monkeypatch.setattr(auth_module, "st", fake_st)

    auth = _build_auth()
    auth._token_decode = lambda: {"name": "User", "exp_date": 99999999999}
    auth._check_cookie()

    assert fake_st.session_state["authentication_status"] is None
    assert fake_st.session_state["email"] is None

    auth._token_decode = lambda: {"name": "User", "email": "user@example.com", "exp_date": 99999999999}
    auth._check_cookie()

    assert fake_st.session_state["authentication_status"] is True
    assert fake_st.session_state["email"] == "user@example.com"
