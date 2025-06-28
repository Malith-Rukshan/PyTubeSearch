#!/usr/bin/env python3
"""
Error Handling Example - PyTubeSearch

This example demonstrates comprehensive error handling patterns:
- Handling different types of exceptions
- Implementing retry logic
- Graceful degradation strategies
- Logging and debugging techniques

Usage:
    python error_handling.py
"""

import logging
import time

from pytubesearch import DataExtractionError, PyTubeSearch, PyTubeSearchError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("pytubesearch_errors.log")],
)
logger = logging.getLogger(__name__)


def basic_error_handling_example():
    """Demonstrate basic error handling patterns."""
    print("🛡️ Basic Error Handling Examples")
    print("-" * 50)

    # Example 1: Invalid search query
    print("1. Testing with empty search query:")
    with PyTubeSearch() as client:
        try:
            results = client.search("")
            print(f"   ✅ Unexpected success: {len(results.items)} items")
        except PyTubeSearchError as e:
            print(f"   ❌ PyTubeSearchError: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {type(e).__name__}: {e}")

    print()

    # Example 2: Invalid video ID
    print("2. Testing with invalid video ID:")
    with PyTubeSearch() as client:
        try:
            details = client.get_video_details("invalid_video_id_123")
            print(f"   ✅ Unexpected success: {details.title}")
        except DataExtractionError as e:
            print(f"   ❌ DataExtractionError: {e}")
        except PyTubeSearchError as e:
            print(f"   ❌ PyTubeSearchError: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {type(e).__name__}: {e}")

    print()

    # Example 3: Invalid playlist ID
    print("3. Testing with invalid playlist ID:")
    with PyTubeSearch() as client:
        try:
            playlist = client.get_playlist_data("invalid_playlist_123")
            print(f"   ✅ Unexpected success: {len(playlist.items)} items")
        except PyTubeSearchError as e:
            print(f"   ❌ PyTubeSearchError: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {type(e).__name__}: {e}")

    print()

    # Example 4: Network timeout simulation
    print("4. Testing with very short timeout:")
    try:
        with PyTubeSearch(timeout=0.001) as client:  # Very short timeout
            results = client.search("python programming")
            print(f"   ✅ Unexpected success: {len(results.items)} items")
    except Exception as e:
        print(f"   ❌ Timeout/Network error: {type(e).__name__}: {e}")


def retry_mechanism_example():
    """Demonstrate retry mechanisms for handling transient failures."""
    print("🔄 Retry Mechanism Examples")
    print("-" * 50)

    def search_with_retry(client, query, max_retries=3, delay=1.0):
        """Search with exponential backoff retry."""
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1} for query: {query}")
                results = client.search(query, limit=5)
                logger.info(f"Success on attempt {attempt + 1}")
                return results

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")

                if attempt < max_retries - 1:
                    wait_time = delay * (2**attempt)  # Exponential backoff
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed")
                    raise

    # Test retry mechanism
    queries = ["python programming", "invalid@#$query", "machine learning"]

    with PyTubeSearch() as client:
        for i, query in enumerate(queries, 1):
            print(f"{i}. Testing retry for: {query}")
            try:
                results = search_with_retry(client, query, max_retries=3)
                print(f"   ✅ Success: {len(results.items)} items found")

            except Exception as e:
                print(f"   ❌ Final failure: {type(e).__name__}: {e}")
            print()


def graceful_degradation_example():
    """Demonstrate graceful degradation when some operations fail."""
    print("🎯 Graceful Degradation Examples")
    print("-" * 50)

    # List of video IDs - some valid, some invalid
    video_ids = [
        "dQw4w9WgXcQ",  # Valid - Rick Roll
        "invalid_id_1",  # Invalid
        "9bZkp7q19f0",  # Valid - Gangnam Style
        "invalid_id_2",  # Invalid
        "kJQP7kiw5Fk",  # Valid - AlphaGo
    ]

    successful_details = []
    failed_ids = []

    with PyTubeSearch() as client:
        for i, video_id in enumerate(video_ids, 1):
            print(f"📹 Processing video {i}/{len(video_ids)}: {video_id}")

            try:
                details = client.get_video_details(video_id)
                successful_details.append(details)
                print(f"   ✅ Success: {details.title}")

            except Exception as e:
                failed_ids.append(video_id)
                print(f"   ❌ Failed: {type(e).__name__}: {e}")
                logger.error(f"Failed to get details for {video_id}: {e}")

            print()

    # Summary with graceful degradation
    print("📊 GRACEFUL DEGRADATION SUMMARY:")
    print(f"   Total videos processed: {len(video_ids)}")
    print(f"   Successful: {len(successful_details)}")
    print(f"   Failed: {len(failed_ids)}")
    print(f"   Success rate: {len(successful_details)/len(video_ids)*100:.1f}%")

    if successful_details:
        print(f"\n✅ Successfully retrieved details:")
        for details in successful_details:
            print(f"   📹 {details.title} by {details.channel}")

    if failed_ids:
        print(f"\n❌ Failed to retrieve details for:")
        for video_id in failed_ids:
            print(f"   🆔 {video_id}")


