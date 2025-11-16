"""Tests for Telegram bot."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.bot import YouTubeTranscriptBot
from src.config import Config
from src.models import VideoMetadata, Transcript, VideoSummary


@pytest.fixture
def config():
    """Create test configuration."""
    return Config(
        telegram_bot_token="test_token",
        youtube_api_key="test_youtube_key",
        anthropic_api_key="test_anthropic_key",
        database_url="sqlite:///:memory:",
    )


@pytest.fixture
def bot(config):
    """Create bot instance for testing."""
    return YouTubeTranscriptBot(config)


@pytest.fixture
def mock_update():
    """Create mock Telegram update."""
    update = Mock()
    update.effective_user.id = 12345
    update.effective_user.language_code = "en"
    update.message.text = "test message"
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Create mock context."""
    return Mock()


class TestStartCommand:
    """Tests for /start command."""

    @pytest.mark.asyncio
    async def test_start_command(self, bot, mock_update, mock_context):
        """Test /start command sends welcome message."""
        await bot.start(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Welcome" in call_args
        assert "/start" in call_args
        assert "/help" in call_args


class TestHelpCommand:
    """Tests for /help command."""

    @pytest.mark.asyncio
    async def test_help_command(self, bot, mock_update, mock_context):
        """Test /help command sends help message."""
        await bot.help_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "How to use" in call_args


class TestHandleMessage:
    """Tests for message handling."""

    @pytest.mark.asyncio
    async def test_youtube_url_triggers_processing(
        self, bot, mock_update, mock_context
    ):
        """Test that YouTube URL triggers video processing."""
        mock_update.message.text = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        with patch.object(bot, "process_video", new_callable=AsyncMock) as mock_process:
            await bot.handle_message(mock_update, mock_context)
            mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_non_url_triggers_conversation(self, bot, mock_update, mock_context):
        """Test that non-URL message triggers conversation."""
        mock_update.message.text = "What is this video about?"

        with patch.object(
            bot, "handle_conversation", new_callable=AsyncMock
        ) as mock_conv:
            await bot.handle_message(mock_update, mock_context)
            mock_conv.assert_called_once()


class TestProcessVideo:
    """Tests for video processing."""

    @pytest.mark.asyncio
    async def test_process_existing_video(self, bot, mock_update, mock_context):
        """Test processing already-cached video."""
        # Save a summary to database
        summary = VideoSummary(
            video_id="test123",
            summary="Existing summary",
            created_at=datetime.utcnow(),
        )
        bot.db.save_summary(summary)

        mock_update.message.reply_text = AsyncMock()

        await bot.process_video(mock_update, "test123", "en")

        # Should reply with existing summary
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "already have" in call_args
        assert "Existing summary" in call_args

    @pytest.mark.asyncio
    async def test_process_new_video_success(self, bot, mock_update, mock_context):
        """Test processing new video successfully."""
        mock_status_msg = Mock()
        mock_status_msg.edit_text = AsyncMock()
        mock_update.message.reply_text = AsyncMock(return_value=mock_status_msg)

        # Mock YouTube service
        mock_metadata = VideoMetadata(
            video_id="test123",
            title="Test Video",
            description="Description",
            channel_name="Channel",
            duration=600,
            published_at=datetime.utcnow(),
            view_count=1000,
            like_count=100,
        )

        mock_transcript = Transcript(
            video_id="test123", language="en", text="Test transcript"
        )

        with patch.object(
            bot.youtube, "get_video_metadata", return_value=mock_metadata
        ):
            with patch.object(
                bot.youtube, "get_transcript", return_value=mock_transcript
            ):
                with patch.object(
                    bot.ai, "generate_summary", return_value="Generated summary"
                ):
                    await bot.process_video(mock_update, "test123", "en")

        # Should update status multiple times
        assert mock_status_msg.edit_text.call_count >= 3

    @pytest.mark.asyncio
    async def test_process_video_error(self, bot, mock_update, mock_context):
        """Test error handling during video processing."""
        mock_status_msg = Mock()
        mock_status_msg.edit_text = AsyncMock()
        mock_update.message.reply_text = AsyncMock(return_value=mock_status_msg)

        # Mock YouTube service to raise error
        with patch.object(
            bot.youtube, "get_video_metadata", side_effect=Exception("API Error")
        ):
            await bot.process_video(mock_update, "test123", "en")

        # Should show error message
        error_call = mock_status_msg.edit_text.call_args_list[-1][0][0]
        assert "Error" in error_call


class TestHandleConversation:
    """Tests for conversation handling."""

    @pytest.mark.asyncio
    async def test_conversation_no_previous_video(
        self, bot, mock_update, mock_context
    ):
        """Test conversation when user has no previous video."""
        await bot.handle_conversation(
            mock_update, 12345, "What is this about?", "en"
        )

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "send me a YouTube link" in call_args

    @pytest.mark.asyncio
    async def test_conversation_with_video(self, bot, mock_update, mock_context):
        """Test conversation about a video."""
        # Setup video data
        metadata = VideoMetadata(
            video_id="test123",
            title="Test Video",
            description="Description",
            channel_name="Channel",
            duration=600,
            published_at=datetime.utcnow(),
            view_count=1000,
            like_count=100,
        )
        bot.db.save_video_metadata(metadata)

        transcript = Transcript(
            video_id="test123", language="en", text="Test transcript"
        )
        bot.db.save_transcript(transcript)

        # Save a message to establish video context
        from src.models import ConversationMessage

        msg = ConversationMessage(
            user_id=12345,
            video_id="test123",
            role="user",
            content="Previous message",
            created_at=datetime.utcnow(),
        )
        bot.db.save_message(msg)

        mock_typing_msg = Mock()
        mock_typing_msg.edit_text = AsyncMock()
        mock_update.message.reply_text = AsyncMock(return_value=mock_typing_msg)

        with patch.object(bot.ai, "chat_about_video", return_value="AI response"):
            await bot.handle_conversation(
                mock_update, 12345, "What is this about?", "en"
            )

        # Should show typing indicator and then response
        assert mock_update.message.reply_text.call_count == 1
        mock_typing_msg.edit_text.assert_called_once_with("AI response")
