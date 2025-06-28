"""Pydantic models for PyTubeSearch."""

from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field


class SearchOptions(BaseModel):
    """Search options for filtering YouTube content."""

    type: str = Field(
        ..., description="Type of content to search for (video, channel, playlist, movie)"
    )


class SearchItem(BaseModel):
    """Individual search result item."""

    id: str = Field(..., description="Unique identifier for the item")
    type: str = Field(..., description="Type of the item (video, channel, playlist)")
    thumbnail: Optional[Any] = Field(None, description="Thumbnail data")
    title: str = Field(..., description="Title of the item")
    channel_title: Optional[str] = Field(None, description="Channel title", alias="channelTitle")
    short_byline_text: Optional[str] = Field(
        None, description="Short byline text", alias="shortBylineText"
    )
    length: Optional[Union[str, Any]] = Field(None, description="Length of the video")
    is_live: Optional[bool] = Field(
        False, description="Whether the content is live", alias="isLive"
    )
    videos: Optional[List[Any]] = Field(None, description="Videos in playlist")
    video_count: Optional[str] = Field(
        None, description="Number of videos in playlist", alias="videoCount"
    )

    class Config:
        populate_by_name = True


class NextPageData(BaseModel):
    """Next page pagination data."""

    next_page_token: Optional[str] = Field(
        None, description="Token for next page", alias="nextPageToken"
    )
    next_page_context: Optional[Any] = Field(
        None, description="Context for next page", alias="nextPageContext"
    )

    class Config:
        populate_by_name = True


class SearchResult(BaseModel):
    """Search results container."""

    items: List[SearchItem] = Field(..., description="List of search result items")
    next_page: NextPageData = Field(..., description="Next page data", alias="nextPage")

    class Config:
        populate_by_name = True


class PlaylistResult(BaseModel):
    """Playlist result container."""

    items: List[SearchItem] = Field(..., description="List of playlist items")
    metadata: Optional[Any] = Field(None, description="Playlist metadata")


class ChannelResult(BaseModel):
    """Channel result container."""

    title: str = Field(..., description="Channel title")
    content: Optional[Any] = Field(None, description="Channel content")


class VideoDetails(BaseModel):
    """Detailed video information."""

    id: str = Field(..., description="Video ID")
    title: str = Field(..., description="Video title")
    thumbnail: Optional[Any] = Field(None, description="Video thumbnail")
    is_live: bool = Field(False, description="Whether the video is live", alias="isLive")
    channel: str = Field(..., description="Channel name")
    channel_id: str = Field(..., description="Channel ID", alias="channelId")
    description: str = Field(..., description="Video description")
    keywords: List[str] = Field(default_factory=list, description="Video keywords")
    suggestion: List[SearchItem] = Field(default_factory=list, description="Suggested videos")

    class Config:
        populate_by_name = True


class ShortVideo(BaseModel):
    """YouTube Shorts video."""

    id: str = Field(..., description="Short video ID")
    type: str = Field(..., description="Type of content (reel)")
    thumbnail: Optional[Any] = Field(None, description="Short video thumbnail")
    title: str = Field(..., description="Short video title")
    inline_playback_endpoint: Optional[Any] = Field(
        None, description="Inline playback data", alias="inlinePlaybackEndpoint"
    )

    class Config:
        populate_by_name = True


class YoutubeInitData(BaseModel):
    """Internal YouTube initialization data."""

    initdata: Any = Field(..., description="YouTube page initialization data")
    api_token: Optional[str] = Field(None, description="YouTube API token", alias="apiToken")
    context: Optional[Any] = Field(None, description="YouTube request context")

    class Config:
        populate_by_name = True


class YoutubePlayerDetail(BaseModel):
    """YouTube player details."""

    video_id: str = Field(..., description="Video ID", alias="videoId")
    thumbnail: Optional[Any] = Field(None, description="Video thumbnail")
    author: Optional[str] = Field(None, description="Video author")
    channel_id: str = Field(..., description="Channel ID", alias="channelId")
    short_description: str = Field(..., description="Short description", alias="shortDescription")
    keywords: List[str] = Field(default_factory=list, description="Video keywords")

    class Config:
        populate_by_name = True
