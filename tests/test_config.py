from configparser import ConfigParser

import pytest

from fetchrewards_takehome.utils import read_config


@pytest.fixture
def config() -> ConfigParser:
    """Get configuration parser object for testing"""
    return read_config()


def test_has_expected_config(config):
    assert config.has_option("DEV", "postgres_database")
    assert config.has_option("DEV", "postgres_host")
    assert config.has_option("DEV", "postgres_user")
    assert config.has_option("DEV", "postgres_password")
    assert config.has_option("DEV", "postgres_port")
    assert config.has_option("DEV", "table_name")
    assert config.has_option("DEV", "queue_url")
    assert config.has_option("DEV", "fernet_key")
