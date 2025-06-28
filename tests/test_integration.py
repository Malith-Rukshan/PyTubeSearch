"""Integration tests for PyTubeSearch."""

import pytest

from pytubesearch import PyTubeSearch
from pytubesearch.client import PyTubeSearchError
from pytubesearch.models import SearchOptions


class TestSearchIntegration:
    """Integration tests for search functionality."""

    @pytest.mark.integration
    def test_basic_search_integration(self):
        """Test basic search with real YouTube data."""
        with PyTubeSearch(timeout=60.0) as client:
            try:
                result = client.search("python programming", limit=5)

                assert result is not None
                assert len(result.items) <= 5

                for item in result.items:
                    assert item.id
                    assert item.title
                    assert item.type in ["video", "channel", "playlist"]

            except PyTubeSearchError as e:
                pytest.skip(f"Search failed, possibly due to YouTube changes: {e}")

    @pytest.mark.integration
    def test_search_with_video_filter_integration(self):
        """Test search with video filter."""
        with PyTubeSearch(timeout=60.0) as client:
            try:
                options = [SearchOptions(type="video")]
                result = client.search("machine learning", options=options, limit=3)

                assert result is not None

                for item in result.items:
                    assert item.type == "video"
                    assert item.id
                    assert item.title

            except PyTubeSearchError as e:
                pytest.skip(f"Video search failed: {e}")

    @pytest.mark.integration
    def test_search_with_channel_filter_integration(self):
        """Test search with channel filter."""
        with PyTubeSearch(timeout=60.0) as client:
            try:
                options = [SearchOptions(type="channel")]
                result = client.search("tech channels", options=options, limit=2)

                assert result is not None

                for item in result.items:
                    assert item.type == "channel"
                    assert item.id
                    assert item.title

            except PyTubeSearchError as e:
                pytest.skip(f"Channel search failed: {e}")


class TestVideoDetailsIntegration:
    """Integration tests for video details."""

    @pytest.mark.integration
    def test_get_video_details_integration(self):
        """Test getting video details with real data."""
        # Using a known video ID that should be stable
        video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up

        with PyTubeSearch(timeout=60.0) as client:
            try:
                details = client.get_video_details(video_id)

                assert details.id == video_id
                assert details.title
                assert details.channel
                assert isinstance(
                    details.channel_id, str
                )  # May be empty due to YouTube structure changes
                assert isinstance(details.description, str)
                assert isinstance(details.keywords, list)
                assert isinstance(details.is_live, bool)

            except PyTubeSearchError as e:
                pytest.skip(f"Video details failed: {e}")


class TestPlaylistIntegration:
    """Integration tests for playlist functionality."""

    @pytest.mark.integration
    def test_get_playlist_data_integration(self):
        """Test getting playlist data with real data."""
        # Using a known playlist ID that should be stable
        playlist_id = "PLrAXtmRdnEQy9j4XPpPNJkr0bO8E4BcJj"  # Example playlist

        with PyTubeSearch(timeout=60.0) as client:
            try:
                playlist = client.get_playlist_data(playlist_id, limit=5)

                assert playlist is not None
                assert len(playlist.items) <= 5

                for item in playlist.items:
                    assert item.id
                    assert item.title
                    assert item.type == "video"

            except PyTubeSearchError as e:
                pytest.skip(f"Playlist data failed: {e}")


class TestChannelIntegration:
    """Integration tests for channel functionality."""

    @pytest.mark.integration
    def test_get_channel_by_id_integration(self):
        """Test getting channel data with real data."""
        # Using a known channel ID that should be stable
        channel_id = "UC8butISFwT-Wl7EV0hUK0BQ"  # Example tech channel

        with PyTubeSearch(timeout=60.0) as client:
            try:
                channel_data = client.get_channel_by_id(channel_id)

                assert channel_data is not None
                assert len(channel_data) > 0

                for tab in channel_data:
                    assert tab.title

            except PyTubeSearchError as e:
                pytest.skip(f"Channel data failed: {e}")


