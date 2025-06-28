"""Test Pydantic models."""

import pytest
from pydantic import ValidationError

from pytubesearch.models import (
    ChannelResult,
    NextPageData,
    PlaylistResult,
    SearchItem,
    SearchOptions,
    SearchResult,
    ShortVideo,
    VideoDetails,
    YoutubeInitData,
    YoutubePlayerDetail,
)


class TestSearchOptions:
    """Test SearchOptions model."""

    def test_valid_search_options(self):
        """Test creating valid search options."""
        options = SearchOptions(type="video")
        assert options.type == "video"

    def test_search_options_types(self):
        """Test different search option types."""
        valid_types = ["video", "channel", "playlist", "movie"]

        for option_type in valid_types:
            options = SearchOptions(type=option_type)
            assert options.type == option_type

    def test_empty_type_works(self):
        """Test that empty type is allowed."""
        # Empty string is technically valid, just check it works
        options = SearchOptions(type="")
        assert options.type == ""


class TestSearchItem:
    """Test SearchItem model."""

    def test_minimal_search_item(self):
        """Test creating minimal search item."""
        item = SearchItem(id="test_id", type="video", title="Test Title")
        assert item.id == "test_id"
        assert item.type == "video"
        assert item.title == "Test Title"
        assert item.is_live is False

    def test_full_search_item(self):
        """Test creating full search item."""
        item = SearchItem(
            id="test_id",
            type="video",
            title="Test Title",
            channel_title="Test Channel",
            short_byline_text="Test byline",
            length="10:30",
            is_live=True,
            video_count="5",
        )
        assert item.channel_title == "Test Channel"
        assert item.is_live is True
        assert item.video_count == "5"

    def test_alias_support(self):
        """Test that field aliases work correctly."""
        data = {
            "id": "test_id",
            "type": "video",
            "title": "Test Title",
            "channelTitle": "Test Channel",
            "shortBylineText": "Test byline",
            "isLive": True,
            "videoCount": "10",
        }
        item = SearchItem(**data)
        assert item.channel_title == "Test Channel"
        assert item.short_byline_text == "Test byline"
        assert item.is_live is True
        assert item.video_count == "10"


class TestNextPageData:
    """Test NextPageData model."""

    def test_next_page_data(self):
        """Test creating next page data."""
        next_page = NextPageData(
            next_page_token="test_token", next_page_context={"continuation": "test_continuation"}
        )
        assert next_page.next_page_token == "test_token"
        assert next_page.next_page_context["continuation"] == "test_continuation"

    def test_next_page_alias(self):
        """Test next page data with aliases."""
        data = {
            "nextPageToken": "test_token",
            "nextPageContext": {"continuation": "test_continuation"},
        }
        next_page = NextPageData(**data)
        assert next_page.next_page_token == "test_token"
        assert next_page.next_page_context["continuation"] == "test_continuation"


class TestSearchResult:
    """Test SearchResult model."""

    def test_search_result(self):
        """Test creating search result."""
        items = [
            SearchItem(id="1", type="video", title="Video 1"),
            SearchItem(id="2", type="video", title="Video 2"),
        ]
        next_page = NextPageData(next_page_token="token")

        result = SearchResult(items=items, next_page=next_page)
        assert len(result.items) == 2
        assert result.next_page.next_page_token == "token"

    def test_search_result_alias(self):
        """Test search result with alias."""
        data = {
            "items": [{"id": "1", "type": "video", "title": "Video 1"}],
            "nextPage": {"nextPageToken": "token"},
        }
        result = SearchResult(**data)
        assert len(result.items) == 1
        assert result.next_page.next_page_token == "token"


class TestVideoDetails:
    """Test VideoDetails model."""

    def test_minimal_video_details(self):
        """Test creating minimal video details."""
        details = VideoDetails(
            id="test_id",
            title="Test Title",
            channel="Test Channel",
            channel_id="test_channel_id",
            description="Test description",
        )
        assert details.id == "test_id"
        assert details.is_live is False
        assert details.keywords == []
        assert details.suggestion == []

    def test_full_video_details(self):
        """Test creating full video details."""
        details = VideoDetails(
            id="test_id",
            title="Test Title",
            thumbnail={"url": "test.jpg"},
            is_live=True,
            channel="Test Channel",
            channel_id="test_channel_id",
            description="Test description",
            keywords=["test", "video"],
            suggestion=[SearchItem(id="1", type="video", title="Suggestion")],
        )
        assert details.is_live is True
        assert details.keywords == ["test", "video"]
        assert len(details.suggestion) == 1

    def test_video_details_alias(self):
        """Test video details with aliases."""
        data = {
            "id": "test_id",
            "title": "Test Title",
            "isLive": True,
            "channel": "Test Channel",
            "channelId": "test_channel_id",
            "description": "Test description",
        }
        details = VideoDetails(**data)
        assert details.is_live is True
        assert details.channel_id == "test_channel_id"


class TestShortVideo:
    """Test ShortVideo model."""

    def test_short_video(self):
        """Test creating short video."""
        short = ShortVideo(
            id="short_id",
            type="reel",
            title="Short Title",
            thumbnail={"url": "thumb.jpg"},
            inline_playback_endpoint={"data": "test"},
        )
        assert short.id == "short_id"
        assert short.type == "reel"
        assert short.title == "Short Title"

    def test_short_video_alias(self):
        """Test short video with alias."""
        data = {
            "id": "short_id",
            "type": "reel",
            "title": "Short Title",
            "inlinePlaybackEndpoint": {"data": "test"},
        }
        short = ShortVideo(**data)
        assert short.inline_playback_endpoint["data"] == "test"


class TestPlaylistResult:
    """Test PlaylistResult model."""

    def test_playlist_result(self):
        """Test creating playlist result."""
        items = [SearchItem(id="1", type="video", title="Video 1")]
        playlist = PlaylistResult(items=items, metadata={"title": "Test Playlist"})

        assert len(playlist.items) == 1
        assert playlist.metadata["title"] == "Test Playlist"


class TestChannelResult:
    """Test ChannelResult model."""

    def test_channel_result(self):
        """Test creating channel result."""
        channel = ChannelResult(title="Home", content={"data": "test"})
        assert channel.title == "Home"
        assert channel.content["data"] == "test"


class TestYoutubeInitData:
    """Test YoutubeInitData model."""

    def test_youtube_init_data(self):
        """Test creating YouTube init data."""
        init_data = YoutubeInitData(
            initdata={"test": "data"}, api_token="test_token", context={"client": "web"}
        )
        assert init_data.initdata["test"] == "data"
        assert init_data.api_token == "test_token"

    def test_youtube_init_data_alias(self):
        """Test YouTube init data with alias."""
        data = {
            "initdata": {"test": "data"},
            "apiToken": "test_token",
            "context": {"client": "web"},
        }
        init_data = YoutubeInitData(**data)
        assert init_data.api_token == "test_token"


class TestYoutubePlayerDetail:
    """Test YoutubePlayerDetail model."""

    def test_youtube_player_detail(self):
        """Test creating YouTube player detail."""
        player = YoutubePlayerDetail(
            video_id="test_id", channel_id="test_channel", short_description="Test description"
        )
        assert player.video_id == "test_id"
        assert player.keywords == []

    def test_youtube_player_detail_alias(self):
        """Test YouTube player detail with aliases."""
        data = {
            "videoId": "test_id",
            "channelId": "test_channel",
            "shortDescription": "Test description",
        }
        player = YoutubePlayerDetail(**data)
        assert player.video_id == "test_id"
        assert player.channel_id == "test_channel"
        assert player.short_description == "Test description"
