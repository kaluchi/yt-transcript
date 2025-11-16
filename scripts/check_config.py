#!/usr/bin/env python3
"""Script to check configuration before running the bot."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config


def main():
    """Check configuration and display status."""
    print("=" * 50)
    print("YouTube Transcript Bot - Configuration Check")
    print("=" * 50)
    print()

    try:
        config = Config.from_env()

        # Check Telegram token
        print("Telegram Bot Token:", end=" ")
        if config.telegram_bot_token and len(config.telegram_bot_token) > 10:
            print("✓ Set")
        else:
            print("✗ Not set")

        # Check YouTube API key
        print("YouTube API Key:", end=" ")
        if config.youtube_api_key and len(config.youtube_api_key) > 10:
            print("✓ Set")
        else:
            print("✗ Not set")

        # Check OpenAI API key
        print("OpenAI API Key:", end=" ")
        if config.openai_api_key and len(config.openai_api_key) > 10:
            print("✓ Set")
        else:
            print("✗ Not set")

        # Database URL
        print(f"Database URL: {config.database_url}")
        print(f"Log Level: {config.log_level}")
        print(f"Max Summary Words: {config.max_summary_words}")

        print()
        # Validate
        config.validate()
        print("✓ Configuration is valid!")
        print()
        print("You can start the bot with: python -m src.bot")
        return 0

    except ValueError as e:
        print()
        print(f"✗ Configuration error: {e}")
        print()
        print("Please check your .env file and ensure all required")
        print("environment variables are set.")
        return 1
    except Exception as e:
        print()
        print(f"✗ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
