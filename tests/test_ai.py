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

    @patch("src.ai.OpenAI")
    def test_generate_summary_success(
        self, mock_openai, ai_service, sample_metadata, sample_transcript
    ):
        """Test successful summary generation."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "This is a generated summary."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        ai_service.client = mock_client

        summary = ai_service.generate_summary(sample_metadata, sample_transcript)

        assert summary == "This is a generated summary."
        mock_client.chat.completions.create.assert_called_once()

    @patch("src.ai.OpenAI")
    def test_generate_summary_includes_metadata(
        self, mock_openai, ai_service, sample_metadata, sample_transcript
    ):
        """Test that summary generation includes metadata in prompt."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Summary"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        ai_service.client = mock_client

        ai_service.generate_summary(sample_metadata, sample_transcript)

        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        prompt = messages[0]["content"]

        assert "Test Video" in prompt
        assert "Test Channel" in prompt
        assert "10 minutes" in prompt


class TestChatAboutVideo:
    """Tests for chat functionality."""

    @patch("src.ai.OpenAI")
    def test_chat_about_video_success(
        self, mock_openai, ai_service, sample_metadata, sample_transcript
    ):
        """Test successful chat response."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Here's my answer about the video."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        ai_service.client = mock_client

        response = ai_service.chat_about_video(
            "What is this video about?", sample_metadata, sample_transcript, []
        )

        assert response == "Here's my answer about the video."

    @patch("src.ai.OpenAI")
    def test_chat_includes_conversation_history(
        self, mock_openai, ai_service, sample_metadata, sample_transcript
    ):
        """Test that chat includes conversation history."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

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

        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]

        # Should have system message + history + new message
        assert len(messages) >= 4  # system + 2 history + 1 new
        assert messages[1]["content"] == "Previous question"
        assert messages[2]["content"] == "Previous answer"

    @patch("src.ai.OpenAI")
    def test_chat_limits_history(
        self, mock_openai, ai_service, sample_metadata, sample_transcript
    ):
        """Test that chat limits conversation history."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

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

        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]

        # Should have system + last 10 from history + 1 new message
        assert len(messages) <= 12

    @patch("src.ai.OpenAI")
    def test_generate_summary_russian_language(
        self, mock_openai, ai_service, sample_metadata, sample_transcript
    ):
        """Test summary generation in Russian language."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Русское резюме видео."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        ai_service.client = mock_client

        summary = ai_service.generate_summary(sample_metadata, sample_transcript, language="ru")

        assert summary == "Русское резюме видео."
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        prompt = messages[0]["content"]

        # Check that Russian instructions are in the prompt
        assert "Пожалуйста, предоставьте подробное резюме на русском языке" in prompt
        assert "Основная тема и цель видео" in prompt

    @patch("src.ai.OpenAI")
    def test_chat_about_video_russian_language(
        self, mock_openai, ai_service, sample_metadata, sample_transcript
    ):
        """Test chat in Russian language."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Вот мой ответ о видео."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        ai_service.client = mock_client

        response = ai_service.chat_about_video(
            "О чём это видео?", sample_metadata, sample_transcript, [], language="ru"
        )

        assert response == "Вот мой ответ о видео."
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        system_message = messages[0]["content"]

        # Check that Russian system message is used
        assert "Вы полезный помощник, обсуждающий видео YouTube с пользователем" in system_message
        assert "Отвечайте на русском языке" in system_message

    @patch("src.ai.OpenAI")
    def test_generate_summary_api_error(
        self, mock_openai, ai_service, sample_metadata, sample_transcript
    ):
        """Test error handling when OpenAI API fails."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Simulate API error
        mock_client.chat.completions.create.side_effect = Exception("API rate limit exceeded")
        ai_service.client = mock_client

        with pytest.raises(Exception, match="API rate limit exceeded"):
            ai_service.generate_summary(sample_metadata, sample_transcript)

    @patch("src.ai.OpenAI")
    def test_chat_about_video_api_error(
        self, mock_openai, ai_service, sample_metadata, sample_transcript
    ):
        """Test error handling when OpenAI API fails during chat."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Simulate API error
        mock_client.chat.completions.create.side_effect = Exception("API connection error")
        ai_service.client = mock_client

        with pytest.raises(Exception, match="API connection error"):
            ai_service.chat_about_video(
                "What is this about?", sample_metadata, sample_transcript, []
            )