def error_logging_example():
    """Demonstrate comprehensive error logging."""
    print("📝 Error Logging Examples")
    print("-" * 50)

    # Configure detailed logging for this example
    detailed_logger = logging.getLogger("pytubesearch.detailed")
    detailed_handler = logging.FileHandler("detailed_errors.log")
    detailed_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    detailed_logger.addHandler(detailed_handler)
    detailed_logger.setLevel(logging.DEBUG)

    def logged_operation(operation_name, operation_func):
        """Wrapper function to log operations with detailed error info."""
        detailed_logger.info(f"Starting operation: {operation_name}")
        start_time = time.time()

        try:
            result = operation_func()
            end_time = time.time()
            detailed_logger.info(
                f"Operation {operation_name} completed in {end_time - start_time:.2f}s"
            )
            return result

        except Exception as e:
            end_time = time.time()
            detailed_logger.error(
                f"Operation {operation_name} failed after {end_time - start_time:.2f}s: "
                f"{type(e).__name__}: {e}"
            )
            raise

    with PyTubeSearch() as client:
        # Test various operations with logging
        operations = [
            ("normal_search", lambda: client.search("python programming", limit=3)),
            ("empty_search", lambda: client.search("")),
            ("invalid_video", lambda: client.get_video_details("invalid_123")),
            ("valid_video", lambda: client.get_video_details("dQw4w9WgXcQ")),
            ("invalid_playlist", lambda: client.get_playlist_data("invalid_playlist")),
        ]

        for op_name, op_func in operations:
            print(f"🔍 Testing: {op_name}")
            try:
                result = logged_operation(op_name, op_func)
                if hasattr(result, "items"):
                    print(f"   ✅ Success: {len(result.items)} items")
                elif hasattr(result, "title"):
                    print(f"   ✅ Success: {result.title}")
                else:
                    print(f"   ✅ Success: {type(result).__name__}")

            except Exception as e:
                print(f"   ❌ Failed: {type(e).__name__}")

            print()

    print("📁 Detailed logs written to: detailed_errors.log")


def context_manager_error_handling():
    """Demonstrate proper resource cleanup with error handling."""
    print("🔧 Context Manager Error Handling")
    print("-" * 50)

    # Example 1: Normal context manager usage
    print("1. Normal context manager usage:")
    try:
        with PyTubeSearch() as client:
            results = client.search("python tutorial", limit=3)
            print(f"   ✅ Success: {len(results.items)} items")

            # Simulate an error within the context
            if len(results.items) > 0:
                # This might fail
                details = client.get_video_details(results.items[0].id)
                print(f"   ✅ Video details: {details.title}")

    except Exception as e:
        print(f"   ❌ Error occurred: {type(e).__name__}: {e}")
        print("   ℹ️ Resources were properly cleaned up by context manager")

    print()

    # Example 2: Manual resource management with error handling
    print("2. Manual resource management:")
    client = None
    try:
        client = PyTubeSearch(timeout=30.0)
        results = client.search("machine learning", limit=2)
        print(f"   ✅ Success: {len(results.items)} items")

        # Simulate error
        raise ValueError("Simulated error for testing")

    except Exception as e:
        print(f"   ❌ Error occurred: {type(e).__name__}: {e}")

    finally:
        if client:
            client.close()
            print("   ✅ Resources manually cleaned up in finally block")


def error_recovery_strategies():
    """Demonstrate different error recovery strategies."""
    print("🔄 Error Recovery Strategies")
    print("-" * 50)

    with PyTubeSearch() as client:
        # Strategy 1: Fallback to alternative query
        print("1. Fallback strategy:")
        primary_query = "very specific rare programming topic that might not exist"
        fallback_query = "programming tutorial"

        try:
            results = client.search(primary_query, limit=5)
            if len(results.items) == 0:
                raise ValueError("No results found for primary query")
            print(f"   ✅ Primary query success: {len(results.items)} items")

        except Exception as e:
            print(f"   ⚠️ Primary query failed: {e}")
            print(f"   🔄 Trying fallback query: {fallback_query}")

            try:
                results = client.search(fallback_query, limit=5)
                print(f"   ✅ Fallback success: {len(results.items)} items")
            except Exception as e2:
                print(f"   ❌ Fallback also failed: {e2}")

        print()

        # Strategy 2: Partial success handling
        print("2. Partial success strategy:")
        video_ids = ["dQw4w9WgXcQ", "invalid_id", "9bZkp7q19f0"]
        partial_results = []

        for video_id in video_ids:
            try:
                details = client.get_video_details(video_id)
                partial_results.append(details)
                print(f"   ✅ {video_id}: {details.title}")
            except Exception as e:
                print(f"   ❌ {video_id}: Failed ({type(e).__name__})")
                # Continue processing other videos
                continue

        print(f"   📊 Partial success: {len(partial_results)}/{len(video_ids)} videos")


def main():
    """Main function to run error handling examples."""
    print("🛡️ PyTubeSearch - Error Handling Examples")
    print("=" * 60)

    # Run all error handling examples
    basic_error_handling_example()
    print("\n" + "=" * 60 + "\n")

    retry_mechanism_example()
    print("\n" + "=" * 60 + "\n")

    graceful_degradation_example()
    print("\n" + "=" * 60 + "\n")

    error_logging_example()
    print("\n" + "=" * 60 + "\n")

    context_manager_error_handling()
    print("\n" + "=" * 60 + "\n")

    error_recovery_strategies()

    print("\n✅ All error handling examples completed!")
    print("\n💡 Key takeaways:")
    print("   - Always use specific exception types when possible")
    print("   - Implement retry logic for transient failures")
    print("   - Use graceful degradation for partial failures")
    print("   - Log errors for debugging and monitoring")
    print("   - Properly manage resources with context managers")
    print("   - Have fallback strategies for critical operations")


if __name__ == "__main__":
    main()
