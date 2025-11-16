"""Configuration management for the YouTube Transcript Bot."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Application configuration."""

    telegram_bot_token: str
    youtube_api_key: str
    anthropic_api_key: str
    database_url: str
    log_level: str = "INFO"
    max_summary_words: int = 500

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            youtube_api_key=os.getenv("YOUTUBE_API_KEY", ""),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            database_url=os.getenv("DATABASE_URL", "sqlite:///./data/bot.db"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def validate(self) -> None:
        """Validate that required configuration is present."""
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not self.youtube_api_key:
            raise ValueError("YOUTUBE_API_KEY is required")
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
