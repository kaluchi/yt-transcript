"""Telegram bot for YouTube transcript processing."""

import logging
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import telegramify_markdown

from src.config import Config
from src.database import Database
from src.youtube import YouTubeService
from src.ai import AIService
from src.models import VideoSummary, ConversationMessage

logger = logging.getLogger(__name__)


class YouTubeTranscriptBot:
    """Main bot class handling all interactions."""

    def __init__(self, config: Config):
        """Initialize the bot with configuration."""
        self.config = config
        self.db = Database(config.database_url)
        self.youtube = YouTubeService(config.youtube_api_key)
        self.ai = AIService(config.openai_api_key, config.max_summary_words)

    @staticmethod
    def _format_markdown(text: str) -> str:
        """Convert standard Markdown to Telegram MarkdownV2."""
        return telegramify_markdown.markdownify(text)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        welcome_message = """Welcome to YouTube Transcript Bot!

Send me a YouTube link and I'll:
- Create a summary
- Answer questions about the video

/help - Show help"""

        await update.message.reply_text(
            self._format_markdown(welcome_message), parse_mode='MarkdownV2'
        )

    async def help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /help command."""
        help_text = """🔍 How to use:

Send a YouTube URL:
- I'll fetch metadata and transcript
- Generate a summary (max 500 words)
- Save for later discussion

Ask questions:
- I'll answer based on video content
- Conversation context is remembered

Tips:
- Already processed videos load instantly
- Transcripts use your language or English

Examples:
"What is the main idea?"
"Can you explain the part about X?"
"""
        await update.message.reply_text(
            self._format_markdown(help_text), parse_mode='MarkdownV2'
        )

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle incoming text messages."""
        user_id = update.effective_user.id
        message_text = update.message.text
        user_language = update.effective_user.language_code or "en"

        # Check if message contains a YouTube URL
        video_id = self.youtube.extract_video_id(message_text)

        if video_id:
            await self.process_video(update, video_id, user_language)
        else:
            await self.handle_conversation(update, user_id, message_text, user_language)

    async def process_video(
        self, update: Update, video_id: str, user_language: str
    ) -> None:
        """Process a YouTube video URL."""
        user_id = update.effective_user.id

        # Check if we already have this video
        existing_summary = self.db.get_summary(video_id)

        if existing_summary:
            # Save context - user is now interacting with this video
            metadata = self.db.get_video_metadata(video_id)
            context_msg = ConversationMessage(
                user_id=user_id,
                video_id=video_id,
                role="user",
                content=f"[Viewing video: {metadata.title if metadata else video_id}]",
                created_at=datetime.now(timezone.utc),
            )
            self.db.save_message(context_msg)

            message_text = (
                f"✅ I already have this video!\n\n{existing_summary.summary}\n\n"
                f"💬 Ask me anything about this video!"
            )
            await update.message.reply_text(
                self._format_markdown(message_text), parse_mode='MarkdownV2'
            )
            return

        # Send initial status message
        status_msg = await update.message.reply_text("⏳ Processing video...")

        try:
            # Step 1: Fetch metadata
            await status_msg.edit_text("📥 Fetching video metadata...")
            metadata = self.youtube.get_video_metadata(video_id)
            self.db.save_video_metadata(metadata)

            # Step 2: Fetch transcript
            await status_msg.edit_text("📝 Fetching video transcript...")
            preferred_languages = [user_language, "en"]
            transcript = self.youtube.get_transcript(video_id, preferred_languages)
            self.db.save_transcript(transcript)

            # Step 3: Generate summary
            await status_msg.edit_text("🤖 Generating summary with AI...")
            summary_text = self.ai.generate_summary(metadata, transcript, user_language)

            # Save summary
            summary = VideoSummary(
                video_id=video_id, summary=summary_text, created_at=datetime.now(timezone.utc)
            )
            self.db.save_summary(summary)

            # Save context - user is now interacting with this video
            context_msg = ConversationMessage(
                user_id=user_id,
                video_id=video_id,
                role="user",
                content=f"[Processed new video: {metadata.title}]",
                created_at=datetime.now(timezone.utc),
            )
            self.db.save_message(context_msg)

            # Send summary
            message_text = (
                f"✅ Video processed successfully!\n\n"
                f"📺 **{metadata.title}**\n"
                f"👤 {metadata.channel_name}\n\n"
                f"📄 Summary:\n{summary_text}\n\n"
                f"💬 Ask me anything about this video!"
            )
            await status_msg.edit_text(
                self._format_markdown(message_text), parse_mode='MarkdownV2'
            )

        except Exception as e:
            logger.error(f"Error processing video {video_id}: {e}")
            await status_msg.edit_text(
                f"❌ Error processing video: {str(e)}\n\n"
                "Please check the URL and try again."
            )

    async def handle_conversation(
        self, update: Update, user_id: int, message_text: str, user_language: str
    ) -> None:
        """Handle conversation about a video."""
        # Get last video for this user
        last_video_id = self.db.get_last_video_for_user(user_id)

        if not last_video_id:
            # No previous video, show welcome message
            await update.message.reply_text(
                "👋 Please send me a YouTube link first, "
                "then we can discuss the video!\n\n"
                "Use /help for more information."
            )
            return

        # Get video data
        metadata = self.db.get_video_metadata(last_video_id)
        transcript = self.db.get_transcript(last_video_id, user_language) or \
                     self.db.get_transcript(last_video_id, "en")

        if not metadata or not transcript:
            await update.message.reply_text(
                "❌ Sorry, I couldn't find the video data. "
                "Please send the video link again."
            )
            return

        # Get conversation history
        history = self.db.get_conversation_history(user_id, last_video_id)

        # Save user message
        user_msg = ConversationMessage(
            user_id=user_id,
            video_id=last_video_id,
            role="user",
            content=message_text,
            created_at=datetime.now(timezone.utc),
        )
        self.db.save_message(user_msg)

        # Generate response
        try:
            typing_msg = await update.message.reply_text("💭 Thinking...")
            response = self.ai.chat_about_video(
                message_text, metadata, transcript, history, user_language
            )

            # Save assistant response
            assistant_msg = ConversationMessage(
                user_id=user_id,
                video_id=last_video_id,
                role="assistant",
                content=response,
                created_at=datetime.now(timezone.utc),
            )
            self.db.save_message(assistant_msg)

            # Send response
            await typing_msg.edit_text(
                self._format_markdown(response), parse_mode='MarkdownV2'
            )

        except Exception as e:
            logger.error(f"Error in conversation: {e}")
            await update.message.reply_text(
                f"❌ Sorry, I encountered an error: {str(e)}"
            )

    def run(self) -> None:
        """Run the bot."""
        # Build application
        app = Application.builder().token(self.config.telegram_bot_token).build()

        # Add handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        logger.info("Bot started")
        # Run the bot
        app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point."""
    config = Config.from_env()
    config.validate()

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, config.log_level.upper()),
    )

    bot = YouTubeTranscriptBot(config)
    bot.run()


if __name__ == "__main__":
    main()
