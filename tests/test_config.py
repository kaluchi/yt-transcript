"""Tests for configuration module."""

import os
import pytest
from src.config import Config


def test_config_from_env(monkeypatch):
    """Test configuration loading from environment."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.setenv("YOUTUBE_API_KEY", "test_youtube_key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")

    config = Config.from_env()

    assert config.telegram_bot_token == "test_token"
    assert config.youtube_api_key == "test_youtube_key"
    assert config.anthropic_api_key == "test_anthropic_key"
    assert config.database_url == "sqlite:///test.db"


def test_config_defaults(monkeypatch):
    """Test default configuration values."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.setenv("YOUTUBE_API_KEY", "test_youtube_key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")

    config = Config.from_env()

    assert config.log_level == "INFO"
    assert config.max_summary_words == 500


def test_config_validation_missing_telegram_token():
    """Test validation fails when Telegram token is missing."""
    config = Config(
        telegram_bot_token="",
        youtube_api_key="key",
        anthropic_api_key="key",
        database_url="sqlite:///test.db",
    )

    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is required"):
        config.validate()


def test_config_validation_missing_youtube_key():
    """Test validation fails when YouTube API key is missing."""
    config = Config(
        telegram_bot_token="token",
        youtube_api_key="",
        anthropic_api_key="key",
        database_url="sqlite:///test.db",
    )

    with pytest.raises(ValueError, match="YOUTUBE_API_KEY is required"):
        config.validate()


def test_config_validation_success():
    """Test validation passes with all required fields."""
    config = Config(
        telegram_bot_token="token",
        youtube_api_key="youtube_key",
        anthropic_api_key="anthropic_key",
        database_url="sqlite:///test.db",
    )

    # Should not raise
    config.validate()
