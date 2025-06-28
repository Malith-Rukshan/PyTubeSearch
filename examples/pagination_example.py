#!/usr/bin/env python3
"""
Pagination Example - PyTubeSearch

This example demonstrates how to handle pagination for large result sets:
- Getting multiple pages of results
- Implementing pagination loops
- Handling pagination errors
- Collecting results across pages

Usage:
    python pagination_example.py
    python pagination_example.py "machine learning" 3
"""

import sys

from pytubesearch import PyTubeSearch


def basic_pagination_example(query: str, max_pages: int = 3):
    """Demonstrate basic pagination through search results."""
    print(f"📄 Basic pagination for: {query} (max {max_pages} pages)")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            all_results = []
            page_num = 1

            # Get first page
            print(f"📄 Getting page {page_num}...")
            results = client.search(query, limit=5)

            if not results.items:
                print("No results found")
                return

            all_results.extend(results.items)
            print(f"   Found {len(results.items)} items")

            # Show first page results
            for i, item in enumerate(results.items, 1):
                print(f"   {i}. {item.title[:60]}...")
            print()

            # Get additional pages
            current_results = results
            while current_results.next_page.next_page_token and page_num < max_pages:

                page_num += 1
                print(f"📄 Getting page {page_num}...")

                try:
                    current_results = client.next_page(current_results.next_page, limit=5)
                    all_results.extend(current_results.items)
                    print(f"   Found {len(current_results.items)} items")

                    # Show results from this page
                    for i, item in enumerate(current_results.items, 1):
                        page_item_num = len(all_results) - len(current_results.items) + i
                        print(f"   {page_item_num}. {item.title[:60]}...")
                    print()

                except Exception as e:
                    print(f"   ❌ Failed to get page {page_num}: {e}")
                    break

            # Summary
            print("📊 PAGINATION SUMMARY:")
            print(f"   Pages retrieved: {page_num}")
            print(f"   Total items: {len(all_results)}")
            print(f"   Items per page: ~{len(all_results) / page_num:.1f}")

            if current_results.next_page.next_page_token:
                print("   More pages available: YES")
            else:
                print("   More pages available: NO")

        except Exception as e:
            print(f"❌ Pagination failed: {e}")


