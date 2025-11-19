"""AI service for generating summaries and handling conversations."""

import logging
from typing import List

from openai import OpenAI

from src.models import VideoMetadata, Transcript, ConversationMessage

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered operations using OpenAI."""

    def __init__(self, api_key: str, max_summary_words: int = 500):
        """Initialize AI service."""
        self.client = OpenAI(api_key=api_key)
        self.max_summary_words = max_summary_words
        self.model = "gpt-4o-mini"  # Fast and cost-effective

    def generate_summary(
        self, metadata: VideoMetadata, transcript: Transcript, language: str = "en"
    ) -> str:
        """
        Generate a summary of the video based on metadata and transcript.

        Args:
            metadata: Video metadata
            transcript: Video transcript
            language: Target language for summary (ISO 639-1 code like 'en', 'ru', etc.)

        Returns:
            Summary text (max 500 words)
        """
        # Language-specific instructions (ru/en only)
        if language == "ru":
            instruction = f"Пожалуйста, предоставьте подробное резюме на русском языке (не более {self.max_summary_words} слов), которое включает:"
            points = """1. Основная тема и цель видео
2. Ключевые моменты и важная обсуждаемая информация
3. Основные выводы или главные идеи

Пишите в ясном, информативном стиле."""
        else:
            instruction = f"Please provide a comprehensive summary in English (no more than {self.max_summary_words} words) that covers:"
            points = """1. The main topic and purpose of the video
2. Key points and important information discussed
3. Main conclusions or takeaways

Write in a clear, informative style."""

        # Construct YouTube URL
        video_url = f"https://www.youtube.com/watch?v={metadata.video_id}"

        prompt = f"""Analyze this YouTube video and create a concise summary.

Video Details:
- URL: {video_url}
- Title: {metadata.title}
- Channel: {metadata.channel_name}
- Duration: {metadata.duration // 60} minutes {metadata.duration % 60} seconds
- Views: {metadata.view_count:,}
- Likes: {metadata.like_count:,}

Transcript:
{transcript.text[:15000]}  # Limit transcript to avoid token limits

{instruction}
{points}

IMPORTANT: At the very beginning of your response, include the video link in this exact format:
🎬 {video_url}

Then provide the summary."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                temperature=0.7,
            )

            summary = response.choices[0].message.content
            logger.info(f"Generated summary for video {metadata.video_id}")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise

    def chat_about_video(
        self,
        user_message: str,
        metadata: VideoMetadata,
        transcript: Transcript,
        conversation_history: List[ConversationMessage],
        language: str = "en",
    ) -> str:
        """
        Handle a conversation about a video.

        Args:
            user_message: User's message
            metadata: Video metadata
            transcript: Video transcript
            conversation_history: Previous conversation messages
            language: User's language for responses

        Returns:
            AI response
        """
        # Language-specific system instructions (ru/en only)
        if language == "ru":
            lang_instruction = "Вы полезный помощник, обсуждающий видео YouTube с пользователем. Отвечайте на русском языке."
        else:
            lang_instruction = "You are a helpful assistant discussing a YouTube video with a user. Respond in English."

        # Build system message
        system_message = f"""{lang_instruction}

Video Information:
- Title: {metadata.title}
- Channel: {metadata.channel_name}
- Description: {metadata.description[:500]}

Full Transcript:
{transcript.text[:20000]}  # Limit to avoid token limits

Use the transcript to answer questions accurately. Be conversational and helpful.
Refer to specific parts of the video when relevant."""

        # Build conversation messages
        messages = [{"role": "system", "content": system_message}]

        # Add conversation history
        for msg in conversation_history[-10:]:  # Keep last 10 messages
            messages.append({"role": msg.role, "content": msg.content})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2048,
                temperature=0.7,
            )

            reply = response.choices[0].message.content
            logger.info(f"Generated chat response for video {metadata.video_id}")
            return reply

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise
