"""Tests for AI service."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.ai import AIService
from src.models import VideoMetadata, Transcript, ConversationMessage


@pytest.fixture
def ai_service():
    """Create an AI service instance for testing."""
    return AIService(api_key="test_api_key", max_summary_words=500)


@pytest.fixture
def sample_metadata():
    """Create sample video metadata."""
    return VideoMetadata(
        video_id="test123",
        title="Test Video",
        description="Test description",
        channel_name="Test Channel",
        duration=600,
        published_at=datetime(2024, 1, 1),
        view_count=1000,
        like_count=100,
    )


@pytest.fixture
def sample_transcript():
    """Create sample transcript."""
    return Transcript(
        video_id="test123",
        language="en",
        text="This is a test transcript about artificial intelligence and machine learning.",
    )


class TestGenerateSummary:
    """Tests for summary generation."""

    @patch("src.ai.Anthropic")
    def test_generate_summary_success(
        self, mock_anthropic, ai_service, sample_metadata, sample_transcript
    ):
        """Test successful summary generation."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="This is a generated summary.")]
        mock_client.messages.create.return_value = mock_response

        ai_service.client = mock_client

        summary = ai_service.generate_summary(sample_metadata, sample_transcript)

        assert summary == "This is a generated summary."
        mock_client.messages.create.assert_called_once()

    @patch("src.ai.Anthropic")
    def test_generate_summary_includes_metadata(
        self, mock_anthropic, ai_service, sample_metadata, sample_transcript
    ):
        """Test that summary generation includes metadata in prompt."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Summary")]
        mock_client.messages.create.return_value = mock_response

        ai_service.client = mock_client

        ai_service.generate_summary(sample_metadata, sample_transcript)

        call_args = mock_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]

        assert "Test Video" in prompt
        assert "Test Channel" in prompt
        assert "10 minutes" in prompt


class TestChatAboutVideo:
    """Tests for chat functionality."""

    @patch("src.ai.Anthropic")
    def test_chat_about_video_success(
        self, mock_anthropic, ai_service, sample_metadata, sample_transcript
    ):
        """Test successful chat response."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Here's my answer about the video.")]
        mock_client.messages.create.return_value = mock_response

        ai_service.client = mock_client

        response = ai_service.chat_about_video(
            "What is this video about?", sample_metadata, sample_transcript, []
        )

        assert response == "Here's my answer about the video."

    @patch("src.ai.Anthropic")
    def test_chat_includes_conversation_history(
        self, mock_anthropic, ai_service, sample_metadata, sample_transcript
    ):
        """Test that chat includes conversation history."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_client.messages.create.return_value = mock_response

        ai_service.client = mock_client

        history = [
            ConversationMessage(
                user_id=123,
                video_id="test123",
                role="user",
                content="Previous question",
                created_at=datetime.utcnow(),
            ),
            ConversationMessage(
                user_id=123,
                video_id="test123",
                role="assistant",
                content="Previous answer",
                created_at=datetime.utcnow(),
            ),
        ]

        ai_service.chat_about_video(
            "Follow-up question", sample_metadata, sample_transcript, history
        )

        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs["messages"]

        assert len(messages) >= 3  # History + new message
        assert messages[0]["content"] == "Previous question"
        assert messages[1]["content"] == "Previous answer"

    @patch("src.ai.Anthropic")
    def test_chat_limits_history(
        self, mock_anthropic, ai_service, sample_metadata, sample_transcript
    ):
        """Test that chat limits conversation history."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_client.messages.create.return_value = mock_response

        ai_service.client = mock_client

        # Create 20 messages in history
        history = [
            ConversationMessage(
                user_id=123,
                video_id="test123",
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                created_at=datetime.utcnow(),
            )
            for i in range(20)
        ]

        ai_service.chat_about_video(
            "New question", sample_metadata, sample_transcript, history
        )

        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs["messages"]

        # Should have last 10 from history + 1 new message
        assert len(messages) <= 11
