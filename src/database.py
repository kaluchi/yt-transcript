"""Database layer for the YouTube Transcript Bot."""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    create_engine,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from src.models import VideoMetadata, Transcript, VideoSummary, ConversationMessage

logger = logging.getLogger(__name__)
Base = declarative_base()


class VideoMetadataDB(Base):
    """Database model for video metadata."""

    __tablename__ = "video_metadata"

    video_id = Column(String(20), primary_key=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    channel_name = Column(String(200))
    duration = Column(Integer)
    published_at = Column(DateTime)
    view_count = Column(Integer)
    like_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class TranscriptDB(Base):
    """Database model for transcripts."""

    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(20), nullable=False, index=True)
    language = Column(String(10), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_video_language", "video_id", "language"),)


class VideoSummaryDB(Base):
    """Database model for video summaries."""

    __tablename__ = "video_summaries"

    video_id = Column(String(20), primary_key=True)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ConversationMessageDB(Base):
    """Database model for conversation messages."""

    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    video_id = Column(String(20), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_user_video", "user_id", "video_id"),)


class Database:
    """Database operations handler."""

    def __init__(self, database_url: str):
        """Initialize database connection."""
        # Ensure data directory exists for SQLite
        if database_url.startswith("sqlite"):
            db_path = database_url.replace("sqlite:///", "")
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        logger.info("Database initialized")

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def save_video_metadata(self, metadata: VideoMetadata) -> None:
        """Save video metadata to database."""
        with self.get_session() as session:
            db_metadata = VideoMetadataDB(
                video_id=metadata.video_id,
                title=metadata.title,
                description=metadata.description,
                channel_name=metadata.channel_name,
                duration=metadata.duration,
                published_at=metadata.published_at,
                view_count=metadata.view_count,
                like_count=metadata.like_count,
            )
            session.merge(db_metadata)
            session.commit()

    def save_transcript(self, transcript: Transcript) -> None:
        """Save transcript to database."""
        with self.get_session() as session:
            # Check if transcript already exists
            existing = (
                session.query(TranscriptDB)
                .filter_by(video_id=transcript.video_id, language=transcript.language)
                .first()
            )
            if not existing:
                db_transcript = TranscriptDB(
                    video_id=transcript.video_id,
                    language=transcript.language,
                    text=transcript.text,
                )
                session.add(db_transcript)
                session.commit()

    def save_summary(self, summary: VideoSummary) -> None:
        """Save video summary to database."""
        with self.get_session() as session:
            db_summary = VideoSummaryDB(
                video_id=summary.video_id,
                summary=summary.summary,
                created_at=summary.created_at,
            )
            session.merge(db_summary)
            session.commit()

    def save_message(self, message: ConversationMessage) -> None:
        """Save conversation message to database."""
        with self.get_session() as session:
            db_message = ConversationMessageDB(
                user_id=message.user_id,
                video_id=message.video_id,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
            )
            session.add(db_message)
            session.commit()

    def get_video_metadata(self, video_id: str) -> Optional[VideoMetadata]:
        """Get video metadata from database."""
        with self.get_session() as session:
            db_metadata = (
                session.query(VideoMetadataDB).filter_by(video_id=video_id).first()
            )
            if db_metadata:
                return VideoMetadata(
                    video_id=db_metadata.video_id,
                    title=db_metadata.title,
                    description=db_metadata.description,
                    channel_name=db_metadata.channel_name,
                    duration=db_metadata.duration,
                    published_at=db_metadata.published_at,
                    view_count=db_metadata.view_count,
                    like_count=db_metadata.like_count,
                )
            return None

    def get_transcript(self, video_id: str, language: str) -> Optional[Transcript]:
        """Get transcript from database."""
        with self.get_session() as session:
            db_transcript = (
                session.query(TranscriptDB)
                .filter_by(video_id=video_id, language=language)
                .first()
            )
            if db_transcript:
                return Transcript(
                    video_id=db_transcript.video_id,
                    language=db_transcript.language,
                    text=db_transcript.text,
                )
            return None

    def get_summary(self, video_id: str) -> Optional[VideoSummary]:
        """Get video summary from database."""
        with self.get_session() as session:
            db_summary = (
                session.query(VideoSummaryDB).filter_by(video_id=video_id).first()
            )
            if db_summary:
                return VideoSummary(
                    video_id=db_summary.video_id,
                    summary=db_summary.summary,
                    created_at=db_summary.created_at,
                )
            return None

    def get_conversation_history(
        self, user_id: int, video_id: str, limit: int = 50
    ) -> List[ConversationMessage]:
        """Get conversation history for a user and video."""
        with self.get_session() as session:
            messages = (
                session.query(ConversationMessageDB)
                .filter_by(user_id=user_id, video_id=video_id)
                .order_by(ConversationMessageDB.created_at)
                .limit(limit)
                .all()
            )
            return [
                ConversationMessage(
                    user_id=msg.user_id,
                    video_id=msg.video_id,
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at,
                )
                for msg in messages
            ]

    def get_last_video_for_user(self, user_id: int) -> Optional[str]:
        """Get the last video ID discussed by a user."""
        with self.get_session() as session:
            last_message = (
                session.query(ConversationMessageDB)
                .filter_by(user_id=user_id)
                .order_by(ConversationMessageDB.created_at.desc())
                .first()
            )
            return last_message.video_id if last_message else None
