"""Data models for the YouTube Transcript Bot."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class VideoMetadata:
    """YouTube video metadata."""

    video_id: str
    title: str
    description: str
    channel_name: str
    duration: int
    published_at: datetime
    view_count: int
    like_count: int


@dataclass
class Transcript:
    """Video transcript data."""

    video_id: str
    language: str
    text: str


@dataclass
class VideoSummary:
    """Generated summary of a video."""

    video_id: str
    summary: str
    created_at: datetime


@dataclass
class ConversationMessage:
    """A message in a conversation about a video."""

    user_id: int
    video_id: str
    role: str  # 'user' or 'assistant'
    content: str
    created_at: datetime
