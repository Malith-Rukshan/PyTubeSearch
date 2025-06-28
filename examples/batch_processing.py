#!/usr/bin/env python3
"""
Batch Processing Example - PyTubeSearch

This example demonstrates how to process multiple queries efficiently:
- Running multiple searches in sequence
- Aggregating results from different queries
- Handling errors in batch operations
- Performance optimization for bulk operations

Usage:
    python batch_processing.py
    python batch_processing.py "python,javascript,rust,go"
"""

import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from pytubesearch import PyTubeSearch


def sequential_batch_processing(queries: list):
    """Process multiple queries sequentially."""
    print(f"🔄 Sequential batch processing for {len(queries)} queries")
    print("-" * 50)

    all_results = {}
    total_start_time = time.time()

    with PyTubeSearch() as client:
        for i, query in enumerate(queries, 1):
            print(f"📝 Processing query {i}/{len(queries)}: {query}")

            try:
                start_time = time.time()
                results = client.search(query, limit=5)
                end_time = time.time()

                all_results[query] = {
                    "items": results.items,
                    "count": len(results.items),
                    "time": end_time - start_time,
                    "success": True,
                }

                print(f"   ✅ Found {len(results.items)} items in {end_time - start_time:.2f}s")

                # Show first result
                if results.items:
                    first_item = results.items[0]
                    print(f"   📹 Top result: {first_item.title[:50]}...")

            except Exception as e:
                print(f"   ❌ Failed: {e}")
                all_results[query] = {
                    "items": [],
                    "count": 0,
                    "time": 0,
                    "success": False,
                    "error": str(e),
                }

            print()

    total_end_time = time.time()
    total_time = total_end_time - total_start_time

    # Summary
    print("📊 SEQUENTIAL PROCESSING SUMMARY:")
    print(f"   Total queries: {len(queries)}")
    print(f"   Successful: {sum(1 for r in all_results.values() if r['success'])}")
    print(f"   Failed: {sum(1 for r in all_results.values() if not r['success'])}")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Average per query: {total_time/len(queries):.2f}s")

    total_items = sum(r["count"] for r in all_results.values())
    print(f"   Total items found: {total_items}")

    return all_results


def parallel_batch_processing(queries: list, max_workers: int = 3):
    """Process multiple queries in parallel using threads."""
    print(f"⚡ Parallel batch processing for {len(queries)} queries (max {max_workers} workers)")
    print("-" * 50)

    def search_query(query):
        """Search function for thread execution."""
        try:
            with PyTubeSearch() as client:
                start_time = time.time()
                results = client.search(query, limit=5)
                end_time = time.time()

                return {
                    "query": query,
                    "items": results.items,
                    "count": len(results.items),
                    "time": end_time - start_time,
                    "success": True,
                }
        except Exception as e:
            return {
                "query": query,
                "items": [],
                "count": 0,
                "time": 0,
                "success": False,
                "error": str(e),
            }

    all_results = {}
    total_start_time = time.time()

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all queries
        future_to_query = {executor.submit(search_query, query): query for query in queries}

        # Process completed futures
        for future in as_completed(future_to_query):
            query = future_to_query[future]
            try:
                result = future.result()
                all_results[query] = result

                if result["success"]:
                    print(f"✅ {query}: {result['count']} items in {result['time']:.2f}s")
                    if result["items"]:
                        first_item = result["items"][0]
                        print(f"   📹 Top: {first_item.title[:50]}...")
                else:
                    print(f"❌ {query}: {result.get('error', 'Unknown error')}")

            except Exception as e:
                print(f"❌ {query}: Thread execution failed: {e}")
                all_results[query] = {
                    "items": [],
                    "count": 0,
                    "time": 0,
                    "success": False,
                    "error": str(e),
                }

    total_end_time = time.time()
    total_time = total_end_time - total_start_time

    # Summary
    print(f"\n📊 PARALLEL PROCESSING SUMMARY:")
    print(f"   Total queries: {len(queries)}")
    print(f"   Successful: {sum(1 for r in all_results.values() if r['success'])}")
    print(f"   Failed: {sum(1 for r in all_results.values() if not r['success'])}")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Average per query: {total_time/len(queries):.2f}s")

    total_items = sum(r["count"] for r in all_results.values())
    print(f"   Total items found: {total_items}")

    return all_results


