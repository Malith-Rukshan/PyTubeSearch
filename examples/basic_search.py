#!/usr/bin/env python3
"""
Basic Search Example - PyTubeSearch

This example demonstrates the most basic usage of PyTubeSearch:
- Simple keyword search
- Displaying results
- Proper resource management

Usage:
    python basic_search.py
    python basic_search.py "custom search query"
"""

import sys

from pytubesearch import PyTubeSearch


def basic_search_example(query: str = "python programming"):
    """Demonstrate basic search functionality."""
    print(f"🔍 Searching for: {query}")
    print("-" * 50)

    # Method 1: Using context manager (recommended)
    with PyTubeSearch() as client:
        try:
            # Perform search with limit
            results = client.search(query, limit=5)

            print(f"Found {len(results.items)} results:")
            print()

            # Display results
            for i, item in enumerate(results.items, 1):
                print(f"{i}. 📹 {item.title}")
                print(f"   Channel: {item.channel_title or 'Unknown'}")
                print(f"   Type: {item.type}")
                print(f"   ID: {item.id}")
                if item.length:
                    print(f"   Duration: {item.length}")
                if item.is_live:
                    print("   🔴 LIVE")
                print()

            # Show pagination info
            if results.next_page.next_page_token:
                print("📄 More results available (use pagination example to see more)")
            else:
                print("📄 No more results available")

        except Exception as e:
            print(f"❌ Search failed: {e}")


def manual_resource_management_example(query: str):
    """Demonstrate manual resource management (alternative to context manager)."""
    print(f"\n🔧 Manual resource management example")
    print(f"🔍 Searching for: {query}")
    print("-" * 50)

    # Create client manually
    client = PyTubeSearch(timeout=30.0)

    try:
        results = client.search(query, limit=3)

        print(f"Found {len(results.items)} results:")
        for item in results.items:
            print(f"📹 {item.title} ({item.type})")

    except Exception as e:
        print(f"❌ Search failed: {e}")
    finally:
        # Important: Always close the client when done
        client.close()
        print("✅ Client resources cleaned up")


def search_statistics_example(query: str):
    """Show search statistics and metadata."""
    print(f"\n📊 Search statistics for: {query}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            results = client.search(query, limit=10)

            # Count different types of content
            videos = sum(1 for item in results.items if item.type == "video")
            channels = sum(1 for item in results.items if item.type == "channel")
            playlists = sum(1 for item in results.items if item.type == "playlist")
            live_streams = sum(1 for item in results.items if item.is_live)

            print(f"📊 Results breakdown:")
            print(f"   Total items: {len(results.items)}")
            print(f"   Videos: {videos}")
            print(f"   Channels: {channels}")
            print(f"   Playlists: {playlists}")
            print(f"   Live streams: {live_streams}")

            # Show longest and shortest videos (if any)
            video_items = [item for item in results.items if item.type == "video" and item.length]
            if video_items:
                print(f"\n📹 Video details:")
                for item in video_items[:3]:  # Show first 3 videos
                    print(f"   {item.title[:50]}... - {item.length}")

        except Exception as e:
            print(f"❌ Statistics collection failed: {e}")


def main():
    """Main function to run examples."""
    print("🎬 PyTubeSearch - Basic Search Examples")
    print("=" * 60)

    # Get query from command line or use default
    query = sys.argv[1] if len(sys.argv) > 1 else "python programming"

    # Run examples
    basic_search_example(query)
    manual_resource_management_example(query)
    search_statistics_example(query)

    print("\n✅ All examples completed!")
    print("\n💡 Next steps:")
    print("   - Try advanced_filtering.py for search filters")
    print("   - Try video_details.py for detailed video information")
    print("   - Try pagination_example.py for handling large result sets")


if __name__ == "__main__":
    main()