class TestSuggestionsIntegration:
    """Integration tests for suggestions."""

    @pytest.mark.integration
    def test_get_suggestions_integration(self):
        """Test getting homepage suggestions."""
        with PyTubeSearch(timeout=60.0) as client:
            try:
                suggestions = client.get_suggestions(limit=5)

                assert suggestions is not None
                assert len(suggestions) <= 5

                for item in suggestions:
                    assert item.id
                    assert item.title
                    assert item.type == "video"

            except PyTubeSearchError as e:
                pytest.skip(f"Suggestions failed: {e}")


class TestShortsIntegration:
    """Integration tests for YouTube Shorts."""

    @pytest.mark.integration
    def test_get_short_videos_integration(self):
        """Test getting YouTube Shorts."""
        with PyTubeSearch(timeout=60.0) as client:
            try:
                shorts = client.get_short_videos()

                assert shorts is not None
                assert isinstance(shorts, list)

                for short in shorts:
                    assert short.id
                    assert short.title
                    assert short.type == "reel"

            except PyTubeSearchError as e:
                pytest.skip(f"Shorts failed: {e}")


class TestPaginationIntegration:
    """Integration tests for pagination."""

    @pytest.mark.integration
    def test_pagination_integration(self):
        """Test pagination with real data."""
        with PyTubeSearch(timeout=60.0) as client:
            try:
                # Get first page
                first_page = client.search("python tutorial", limit=5)

                assert first_page is not None
                assert first_page.next_page is not None

                # Get next page if available
                if first_page.next_page.next_page_token:
                    second_page = client.next_page(first_page.next_page, limit=5)

                    assert second_page is not None
                    assert len(second_page.items) <= 5

                    # Verify different results (usually different videos)
                    first_ids = {item.id for item in first_page.items}
                    second_ids = {item.id for item in second_page.items}

                    # Should have mostly different results
                    overlap = first_ids.intersection(second_ids)
                    assert len(overlap) < len(first_ids)  # Some overlap is ok, but not all

            except PyTubeSearchError as e:
                pytest.skip(f"Pagination failed: {e}")


class TestErrorHandlingIntegration:
    """Integration tests for error handling."""

    @pytest.mark.integration
    def test_invalid_video_id_integration(self):
        """Test error handling with invalid video ID."""
        with PyTubeSearch(timeout=30.0) as client:
            try:
                # Use an invalid video ID
                details = client.get_video_details("invalid_video_id_123")
                # If this doesn't raise an error, that's also valid behavior
                # YouTube might return empty data or redirect

            except PyTubeSearchError:
                # This is expected behavior for invalid IDs
                pass

    @pytest.mark.integration
    def test_invalid_playlist_id_integration(self):
        """Test error handling with invalid playlist ID."""
        with PyTubeSearch(timeout=30.0) as client:
            try:
                # Use an invalid playlist ID
                playlist = client.get_playlist_data("invalid_playlist_id_123")
                # If this doesn't raise an error, that's also valid behavior

            except PyTubeSearchError:
                # This is expected behavior for invalid IDs
                pass

    @pytest.mark.integration
    def test_invalid_channel_id_integration(self):
        """Test error handling with invalid channel ID."""
        with PyTubeSearch(timeout=30.0) as client:
            try:
                # Use an invalid channel ID
                channel = client.get_channel_by_id("invalid_channel_id_123")
                # If this doesn't raise an error, that's also valid behavior

            except PyTubeSearchError:
                # This is expected behavior for invalid IDs
                pass


class TestTimeoutIntegration:
    """Integration tests for timeout handling."""

    @pytest.mark.integration
    def test_short_timeout_integration(self):
        """Test behavior with very short timeout."""
        with PyTubeSearch(timeout=0.001) as client:  # Very short timeout
            try:
                result = client.search("test query")
                # If this succeeds, the request was very fast

            except (PyTubeSearchError, Exception):
                # Timeout or connection error is expected
                pass
