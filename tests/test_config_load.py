import pytest

import utils


class FakeStreamlit:
    def __init__(self, secrets):
        self.secrets = secrets


def test_config_prefers_env_over_secrets(monkeypatch):
    monkeypatch.setenv("AUTH_COOKIE_NAME", "from-env")
    monkeypatch.setattr(utils, "st", FakeStreamlit({"AUTH_COOKIE_NAME": "from-secrets"}))

    assert utils.get_config_value("AUTH_COOKIE_NAME") == "from-env"


def test_config_falls_back_to_secrets(monkeypatch):
    monkeypatch.delenv("AUTH_COOKIE_NAME", raising=False)
    monkeypatch.setattr(utils, "st", FakeStreamlit({"AUTH_COOKIE_NAME": "from-secrets"}))

    assert utils.get_config_value("AUTH_COOKIE_NAME") == "from-secrets"


def test_required_config_missing_raises_controlled_error(monkeypatch):
    monkeypatch.delenv("AUTH_COOKIE_KEY", raising=False)
    monkeypatch.setattr(utils, "st", FakeStreamlit({}))

    with pytest.raises(RuntimeError, match="Missing required config: AUTH_COOKIE_KEY"):
        utils.get_config_value("AUTH_COOKIE_KEY", required=True)