def collect_all_available_results(query: str, max_items: int = 50):
    """Collect as many results as possible up to a maximum."""
    print(f"🗂️ Collecting up to {max_items} results for: {query}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            all_results = []
            page_num = 0

            # Get first page
            page_num += 1
            print(f"📄 Page {page_num}: ", end="")
            results = client.search(query, limit=10)

            if not results.items:
                print("No results found")
                return

            all_results.extend(results.items)
            print(f"{len(results.items)} items")

            # Continue until we have enough items or no more pages
            current_results = results
            while len(all_results) < max_items and current_results.next_page.next_page_token:

                page_num += 1
                print(f"📄 Page {page_num}: ", end="")

                try:
                    current_results = client.next_page(current_results.next_page, limit=10)

                    if not current_results.items:
                        print("No more items")
                        break

                    # Add items but don't exceed maximum
                    items_to_add = current_results.items[: max_items - len(all_results)]
                    all_results.extend(items_to_add)
                    print(f"{len(items_to_add)} items (total: {len(all_results)})")

                    if len(all_results) >= max_items:
                        print(f"📊 Reached maximum of {max_items} items")
                        break

                except Exception as e:
                    print(f"❌ Error: {e}")
                    break

            # Analysis of collected results
            print(f"\n📊 COLLECTION SUMMARY:")
            print(f"   Total collected: {len(all_results)}")
            print(f"   Pages processed: {page_num}")

            # Content type breakdown
            content_types = {}
            for item in all_results:
                content_types[item.type] = content_types.get(item.type, 0) + 1

            print("   Content breakdown:")
            for content_type, count in content_types.items():
                print(f"      {content_type.capitalize()}s: {count}")

            # Show sample of results
            print(f"\n🎯 SAMPLE RESULTS (first 5):")
            for i, item in enumerate(all_results[:5], 1):
                emoji = {"video": "📹", "channel": "📺", "playlist": "📋"}.get(item.type, "📄")
                print(f"   {i}. {emoji} {item.title}")
                print(f"      Type: {item.type}, Channel: {item.channel_title}")

        except Exception as e:
            print(f"❌ Collection failed: {e}")


def pagination_with_filtering_example(query: str):
    """Paginate through results while applying filters."""
    print(f"🎯 Filtered pagination for: {query}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            filtered_results = []
            page_num = 0
            total_processed = 0

            # Get first page
            page_num += 1
            results = client.search(query, limit=10)

            if not results.items:
                print("No results found")
                return

            # Filter function - only videos with certain criteria
            def is_good_video(item):
                return (
                    item.type == "video"
                    and item.title
                    and len(item.title) > 10
                    and item.channel_title
                    and not item.is_live
                )  # Exclude live streams for this example

            # Process first page
            page_filtered = [item for item in results.items if is_good_video(item)]
            filtered_results.extend(page_filtered)
            total_processed += len(results.items)

            print(
                f"📄 Page {page_num}: {len(page_filtered)}/{len(results.items)} items passed filter"
            )

            # Continue pagination while looking for good results
            current_results = results
            while (
                len(filtered_results) < 20  # Want at least 20 good results
                and current_results.next_page.next_page_token
                and page_num < 10
            ):  # Don't go beyond 10 pages

                page_num += 1

                try:
                    current_results = client.next_page(current_results.next_page, limit=10)

                    if not current_results.items:
                        break

                    # Apply filter
                    page_filtered = [item for item in current_results.items if is_good_video(item)]
                    filtered_results.extend(page_filtered)
                    total_processed += len(current_results.items)

                    print(
                        f"📄 Page {page_num}: {len(page_filtered)}/{len(current_results.items)} items passed filter"
                    )

                except Exception as e:
                    print(f"❌ Page {page_num} failed: {e}")
                    break

            # Results summary
            print(f"\n📊 FILTERING SUMMARY:")
            print(f"   Pages processed: {page_num}")
            print(f"   Total items seen: {total_processed}")
            print(f"   Items passed filter: {len(filtered_results)}")
            print(f"   Filter efficiency: {len(filtered_results)/total_processed*100:.1f}%")

            # Show filtered results
            print(f"\n✅ FILTERED RESULTS:")
            for i, item in enumerate(filtered_results[:8], 1):
                print(f"   {i}. 📹 {item.title}")
                print(f"      Channel: {item.channel_title}")
                print(f"      Duration: {item.length or 'Unknown'}")

        except Exception as e:
            print(f"❌ Filtered pagination failed: {e}")


def pagination_performance_test(query: str):
    """Test pagination performance and timing."""
    print(f"⏱️ Pagination performance test for: {query}")
    print("-" * 50)

    import time

    with PyTubeSearch() as client:
        try:
            page_times = []
            total_items = 0
            page_num = 0

            # Get first page
            page_num += 1
            start_time = time.time()
            results = client.search(query, limit=8)
            end_time = time.time()

            page_time = end_time - start_time
            page_times.append(page_time)
            total_items += len(results.items)

            print(f"📄 Page {page_num}: {len(results.items)} items in {page_time:.2f}s")

            # Get several more pages to test performance
            current_results = results
            while current_results.next_page.next_page_token and page_num < 5:  # Test 5 pages total

                page_num += 1
                start_time = time.time()

                try:
                    current_results = client.next_page(current_results.next_page, limit=8)
                    end_time = time.time()

                    page_time = end_time - start_time
                    page_times.append(page_time)
                    total_items += len(current_results.items)

                    print(
                        f"📄 Page {page_num}: {len(current_results.items)} items in {page_time:.2f}s"
                    )

                except Exception as e:
                    print(f"❌ Page {page_num} failed: {e}")
                    break

            # Performance analysis
            if page_times:
                avg_time = sum(page_times) / len(page_times)
                min_time = min(page_times)
                max_time = max(page_times)
                total_time = sum(page_times)

                print(f"\n⏱️ PERFORMANCE SUMMARY:")
                print(f"   Total pages: {len(page_times)}")
                print(f"   Total items: {total_items}")
                print(f"   Total time: {total_time:.2f}s")
                print(f"   Average page time: {avg_time:.2f}s")
                print(f"   Fastest page: {min_time:.2f}s")
                print(f"   Slowest page: {max_time:.2f}s")
                print(f"   Items per second: {total_items/total_time:.1f}")

        except Exception as e:
            print(f"❌ Performance test failed: {e}")


def main():
    """Main function to run pagination examples."""
    print("📄 PyTubeSearch - Pagination Examples")
    print("=" * 60)

    # Get query and max pages from command line or use defaults
    query = sys.argv[1] if len(sys.argv) > 1 else "python programming"
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    # Run examples
    basic_pagination_example(query, max_pages)
    print("\n" + "=" * 60 + "\n")

    collect_all_available_results(query, max_items=30)
    print("\n" + "=" * 60 + "\n")

    pagination_with_filtering_example(query)
    print("\n" + "=" * 60 + "\n")

    pagination_performance_test(query)

    print("\n✅ All pagination examples completed!")
    print("\n💡 Next steps:")
    print("   - Try batch_processing.py for multiple queries")
    print("   - Try error_handling.py for robust error handling")
    print("   - Try data_export.py for saving results")


if __name__ == "__main__":
    main()