def aggregate_batch_results(results_dict: dict):
    """Aggregate and analyze results from batch processing."""
    print("📈 BATCH RESULTS AGGREGATION")
    print("-" * 50)

    # Collect all items
    all_items = []
    successful_queries = []

    for query, result in results_dict.items():
        if result["success"]:
            all_items.extend(result["items"])
            successful_queries.append(query)

    if not all_items:
        print("No items to aggregate")
        return

    print(f"📊 AGGREGATED STATISTICS:")
    print(f"   Total items across all queries: {len(all_items)}")
    print(f"   Successful queries: {len(successful_queries)}")
    print()

    # Content type analysis
    content_types = {}
    for item in all_items:
        content_types[item.type] = content_types.get(item.type, 0) + 1

    print("📋 CONTENT TYPE BREAKDOWN:")
    for content_type, count in sorted(content_types.items()):
        percentage = (count / len(all_items)) * 100
        print(f"   {content_type.capitalize()}s: {count} ({percentage:.1f}%)")
    print()

    # Channel analysis
    channels = {}
    for item in all_items:
        if item.channel_title:
            channels[item.channel_title] = channels.get(item.channel_title, 0) + 1

    if channels:
        print("📺 TOP CHANNELS (across all queries):")
        top_channels = sorted(channels.items(), key=lambda x: x[1], reverse=True)[:10]
        for channel, count in top_channels:
            print(f"   {channel}: {count} videos")
        print()

    # Live content analysis
    live_items = [item for item in all_items if item.is_live]
    print(f"🔴 LIVE CONTENT: {len(live_items)} items ({len(live_items)/len(all_items)*100:.1f}%)")

    # Query-specific analysis
    print("\n🔍 PER-QUERY BREAKDOWN:")
    for query in successful_queries:
        result = results_dict[query]
        query_items = result["items"]

        if query_items:
            videos = sum(1 for item in query_items if item.type == "video")
            channels = sum(1 for item in query_items if item.type == "channel")
            live = sum(1 for item in query_items if item.is_live)

            print(f"   {query}:")
            print(
                f"      Total: {len(query_items)}, Videos: {videos}, Channels: {channels}, Live: {live}"
            )


def compare_processing_methods(queries: list):
    """Compare sequential vs parallel processing performance."""
    print("⚖️ PROCESSING METHOD COMPARISON")
    print("-" * 50)

    print("🔄 Running sequential processing...")
    seq_start = time.time()
    seq_results = sequential_batch_processing(queries)
    seq_time = time.time() - seq_start

    print("\n" + "=" * 60 + "\n")

    print("⚡ Running parallel processing...")
    par_start = time.time()
    par_results = parallel_batch_processing(queries, max_workers=3)
    par_time = time.time() - par_start

    print("\n" + "=" * 60 + "\n")

    # Comparison
    print("📊 PERFORMANCE COMPARISON:")
    print(f"   Sequential time: {seq_time:.2f}s")
    print(f"   Parallel time: {par_time:.2f}s")

    if par_time > 0:
        speedup = seq_time / par_time
        print(f"   Speedup: {speedup:.2f}x")
        print(
            f"   Time saved: {seq_time - par_time:.2f}s ({(seq_time - par_time)/seq_time*100:.1f}%)"
        )

    # Results comparison
    seq_total = sum(r["count"] for r in seq_results.values() if r["success"])
    par_total = sum(r["count"] for r in par_results.values() if r["success"])

    print(f"   Sequential total items: {seq_total}")
    print(f"   Parallel total items: {par_total}")
    print(f"   Results consistency: {'✅ SAME' if seq_total == par_total else '⚠️ DIFFERENT'}")


def batch_error_handling_example(queries: list):
    """Demonstrate error handling in batch processing."""
    print("🛡️ BATCH ERROR HANDLING EXAMPLE")
    print("-" * 50)

    # Add some intentionally problematic queries
    test_queries = queries + ["", "a" * 1000, "invalid@#$%query"]

    results = {}
    error_count = 0

    with PyTubeSearch() as client:
        for i, query in enumerate(test_queries, 1):
            print(
                f"📝 Query {i}/{len(test_queries)}: {query[:30]}{'...' if len(query) > 30 else ''}"
            )

            try:
                # Add timeout and retry logic
                results[query] = client.search(query, limit=3)
                print(f"   ✅ Success: {len(results[query].items)} items")

            except Exception as e:
                error_count += 1
                error_type = type(e).__name__
                print(f"   ❌ {error_type}: {str(e)[:50]}...")

                # Log error but continue processing
                results[query] = None

    print(f"\n📊 ERROR HANDLING SUMMARY:")
    print(f"   Total queries: {len(test_queries)}")
    print(f"   Successful: {len(test_queries) - error_count}")
    print(f"   Failed: {error_count}")
    print(f"   Success rate: {(len(test_queries) - error_count)/len(test_queries)*100:.1f}%")


def main():
    """Main function to run batch processing examples."""
    print("📦 PyTubeSearch - Batch Processing Examples")
    print("=" * 60)

    # Get queries from command line or use defaults
    if len(sys.argv) > 1:
        queries = [q.strip() for q in sys.argv[1].split(",")]
    else:
        queries = ["python programming", "machine learning", "web development", "data science"]

    print(f"🎯 Processing queries: {', '.join(queries)}")
    print("\n" + "=" * 60 + "\n")

    # Run sequential processing
    seq_results = sequential_batch_processing(queries)
    print("\n" + "=" * 60 + "\n")

    # Aggregate results
    aggregate_batch_results(seq_results)
    print("\n" + "=" * 60 + "\n")

    # Compare processing methods (if we have multiple queries)
    if len(queries) > 1:
        compare_processing_methods(queries[:3])  # Limit to 3 for comparison
        print("\n" + "=" * 60 + "\n")

    # Error handling example
    batch_error_handling_example(queries[:2])  # Use subset for error demo

    print("\n✅ All batch processing examples completed!")
    print("\n💡 Next steps:")
    print("   - Try error_handling.py for comprehensive error handling")
    print("   - Try data_export.py for saving batch results")
    print("   - Try async_usage.py for async processing patterns")


if __name__ == "__main__":
    main()
