"""Test PyTubeSearch client functionality."""

import json
import re
from unittest.mock import Mock, patch

import pytest
from httpx import RequestError

from pytubesearch import PyTubeSearch
from pytubesearch.client import DataExtractionError, PyTubeSearchError
from pytubesearch.models import SearchOptions, SearchResult


class TestPyTubeSearchInit:
    """Test PyTubeSearch initialization."""

    def test_init_default_timeout(self):
        """Test initialization with default timeout."""
        client = PyTubeSearch()
        assert client.timeout == 30.0
        client.close()

    def test_init_custom_timeout(self):
        """Test initialization with custom timeout."""
        client = PyTubeSearch(timeout=60.0)
        assert client.timeout == 60.0
        client.close()

    def test_context_manager(self):
        """Test using client as context manager."""
        with PyTubeSearch() as client:
            assert client is not None
            assert hasattr(client, "client")


class TestDataExtraction:
    """Test data extraction methods."""

    def test_get_youtube_init_data_success(self, mock_response):
        """Test successful YouTube init data extraction."""
        html_content = """
        <html>
        <script>var ytInitialData = {"test": "data"};</script>
        <script>"innertubeApiKey":"test_api_key"</script>
        <script>"INNERTUBE_CONTEXT":{"client": "web"},"INNERTUBE_CONTEXT_CLIENT_NAME"</script>
        </html>
        """

        with patch.object(PyTubeSearch, "__init__", lambda x, **kwargs: None):
            client = PyTubeSearch()
            client.timeout = 30.0

            mock_http_client = Mock()
            mock_http_client.get.return_value = mock_response(content=html_content)
            client.client = mock_http_client

            result = client._get_youtube_init_data("https://youtube.com")

            assert result.initdata["test"] == "data"
            assert result.api_token == "test_api_key"
            assert result.context["client"] == "web"

    def test_get_youtube_init_data_no_data(self, mock_response):
        """Test YouTube init data extraction failure."""
        html_content = "<html><body>No data here</body></html>"

        with patch.object(PyTubeSearch, "__init__", lambda x, **kwargs: None):
            client = PyTubeSearch()
            client.timeout = 30.0

            mock_http_client = Mock()
            mock_http_client.get.return_value = mock_response(content=html_content)
            client.client = mock_http_client

            with pytest.raises(DataExtractionError):
                client._get_youtube_init_data("https://youtube.com")

    def test_get_youtube_player_detail_success(self, mock_response):
        """Test successful YouTube player detail extraction."""
        html_content = """
        <html>
        <script>var ytInitialPlayerResponse = {"videoDetails": {"videoId": "test", "title": "Test"}};</script>
        </html>
        """

        with patch.object(PyTubeSearch, "__init__", lambda x, **kwargs: None):
            client = PyTubeSearch()
            client.timeout = 30.0

            mock_http_client = Mock()
            mock_http_client.get.return_value = mock_response(content=html_content)
            client.client = mock_http_client

            result = client._get_youtube_player_detail("https://youtube.com/watch?v=test")

            assert result.video_id == "test"

    def test_get_youtube_player_detail_no_data(self, mock_response):
        """Test YouTube player detail extraction failure."""
        html_content = "<html><body>No player data here</body></html>"

        with patch.object(PyTubeSearch, "__init__", lambda x, **kwargs: None):
            client = PyTubeSearch()
            client.timeout = 30.0

            mock_http_client = Mock()
            mock_http_client.get.return_value = mock_response(content=html_content)
            client.client = mock_http_client

            with pytest.raises(DataExtractionError):
                client._get_youtube_player_detail("https://youtube.com/watch?v=test")


