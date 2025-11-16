"""Telegram bot for YouTube transcript processing."""

import logging
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

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

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        welcome_message = """👋 Welcome to YouTube Transcript Bot!

I can help you:
• Get summaries of YouTube videos
• Discuss video content with you

📌 How to use:
1. Send me a YouTube link
2. I'll fetch the video, transcript, and create a summary
3. You can then ask me questions about the video

Commands:
/start - Show this message
/help - Show help information"""

        await update.message.reply_text(welcome_message)

    async def help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /help command."""
        help_text = """🔍 How to use this bot:

1️⃣ Send a YouTube URL:
   - I'll download the video metadata and transcript
   - Generate a summary (max 500 words)
   - Save everything for later discussion

2️⃣ Ask questions:
   - After sending a video, just type your question
   - I'll answer based on the video content
   - I remember our conversation context

💡 Tips:
   - If video was already processed, I'll show the saved summary
   - I prefer transcripts in your language, fallback to English
   - You can discuss any previously sent video

Examples:
   "What is the main idea?"
   "Can you explain the part about X?"
   "What did they say about Y?"
"""
        await update.message.reply_text(help_text)

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
        # Check if we already have this video
        existing_summary = self.db.get_summary(video_id)

        if existing_summary:
            await update.message.reply_text(
                f"✅ I already have this video!\n\n{existing_summary.summary}"
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
            summary_text = self.ai.generate_summary(metadata, transcript)

            # Save summary
            summary = VideoSummary(
                video_id=video_id, summary=summary_text, created_at=datetime.utcnow()
            )
            self.db.save_summary(summary)

            # Send summary
            await status_msg.edit_text(
                f"✅ Video processed successfully!\n\n"
                f"📺 **{metadata.title}**\n"
                f"👤 {metadata.channel_name}\n\n"
                f"📄 Summary:\n{summary_text}\n\n"
                f"💬 Ask me anything about this video!"
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
        transcript = self.db.get_transcript(last_video_id, user_language)

        if not transcript:
            # Try English
            transcript = self.db.get_transcript(last_video_id, "en")

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
            created_at=datetime.utcnow(),
        )
        self.db.save_message(user_msg)

        # Generate response
        try:
            typing_msg = await update.message.reply_text("💭 Thinking...")
            response = self.ai.chat_about_video(
                message_text, metadata, transcript, history
            )

            # Save assistant response
            assistant_msg = ConversationMessage(
                user_id=user_id,
                video_id=last_video_id,
                role="assistant",
                content=response,
                created_at=datetime.utcnow(),
            )
            self.db.save_message(assistant_msg)

            # Send response
            await typing_msg.edit_text(response)

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
    # Setup logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    # Load configuration
    config = Config.from_env()
    config.validate()

    # Create and run bot
    bot = YouTubeTranscriptBot(config)
    bot.run()


if __name__ == "__main__":
    main()
