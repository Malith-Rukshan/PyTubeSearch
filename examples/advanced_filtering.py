#!/usr/bin/env python3
"""
Advanced Filtering Example - PyTubeSearch

This example demonstrates advanced search filtering capabilities:
- Content type filtering (video, channel, playlist, movie)
- Search with playlists included
- Multiple search strategies
- Combining different filters

Usage:
    python advanced_filtering.py
    python advanced_filtering.py "machine learning"
"""

import sys

from pytubesearch import PyTubeSearch, SearchOptions


def video_only_search(query: str):
    """Search for videos only."""
    print(f"🎥 Video-only search for: {query}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            # Create video filter
            video_options = [SearchOptions(type="video")]

            results = client.search(query, options=video_options, limit=5)

            print(f"Found {len(results.items)} videos:")
            for i, video in enumerate(results.items, 1):
                print(f"{i}. 📹 {video.title}")
                print(f"   Channel: {video.channel_title}")
                print(f"   Duration: {video.length or 'Unknown'}")
                if video.is_live:
                    print("   🔴 LIVE")
                print()

        except Exception as e:
            print(f"❌ Video search failed: {e}")


def channel_only_search(query: str):
    """Search for channels only."""
    print(f"📺 Channel-only search for: {query}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            # Create channel filter
            channel_options = [SearchOptions(type="channel")]

            results = client.search(query, options=channel_options, limit=5)

            print(f"Found {len(results.items)} channels:")
            for i, channel in enumerate(results.items, 1):
                print(f"{i}. 📺 {channel.title}")
                print(f"   ID: {channel.id}")
                print(f"   Type: {channel.type}")
                print()

        except Exception as e:
            print(f"❌ Channel search failed: {e}")


def playlist_only_search(query: str):
    """Search for playlists only."""
    print(f"📋 Playlist-only search for: {query}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            # Create playlist filter
            playlist_options = [SearchOptions(type="playlist")]

            results = client.search(query, options=playlist_options, limit=5)

            print(f"Found {len(results.items)} playlists:")
            for i, playlist in enumerate(results.items, 1):
                print(f"{i}. 📋 {playlist.title}")
                print(f"   ID: {playlist.id}")
                if playlist.video_count:
                    print(f"   Videos: {playlist.video_count}")
                print()

        except Exception as e:
            print(f"❌ Playlist search failed: {e}")


def movie_search(query: str):
    """Search for movies."""
    print(f"🎬 Movie search for: {query}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            # Create movie filter
            movie_options = [SearchOptions(type="movie")]

            results = client.search(query, options=movie_options, limit=5)

            print(f"Found {len(results.items)} movies:")
            for i, movie in enumerate(results.items, 1):
                print(f"{i}. 🎬 {movie.title}")
                print(f"   Channel: {movie.channel_title}")
                print(f"   Duration: {movie.length or 'Unknown'}")
                print()

        except Exception as e:
            print(f"❌ Movie search failed: {e}")


def search_with_playlists_included(query: str):
    """Search with playlists included in mixed results."""
    print(f"🔍 Mixed search (including playlists) for: {query}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            # Search with playlists included
            results = client.search(query, with_playlist=True, limit=8)

            print(f"Found {len(results.items)} mixed results:")
            for i, item in enumerate(results.items, 1):
                emoji = {"video": "📹", "channel": "📺", "playlist": "📋"}.get(item.type, "📄")

                print(f"{i}. {emoji} {item.title}")
                print(f"   Type: {item.type.upper()}")

                if item.type == "video":
                    print(f"   Channel: {item.channel_title}")
                    print(f"   Duration: {item.length or 'Unknown'}")
                    if item.is_live:
                        print("   🔴 LIVE")
                elif item.type == "playlist" and item.video_count:
                    print(f"   Videos: {item.video_count}")

                print()

        except Exception as e:
            print(f"❌ Mixed search failed: {e}")


def comparative_search_example(query: str):
    """Compare results across different content types."""
    print(f"📊 Comparative search analysis for: {query}")
    print("-" * 50)

    content_types = ["video", "channel", "playlist", "movie"]
    results_summary = {}

    with PyTubeSearch() as client:
        for content_type in content_types:
            try:
                options = [SearchOptions(type=content_type)]
                results = client.search(query, options=options, limit=3)
                results_summary[content_type] = len(results.items)

                print(f"{content_type.upper()}S ({len(results.items)} found):")
                for item in results.items:
                    print(f"  • {item.title[:60]}...")
                print()

            except Exception as e:
                print(f"  ❌ {content_type} search failed: {e}")
                results_summary[content_type] = 0

    # Summary
    print("📈 SUMMARY:")
    for content_type, count in results_summary.items():
        print(f"   {content_type.capitalize()}s: {count}")


def search_quality_filter_example(query: str):
    """Example of filtering search results by quality indicators."""
    print(f"⭐ Quality-filtered search for: {query}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            # Get more results to filter from
            results = client.search(query, limit=15)

            # Filter for videos with titles (basic quality indicator)
            quality_videos = [
                item
                for item in results.items
                if item.type == "video"
                and item.title
                and len(item.title) > 10  # Reasonable title length
                and item.channel_title  # Has channel info
            ]

            print(f"Quality-filtered results ({len(quality_videos)} out of {len(results.items)}):")
            for i, video in enumerate(quality_videos[:5], 1):
                print(f"{i}. ⭐ {video.title}")
                print(f"   Channel: {video.channel_title}")
                print(f"   Duration: {video.length or 'Unknown'}")
                if video.is_live:
                    print("   🔴 LIVE")
                print()

        except Exception as e:
            print(f"❌ Quality filtering failed: {e}")


def main():
    """Main function to run advanced filtering examples."""
    print("🎯 PyTubeSearch - Advanced Filtering Examples")
    print("=" * 60)

    # Get query from command line or use default
    query = sys.argv[1] if len(sys.argv) > 1 else "python tutorial"

    # Run different filtering examples
    video_only_search(query)
    print("\n" + "=" * 60 + "\n")

    channel_only_search(query)
    print("\n" + "=" * 60 + "\n")

    playlist_only_search(query)
    print("\n" + "=" * 60 + "\n")

    movie_search(query)
    print("\n" + "=" * 60 + "\n")

    search_with_playlists_included(query)
    print("\n" + "=" * 60 + "\n")

    comparative_search_example(query)
    print("\n" + "=" * 60 + "\n")

    search_quality_filter_example(query)

    print("\n✅ All filtering examples completed!")
    print("\n💡 Next steps:")
    print("   - Try video_details.py for detailed video information")
    print("   - Try pagination_example.py for handling large result sets")
    print("   - Try batch_processing.py for multiple queries")


if __name__ == "__main__":
    main()
