"""Pytest configuration and fixtures."""

import json
import os
from unittest.mock import Mock

import pytest
from httpx import Response

from pytubesearch import PyTubeSearch


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, no external dependencies)")
    config.addinivalue_line("markers", "integration: Integration tests (may require network)")
    config.addinivalue_line("markers", "slow: Slow running tests")


@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture."""
    return {
        "timeout": float(os.getenv("PYTUBESEARCH_TEST_TIMEOUT", "10.0")),
        "enable_integration": os.getenv("PYTUBESEARCH_ENABLE_INTEGRATION", "false").lower()
        == "true",
        "max_integration_requests": int(os.getenv("PYTUBESEARCH_MAX_INTEGRATION_REQUESTS", "5")),
    }


@pytest.fixture
def mock_youtube_init_data():
    """Mock YouTube initialization data."""
    return {
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
                                                "videoId": "test_video_id",
                                                "title": {"runs": [{"text": "Test Video Title"}]},
                                                "thumbnail": {
                                                    "thumbnails": [{"url": "test_thumbnail.jpg"}]
                                                },
                                                "ownerText": {"runs": [{"text": "Test Channel"}]},
                                                "lengthText": {"simpleText": "5:30"},
                                                "shortBylineText": {
                                                    "runs": [{"text": "Test Channel"}]
                                                },
                                                "badges": [],
                                            }
                                        }
                                    ]
                                }
                            },
                            {
                                "continuationItemRenderer": {
                                    "continuationEndpoint": {
                                        "continuationCommand": {"token": "test_continuation_token"}
                                    }
                                }
                            },
                        ]
                    }
                }
            }
        }
    }


@pytest.fixture
def mock_youtube_player_data():
    """Mock YouTube player response data."""
    return {
        "videoDetails": {
            "videoId": "test_video_id",
            "title": "Test Video Title",
            "author": "Test Channel",
            "channelId": "test_channel_id",
            "shortDescription": "Test video description",
            "keywords": ["test", "video", "python"],
            "thumbnail": {"thumbnails": [{"url": "test_thumbnail.jpg"}]},
        }
    }


@pytest.fixture
def mock_html_response():
    """Mock HTML response from YouTube."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>YouTube</title></head>
    <body>
        <script>
            var ytInitialData = {"test": "data"};
            var ytInitialPlayerResponse = {"videoDetails": {"videoId": "test"}};
        </script>
        <script>
            window.ytplayer.config = {
                "INNERTUBE_CONTEXT": {"client": {"name": "WEB"}},
                "innertubeApiKey": "test_api_key"
            };
        </script>
    </body>
    </html>
    """


@pytest.fixture
def mock_response():
    """Create a mock HTTP response."""

    def _mock_response(content="", status_code=200, json_data=None):
        response = Mock(spec=Response)
        response.status_code = status_code
        response.text = content
        response.raise_for_status = Mock()

        if json_data:
            response.json = Mock(return_value=json_data)

        return response

    return _mock_response


@pytest.fixture
def pytubesearch_client():
    """Create a PyTubeSearch client for testing."""
    return PyTubeSearch(timeout=10.0)


@pytest.fixture
def sample_search_result():
    """Sample search result for testing."""
    return {
        "items": [
            {
                "id": "test_video_1",
                "type": "video",
                "title": "Test Video 1",
                "channel_title": "Test Channel 1",
                "thumbnail": {"thumbnails": [{"url": "thumb1.jpg"}]},
                "length": "10:30",
                "is_live": False,
            },
            {
                "id": "test_video_2",
                "type": "video",
                "title": "Test Video 2",
                "channel_title": "Test Channel 2",
                "thumbnail": {"thumbnails": [{"url": "thumb2.jpg"}]},
                "length": "5:45",
                "is_live": True,
            },
        ],
        "next_page": {
            "next_page_token": "test_token",
            "next_page_context": {"continuation": "test_continuation"},
        },
    }


@pytest.fixture
def sample_video_details():
    """Sample video details for testing."""
    return {
        "id": "test_video_id",
        "title": "Test Video Title",
        "thumbnail": {"thumbnails": [{"url": "test_thumb.jpg"}]},
        "is_live": False,
        "channel": "Test Channel",
        "channel_id": "test_channel_id",
        "description": "Test video description",
        "keywords": ["test", "video"],
        "suggestion": [],
    }