class TestVideoItemRendering:
    """Test video item rendering methods."""

    def test_render_video_item_basic(self):
        """Test basic video item rendering."""
        video_data = {
            "videoRenderer": {
                "videoId": "test_id",
                "title": {"runs": [{"text": "Test Title"}]},
                "thumbnail": {"thumbnails": [{"url": "test.jpg"}]},
                "ownerText": {"runs": [{"text": "Test Channel"}]},
                "lengthText": {"simpleText": "10:30"},
                "shortBylineText": {"runs": [{"text": "Test Channel"}]},
            }
        }

        with patch.object(PyTubeSearch, "__init__", lambda x, **kwargs: None):
            client = PyTubeSearch()
            result = client._render_video_item(video_data)

            assert result.id == "test_id"
            assert result.title == "Test Title"
            assert result.channel_title == "Test Channel"
            assert result.is_live is False

    def test_render_video_item_live(self):
        """Test rendering live video item."""
        video_data = {
            "videoRenderer": {
                "videoId": "test_id",
                "title": {"runs": [{"text": "Live Stream"}]},
                "badges": [{"metadataBadgeRenderer": {"style": "BADGE_STYLE_TYPE_LIVE_NOW"}}],
            }
        }

        with patch.object(PyTubeSearch, "__init__", lambda x, **kwargs: None):
            client = PyTubeSearch()
            result = client._render_video_item(video_data)

            assert result.is_live is True

    def test_render_video_item_empty(self):
        """Test rendering empty video item."""
        with patch.object(PyTubeSearch, "__init__", lambda x, **kwargs: None):
            client = PyTubeSearch()
            result = client._render_video_item({})

            assert result.id == ""
            assert result.title == ""
            assert result.type == ""

    def test_render_compact_video_item(self):
        """Test rendering compact video item."""
        compact_data = {
            "compactVideoRenderer": {
                "videoId": "compact_id",
                "title": {"simpleText": "Compact Title"},
                "thumbnail": {"thumbnails": [{"url": "compact.jpg"}]},
                "shortBylineText": {"runs": [{"text": "Compact Channel"}]},
                "lengthText": {"simpleText": "5:45"},
            }
        }

        with patch.object(PyTubeSearch, "__init__", lambda x, **kwargs: None):
            client = PyTubeSearch()
            result = client._render_compact_video(compact_data)

            assert result.id == "compact_id"
            assert result.title == "Compact Title"
            assert result.channel_title == "Compact Channel"


