"""Performance tests for PyTubeSearch."""

import time
from unittest.mock import Mock, patch

import pytest

from pytubesearch import PyTubeSearch


@pytest.mark.slow
class TestPerformance:
    """Performance test suite."""

    def test_search_performance_benchmark(self, benchmark):
        """Benchmark search performance with mocked responses."""
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
                                                    "videoId": f"test_id_{i}",
                                                    "title": {
                                                        "runs": [{"text": f"Test Video {i}"}]
                                                    },
                                                    "ownerText": {
                                                        "runs": [{"text": "Test Channel"}]
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
        }

        mock_init_data = Mock()
        mock_init_data.initdata = mock_response_data
        mock_init_data.api_token = "test_token"
        mock_init_data.context = {"client": "web"}

        with patch.object(PyTubeSearch, "_get_youtube_init_data", return_value=mock_init_data):

            def search_operation():
                with PyTubeSearch() as client:
                    return client.search("test query", limit=10)

            result = benchmark(search_operation)
            assert len(result.items) == 10

    def test_batch_search_performance(self):
        """Test performance of batch search operations."""
        queries = ["python", "javascript", "go", "rust", "java"]

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
        }

        mock_init_data = Mock()
        mock_init_data.initdata = mock_response_data
        mock_init_data.api_token = "test_token"
        mock_init_data.context = {"client": "web"}

        with patch.object(PyTubeSearch, "_get_youtube_init_data", return_value=mock_init_data):
            start_time = time.time()

            with PyTubeSearch() as client:
                results = []
                for query in queries:
                    result = client.search(query, limit=5)
                    results.append(result)

            end_time = time.time()
            total_time = end_time - start_time

            # Performance assertions
            assert len(results) == len(queries)
            assert total_time < 5.0  # Should complete within 5 seconds
            assert total_time / len(queries) < 1.0  # Average less than 1 second per query

    def test_memory_usage_stability(self):
        """Test that memory usage remains stable during multiple operations."""
        import gc
        import sys

        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())

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
                                                    "videoId": f"test_id_{i}",
                                                    "title": {
                                                        "runs": [{"text": f"Test Video {i}"}]
                                                    },
                                                    "ownerText": {
                                                        "runs": [{"text": "Test Channel"}]
                                                    },
                                                }
                                            }
                                            for i in range(20)
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
            # Perform multiple search operations
            for i in range(10):
                with PyTubeSearch() as client:
                    result = client.search(f"test query {i}", limit=20)
                    assert len(result.items) == 20

        # Check memory usage after operations
        gc.collect()
        final_objects = len(gc.get_objects())

        # Memory should not have grown significantly
        memory_growth = final_objects - initial_objects
        assert memory_growth < 1000, f"Memory usage grew by {memory_growth} objects"

    @pytest.mark.slow
    def test_concurrent_client_usage(self):
        """Test performance with multiple concurrent clients."""
        import queue
        import threading

        results_queue = queue.Queue()
        errors_queue = queue.Queue()

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
        }

        mock_init_data = Mock()
        mock_init_data.initdata = mock_response_data
        mock_init_data.api_token = "test_token"
        mock_init_data.context = {"client": "web"}

        def worker(thread_id):
            try:
                with patch.object(
                    PyTubeSearch, "_get_youtube_init_data", return_value=mock_init_data
                ):
                    with PyTubeSearch() as client:
                        result = client.search(f"query {thread_id}", limit=5)
                        results_queue.put((thread_id, len(result.items)))
            except Exception as e:
                errors_queue.put((thread_id, str(e)))

        # Start multiple threads
        num_threads = 5
        threads = []

        start_time = time.time()

        for i in range(num_threads):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()
        total_time = end_time - start_time

        # Check results
        assert errors_queue.empty(), f"Errors occurred: {list(errors_queue.queue)}"
        assert results_queue.qsize() == num_threads, "Not all threads completed successfully"

        # Performance should scale reasonably
        assert total_time < 10.0, f"Concurrent operations took too long: {total_time}s"

    def test_large_result_set_handling(self):
        """Test handling of large result sets."""
        # Create a large mock dataset
        large_video_list = []
        for i in range(100):
            large_video_list.append(
                {
                    "videoRenderer": {
                        "videoId": f"large_test_id_{i}",
                        "title": {"runs": [{"text": f"Large Test Video {i}"}]},
                        "ownerText": {"runs": [{"text": f"Test Channel {i % 10}"}]},
                        "lengthText": {"simpleText": f"{i % 60}:{(i * 7) % 60:02d}"},
                    }
                }
            )

        mock_response_data = {
            "contents": {
                "twoColumnSearchResultsRenderer": {
                    "primaryContents": {
                        "sectionListRenderer": {
                            "contents": [{"itemSectionRenderer": {"contents": large_video_list}}]
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
            start_time = time.time()

            with PyTubeSearch() as client:
                result = client.search("large dataset test", limit=100)

            end_time = time.time()
            processing_time = end_time - start_time

            # Verify results
            assert len(result.items) == 100
            assert (
                processing_time < 2.0
            ), f"Large dataset processing took too long: {processing_time}s"

            # Verify data integrity
            for i, item in enumerate(result.items):
                assert item.id == f"large_test_id_{i}"
                assert f"Large Test Video {i}" in item.title
