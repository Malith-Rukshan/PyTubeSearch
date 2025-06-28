"""Edge case tests for PyTubeSearch."""

from unittest.mock import Mock, patch

import pytest

from pytubesearch import DataExtractionError, PyTubeSearch, PyTubeSearchError


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_search_results(self):
        """Test handling of empty search results."""
        mock_response_data = {
            "contents": {
                "twoColumnSearchResultsRenderer": {
                    "primaryContents": {"sectionListRenderer": {"contents": []}}
                }
            }
        }

        mock_init_data = Mock()
        mock_init_data.initdata = mock_response_data
        mock_init_data.api_token = None
        mock_init_data.context = None

        with patch.object(PyTubeSearch, "_get_youtube_init_data", return_value=mock_init_data):
            with PyTubeSearch() as client:
                result = client.search("nonexistent query")
                assert len(result.items) == 0
                assert result.next_page.next_page_token is None

    def test_malformed_video_data(self):
        """Test handling of malformed video data."""
        mock_response_data = {
            "contents": {
                "twoColumnSearchResultsRenderer": {
                    "primaryContents": {
                        "sectionListRenderer": {
                            "contents": [
                                {
                                    "itemSectionRenderer": {
                                        "contents": [
                                            # Missing required fields
                                            {"videoRenderer": {"videoId": "test1"}},
                                            # Empty video renderer
                                            {"videoRenderer": {}},
                                            # Malformed title
                                            {
                                                "videoRenderer": {
                                                    "videoId": "test2",
                                                    "title": {"malformed": "data"},
                                                }
                                            },
                                            # Valid item for comparison
                                            {
                                                "videoRenderer": {
                                                    "videoId": "test3",
                                                    "title": {"runs": [{"text": "Valid Video"}]},
                                                    "ownerText": {
                                                        "runs": [{"text": "Valid Channel"}]
                                                    },
                                                }
                                            },
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }

        mock_init_data = Mock()
        mock_init_data.initdata = mock_response_data
        mock_init_data.api_token = "test_token"
        mock_init_data.context = {"client": "web"}

        with patch.object(PyTubeSearch, "_get_youtube_init_data", return_value=mock_init_data):
            with PyTubeSearch() as client:
                result = client.search("test query")

                # Should handle malformed data gracefully
                assert len(result.items) == 4  # All items should be processed

                # Check that valid item is processed correctly
                valid_item = next((item for item in result.items if item.id == "test3"), None)
                assert valid_item is not None
                assert valid_item.title == "Valid Video"

    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters."""
        special_queries = [
            "python programming 🐍",
            "машинное обучение",  # Russian
            "机器学习",  # Chinese
            "プログラミング",  # Japanese
            "🚀 rocket science 🚀",
            "special chars: !@#$%^&*()",
            "emojis 😀😃😄😁😆",
        ]

        mock_response_data = {
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
                                                    "videoId": "unicode_test",
                                                    "title": {
                                                        "runs": [{"text": "Unicode Test Video 🎯"}]
                                                    },
                                                    "ownerText": {
                                                        "runs": [{"text": "Test Channel 频道"}]
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
        }

        mock_init_data = Mock()
        mock_init_data.initdata = mock_response_data
        mock_init_data.api_token = "test_token"
        mock_init_data.context = {"client": "web"}

        with patch.object(PyTubeSearch, "_get_youtube_init_data", return_value=mock_init_data):
            with PyTubeSearch() as client:
                for query in special_queries:
                    result = client.search(query, limit=1)
                    # Should not raise exceptions and should return valid results
                    assert isinstance(result.items, list)
                    if result.items:
                        assert result.items[0].title == "Unicode Test Video 🎯"

    def test_very_long_strings(self):
        """Test handling of very long strings."""
        # Very long query
        long_query = "a" * 1000

        # Very long video title
        long_title = "Very Long Video Title " + "x" * 500

        mock_response_data = {
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
                                                    "videoId": "long_test",
                                                    "title": {"runs": [{"text": long_title}]},
                                                    "ownerText": {
                                                        "runs": [
                                                            {
                                                                "text": "Long Channel Name "
                                                                + "y" * 200
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
                }
            }
        }

        mock_init_data = Mock()
        mock_init_data.initdata = mock_response_data
        mock_init_data.api_token = "test_token"
        mock_init_data.context = {"client": "web"}

        with patch.object(PyTubeSearch, "_get_youtube_init_data", return_value=mock_init_data):
            with PyTubeSearch() as client:
                result = client.search(long_query, limit=1)

                # Should handle long strings without issues
                assert len(result.items) == 1
                assert result.items[0].title == long_title
                assert len(result.items[0].channel_title) > 200

    def test_nested_data_structures(self):
        """Test handling of deeply nested or complex data structures."""
        complex_mock_data = {
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
                                                    "videoId": "complex_test",
                                                    "title": {
                                                        "runs": [
                                                            {"text": "Complex"},
                                                            {"text": " Video"},
                                                            {"text": " Title"},
                                                        ]
                                                    },
                                                    "ownerText": {
                                                        "runs": [{"text": "Complex Channel"}]
                                                    },
                                                    "thumbnail": {
                                                        "thumbnails": [
                                                            {
                                                                "url": "https://example.com/thumb1.jpg",
                                                                "width": 120,
                                                                "height": 90,
                                                            },
                                                            {
                                                                "url": "https://example.com/thumb2.jpg",
                                                                "width": 320,
                                                                "height": 180,
                                                            },
                                                        ]
                                                    },
                                                    "badges": [
                                                        {
                                                            "metadataBadgeRenderer": {
                                                                "style": "BADGE_STYLE_TYPE_LIVE_NOW",
                                                                "label": "LIVE",
                                                            }
                                                        }
                                                    ],
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
        }

        mock_init_data = Mock()
        mock_init_data.initdata = complex_mock_data
        mock_init_data.api_token = "test_token"
        mock_init_data.context = {"client": "web"}

        with patch.object(PyTubeSearch, "_get_youtube_init_data", return_value=mock_init_data):
            with PyTubeSearch() as client:
                result = client.search("complex test", limit=1)

                assert len(result.items) == 1
                item = result.items[0]

                # Should properly parse complex nested data
                assert item.title == "Complex Video Title"  # Combined from runs
                assert item.channel_title == "Complex Channel"
                assert item.is_live is True  # Should detect live badge
                assert item.thumbnail is not None

    def test_missing_optional_fields(self):
        """Test handling when optional fields are missing."""
        minimal_mock_data = {
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
                                                    "videoId": "minimal_test",
                                                    "title": {"runs": [{"text": "Minimal Video"}]},
                                                    # Missing: ownerText, thumbnail, lengthText, etc.
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
        }

        mock_init_data = Mock()
        mock_init_data.initdata = minimal_mock_data
        mock_init_data.api_token = "test_token"
        mock_init_data.context = {"client": "web"}

        with patch.object(PyTubeSearch, "_get_youtube_init_data", return_value=mock_init_data):
            with PyTubeSearch() as client:
                result = client.search("minimal test", limit=1)

                assert len(result.items) == 1
                item = result.items[0]

                # Should handle missing fields gracefully
                assert item.id == "minimal_test"
                assert item.title == "Minimal Video"
                assert item.channel_title == ""  # Should default to empty string
                assert item.length is None or item.length == ""
                assert item.is_live is False  # Should default to False

    def test_null_and_none_values(self):
        """Test handling of null/None values in data."""
        null_mock_data = {
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
                                                    "videoId": "null_test",
                                                    "title": {
                                                        "runs": [{"text": "Null Test Video"}]
                                                    },
                                                    "ownerText": None,
                                                    "thumbnail": None,
                                                    "lengthText": None,
                                                    "badges": None,
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
        }

        mock_init_data = Mock()
        mock_init_data.initdata = null_mock_data
        mock_init_data.api_token = None
        mock_init_data.context = None

        with patch.object(PyTubeSearch, "_get_youtube_init_data", return_value=mock_init_data):
            with PyTubeSearch() as client:
                result = client.search("null test", limit=1)

                assert len(result.items) == 1
                item = result.items[0]

                # Should handle null values gracefully
                assert item.id == "null_test"
                assert item.title == "Null Test Video"
                # Should not raise exceptions for null values

    def test_concurrent_client_creation_and_disposal(self):
        """Test rapid creation and disposal of clients."""
        import threading
        import time

        def create_and_use_client(results_list, errors_list):
            try:
                client = PyTubeSearch(timeout=1.0)
                try:
                    # Simulate some work
                    time.sleep(0.1)
                    results_list.append("success")
                finally:
                    client.close()
            except Exception as e:
                errors_list.append(str(e))

        results = []
        errors = []
        threads = []

        # Create multiple threads that rapidly create/dispose clients
        for _ in range(10):
            thread = threading.Thread(target=create_and_use_client, args=(results, errors))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Should not have any errors
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10

    def test_extremely_large_limit_values(self):
        """Test handling of very large limit values."""
        mock_response_data = {
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
                                                    "videoId": f"limit_test_{i}",
                                                    "title": {"runs": [{"text": f"Video {i}"}]},
                                                }
                                            }
                                            for i in range(5)  # Only 5 actual results
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }

        mock_init_data = Mock()
        mock_init_data.initdata = mock_response_data
        mock_init_data.api_token = "test_token"
        mock_init_data.context = {"client": "web"}

        with patch.object(PyTubeSearch, "_get_youtube_init_data", return_value=mock_init_data):
            with PyTubeSearch() as client:
                # Test with extremely large limit
                result = client.search("test", limit=999999)

                # Should not crash and should return available results
                assert len(result.items) == 5  # Only 5 results available

                # Test with zero limit
                result_zero = client.search("test", limit=0)
                assert len(result_zero.items) == 5  # Should return all available

    def test_invalid_data_types_in_response(self):
        """Test handling when response contains unexpected data types."""
        invalid_mock_data = {
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
                                                    "videoId": 12345,  # Number instead of string
                                                    "title": {
                                                        "runs": [{"text": 678}]
                                                    },  # Number instead of string
                                                    "ownerText": {
                                                        "runs": [{"text": True}]
                                                    },  # Boolean instead of string
                                                    "isLive": "yes",  # String instead of boolean
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
        }

        mock_init_data = Mock()
        mock_init_data.initdata = invalid_mock_data
        mock_init_data.api_token = "test_token"
        mock_init_data.context = {"client": "web"}

        with patch.object(PyTubeSearch, "_get_youtube_init_data", return_value=mock_init_data):
            with PyTubeSearch() as client:
                # Should handle invalid data types gracefully
                result = client.search("invalid types test", limit=1)

                # Should not crash and should convert types appropriately
                assert len(result.items) == 1
                item = result.items[0]

                # Should convert to strings where appropriate
                assert isinstance(item.id, str)
                assert isinstance(item.title, str)