class TestSearchFunctionality:
    """Test search functionality."""

    @patch("pytubesearch.client.PyTubeSearch._get_youtube_init_data")
    def test_search_basic(self, mock_init_data):
        """Test basic search functionality."""
        mock_init_data.return_value = Mock(
            initdata={
                "contents": {
                    "twoColumnSearchResultsRenderer": {
                        "primaryContents": {
                            "sectionListRenderer": {
                                "contents": [
                                    {
                                        "itemSectionRenderer": {
                                            "contents": [
                                                {
                                                    "videoRenderer": {
                                                        "videoId": "test_id",
                                                        "title": {"runs": [{"text": "Test Video"}]},
                                                        "ownerText": {
                                                            "runs": [{"text": "Test Channel"}]
                                                        },
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            api_token="test_token",
            context={"client": "web"},
        )

        with PyTubeSearch() as client:
            result = client.search("test query")

            assert isinstance(result, SearchResult)
            assert len(result.items) >= 0
            assert result.next_page.next_page_token == "test_token"

    def test_search_with_options(self):
        """Test search with filtering options."""
        with patch.object(PyTubeSearch, "_get_youtube_init_data") as mock_init:
            mock_init.return_value = Mock(
                initdata={
                    "contents": {
                        "twoColumnSearchResultsRenderer": {
                            "primaryContents": {"sectionListRenderer": {"contents": []}}
                        }
                    }
                },
                api_token=None,
                context=None,
            )

            with PyTubeSearch() as client:
                options = [SearchOptions(type="video")]
                result = client.search("test", options=options)

                # Verify the URL contains video filter
                call_args = mock_init.call_args[0][0]
                assert "sp=EgIQAQ%3D%3D" in call_args

    def test_search_with_limit(self):
        """Test search with result limit."""
        with patch.object(PyTubeSearch, "_get_youtube_init_data") as mock_init:
            # Mock data with multiple items
            mock_init.return_value = Mock(
                initdata={
                    "contents": {
                        "twoColumnSearchResultsRenderer": {
                            "primaryContents": {
                                "sectionListRenderer": {
                                    "contents": [
                                        {
                                            "itemSectionRenderer": {
                                                "contents": [
                                                    {
                                                        "videoRenderer": {
                                                            "videoId": f"id_{i}",
                                                            "title": {
                                                                "runs": [{"text": f"Video {i}"}]
                                                            },
                                                        }
                                                    }
                                                    for i in range(10)
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                },
                api_token=None,
                context=None,
            )

            with PyTubeSearch() as client:
                result = client.search("test", limit=3)
                assert len(result.items) <= 3

    def test_search_network_error(self):
        """Test search with network error."""
        with patch.object(PyTubeSearch, "_get_youtube_init_data") as mock_init:
            mock_init.side_effect = RequestError("Network error")

            with PyTubeSearch() as client:
                with pytest.raises(PyTubeSearchError):
                    client.search("test query")


class TestNextPageFunctionality:
    """Test next page functionality."""

    def test_next_page_success(self, mock_response):
        """Test successful next page request."""
        next_page_data = Mock()
        next_page_data.next_page_token = "test_token"
        next_page_data.next_page_context = {"continuation": "test_continuation"}

        response_data = {
            "onResponseReceivedCommands": [
                {
                    "appendContinuationItemsAction": {
                        "continuationItems": [
                            {
                                "itemSectionRenderer": {
                                    "contents": [
                                        {
                                            "videoRenderer": {
                                                "videoId": "next_video",
                                                "title": {"runs": [{"text": "Next Video"}]},
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        }

        with PyTubeSearch() as client:
            mock_http_client = Mock()
            mock_http_client.post.return_value = mock_response(json_data=response_data)
            client.client = mock_http_client

            result = client.next_page(next_page_data)

            assert isinstance(result, SearchResult)
            mock_http_client.post.assert_called_once()

    def test_next_page_no_token(self):
        """Test next page with no token."""
        next_page_data = Mock()
        next_page_data.next_page_token = None

        with PyTubeSearch() as client:
            with pytest.raises(PyTubeSearchError):
                client.next_page(next_page_data)


class TestVideoDetails:
    """Test video details functionality."""

    @patch("pytubesearch.client.PyTubeSearch._get_youtube_player_detail")
    @patch("pytubesearch.client.PyTubeSearch._get_youtube_init_data")
    def test_get_video_details_success(self, mock_init_data, mock_player_detail):
        """Test successful video details retrieval."""
        mock_player_detail.return_value = Mock(
            video_id="test_id",
            author="Test Channel",
            channel_id="test_channel",
            short_description="Test description",
            keywords=["test"],
            thumbnail={"url": "test.jpg"},
        )

        mock_init_data.return_value = Mock(
            initdata={
                "contents": {
                    "twoColumnWatchNextResults": {
                        "results": {
                            "results": {
                                "contents": [
                                    {
                                        "videoPrimaryInfoRenderer": {
                                            "title": {"runs": [{"text": "Test Video"}]},
                                            "viewCount": {
                                                "videoViewCountRenderer": {"isLive": False}
                                            },
                                        }
                                    },
                                    {
                                        "videoSecondaryInfoRenderer": {
                                            "owner": {
                                                "videoOwnerRenderer": {
                                                    "title": {"runs": [{"text": "Channel Owner"}]}
                                                }
                                            }
                                        }
                                    },
                                ]
                            }
                        },
                        "secondaryResults": {"secondaryResults": {"results": []}},
                    }
                }
            }
        )

        with PyTubeSearch() as client:
            result = client.get_video_details("test_id")

            assert result.id == "test_id"
            assert result.title == "Test Video"
            assert result.channel == "Test Channel"

    def test_get_video_details_error(self):
        """Test video details with error."""
        with patch.object(PyTubeSearch, "_get_youtube_init_data") as mock_init:
            mock_init.side_effect = Exception("Failed to get data")

            with PyTubeSearch() as client:
                with pytest.raises(PyTubeSearchError):
                    client.get_video_details("test_id")


class TestPlaylistData:
    """Test playlist data functionality."""

    @patch("pytubesearch.client.PyTubeSearch._get_youtube_init_data")
    def test_get_playlist_data_success(self, mock_init_data):
        """Test successful playlist data retrieval."""
        mock_init_data.return_value = Mock(
            initdata={
                "metadata": {"title": "Test Playlist"},
                "contents": {
                    "twoColumnBrowseResultsRenderer": {
                        "tabs": [
                            {
                                "tabRenderer": {
                                    "content": {
                                        "sectionListRenderer": {
                                            "contents": [
                                                {
                                                    "itemSectionRenderer": {
                                                        "contents": [
                                                            {
                                                                "playlistVideoListRenderer": {
                                                                    "contents": [
                                                                        {
                                                                            "playlistVideoRenderer": {
                                                                                "videoId": "playlist_video",
                                                                                "title": {
                                                                                    "runs": [
                                                                                        {
                                                                                            "text": "Playlist Video"
                                                                                        }
                                                                                    ]
                                                                                },
                                                                            }
                                                                        }
                                                                    ]
                                                                }
                                                            }
                                                        ]
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                },
            }
        )

        with PyTubeSearch() as client:
            result = client.get_playlist_data("test_playlist_id")

            assert len(result.items) >= 0
            assert result.metadata["title"] == "Test Playlist"

    def test_get_playlist_data_error(self):
        """Test playlist data with error."""
        with patch.object(PyTubeSearch, "_get_youtube_init_data") as mock_init:
            mock_init.side_effect = Exception("Failed to get playlist")

            with PyTubeSearch() as client:
                with pytest.raises(PyTubeSearchError):
                    client.get_playlist_data("test_playlist_id")


class TestChannelData:
    """Test channel data functionality."""

    @patch("pytubesearch.client.PyTubeSearch._get_youtube_init_data")
    def test_get_channel_by_id_success(self, mock_init_data):
        """Test successful channel data retrieval."""
        mock_init_data.return_value = Mock(
            initdata={
                "contents": {
                    "twoColumnBrowseResultsRenderer": {
                        "tabs": [
                            {"tabRenderer": {"title": "Home", "content": {"data": "test"}}},
                            {"tabRenderer": {"title": "Videos", "content": {"data": "videos"}}},
                        ]
                    }
                }
            }
        )

        with PyTubeSearch() as client:
            result = client.get_channel_by_id("test_channel_id")

            assert len(result) == 2
            assert result[0].title == "Home"
            assert result[1].title == "Videos"

    def test_get_channel_by_id_error(self):
        """Test channel data with error."""
        with patch.object(PyTubeSearch, "_get_youtube_init_data") as mock_init:
            mock_init.side_effect = Exception("Failed to get channel")

            with PyTubeSearch() as client:
                with pytest.raises(PyTubeSearchError):
                    client.get_channel_by_id("test_channel_id")


class TestSuggestions:
    """Test suggestions functionality."""

    @patch("pytubesearch.client.PyTubeSearch._get_youtube_init_data")
    def test_get_suggestions_success(self, mock_init_data):
        """Test successful suggestions retrieval."""
        mock_init_data.return_value = Mock(
            initdata={
                "contents": {
                    "twoColumnBrowseResultsRenderer": {
                        "tabs": [
                            {
                                "tabRenderer": {
                                    "content": {
                                        "richGridRenderer": {
                                            "contents": [
                                                {
                                                    "richItemRenderer": {
                                                        "content": {
                                                            "videoRenderer": {
                                                                "videoId": "suggested_video",
                                                                "title": {
                                                                    "runs": [
                                                                        {"text": "Suggested Video"}
                                                                    ]
                                                                },
                                                            }
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        )

        with PyTubeSearch() as client:
            result = client.get_suggestions(limit=5)

            assert len(result) <= 5
            if result:
                assert result[0].type == "video"

    def test_get_suggestions_error(self):
        """Test suggestions with error."""
        with patch.object(PyTubeSearch, "_get_youtube_init_data") as mock_init:
            mock_init.side_effect = Exception("Failed to get suggestions")

            with PyTubeSearch() as client:
                with pytest.raises(PyTubeSearchError):
                    client.get_suggestions()


class TestShortVideos:
    """Test short videos functionality."""

    @patch("pytubesearch.client.PyTubeSearch._get_youtube_init_data")
    def test_get_short_videos_success(self, mock_init_data):
        """Test successful short videos retrieval."""
        mock_init_data.return_value = Mock(
            initdata={
                "contents": {
                    "twoColumnBrowseResultsRenderer": {
                        "tabs": [
                            {
                                "tabRenderer": {
                                    "content": {
                                        "richGridRenderer": {
                                            "contents": [
                                                {
                                                    "richSectionRenderer": {
                                                        "content": {
                                                            "richShelfRenderer": {
                                                                "title": {
                                                                    "runs": [{"text": "Shorts"}]
                                                                },
                                                                "contents": [
                                                                    {
                                                                        "richItemRenderer": {
                                                                            "content": {
                                                                                "reelItemRenderer": {
                                                                                    "videoId": "short_id",
                                                                                    "headline": {
                                                                                        "simpleText": "Short Video"
                                                                                    },
                                                                                    "thumbnail": {
                                                                                        "thumbnails": [
                                                                                            {
                                                                                                "url": "short.jpg"
                                                                                            }
                                                                                        ]
                                                                                    },
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                ],
                                                            }
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        )

        with PyTubeSearch() as client:
            result = client.get_short_videos()

            assert isinstance(result, list)
            if result:
                assert result[0].type == "reel"

    def test_get_short_videos_error(self):
        """Test short videos with error."""
        with patch.object(PyTubeSearch, "_get_youtube_init_data") as mock_init:
            mock_init.side_effect = Exception("Failed to get shorts")

            with PyTubeSearch() as client:
                with pytest.raises(PyTubeSearchError):
                    client.get_short_videos()
