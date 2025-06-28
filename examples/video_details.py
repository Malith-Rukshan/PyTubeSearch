#!/usr/bin/env python3
"""
Video Details Example - PyTubeSearch

This example demonstrates how to get detailed information about YouTube videos:
- Getting comprehensive video metadata
- Extracting video suggestions
- Working with video thumbnails and descriptions
- Error handling for invalid video IDs

Usage:
    python video_details.py
    python video_details.py "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
"""

import sys

from pytubesearch import PyTubeSearch


def get_video_details_example(video_id: str):
    """Get detailed information about a specific video."""
    print(f"📹 Getting details for video ID: {video_id}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            details = client.get_video_details(video_id)

            # Basic information
            print("📋 BASIC INFORMATION:")
            print(f"   Title: {details.title}")
            print(f"   Video ID: {details.id}")
            print(f"   Channel: {details.channel}")
            print(f"   Channel ID: {details.channel_id}")
            print()

            # Status information
            print("📊 STATUS:")
            print(f"   Live Stream: {'🔴 YES' if details.is_live else '⚫ NO'}")
            print()

            # Description
            print("📝 DESCRIPTION:")
            description = (
                details.description[:200] + "..."
                if len(details.description) > 200
                else details.description
            )
            print(f"   {description}")
            print()

            # Keywords/Tags
            print("🏷️ KEYWORDS:")
            if details.keywords:
                for i, keyword in enumerate(details.keywords[:10], 1):  # Show first 10
                    print(f"   {i}. {keyword}")
                if len(details.keywords) > 10:
                    print(f"   ... and {len(details.keywords) - 10} more")
            else:
                print("   No keywords available")
            print()

            # Thumbnail information
            print("🖼️ THUMBNAIL:")
            if details.thumbnail:
                print(f"   Available: YES")
                # If thumbnail is a dict with thumbnails array
                if isinstance(details.thumbnail, dict) and "thumbnails" in details.thumbnail:
                    thumbnails = details.thumbnail["thumbnails"]
                    print(f"   Variants: {len(thumbnails)}")
                    for i, thumb in enumerate(thumbnails[:3], 1):  # Show first 3
                        if isinstance(thumb, dict) and "url" in thumb:
                            print(f"     {i}. {thumb['url']}")
            else:
                print("   Available: NO")
            print()

            # Suggested videos
            print("💡 SUGGESTED VIDEOS:")
            if details.suggestion:
                for i, suggestion in enumerate(details.suggestion[:5], 1):  # Show first 5
                    print(f"   {i}. {suggestion.title}")
                    print(f"      Channel: {suggestion.channel_title}")
                    print(f"      ID: {suggestion.id}")
                    print()
                if len(details.suggestion) > 5:
                    print(f"   ... and {len(details.suggestion) - 5} more suggestions")
            else:
                print("   No suggestions available")

        except Exception as e:
            print(f"❌ Failed to get video details: {e}")


def search_and_get_details_example(query: str):
    """Search for videos and get details for the first result."""
    print(f"🔍 Search and details example for: {query}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            # First, search for videos
            search_results = client.search(query, limit=3)

            if not search_results.items:
                print("No search results found")
                return

            # Filter for videos only
            videos = [item for item in search_results.items if item.type == "video"]

            if not videos:
                print("No videos found in search results")
                return

            print(f"Found {len(videos)} videos. Getting details for the first one:")
            print()

            # Get details for the first video
            first_video = videos[0]
            print(f"🎯 Selected: {first_video.title}")
            print()

            details = client.get_video_details(first_video.id)

            # Compare search result vs detailed info
            print("📊 COMPARISON (Search vs Details):")
            print(f"   Title (Search): {first_video.title}")
            print(f"   Title (Details): {details.title}")
            print(f"   Channel (Search): {first_video.channel_title}")
            print(f"   Channel (Details): {details.channel}")
            print(f"   Live Status: {'🔴 LIVE' if details.is_live else '⚫ NOT LIVE'}")
            print()

            # Show additional details not available in search
            print("➕ ADDITIONAL DETAILS:")
            print(f"   Description length: {len(details.description)} characters")
            print(f"   Keywords: {len(details.keywords)} tags")
            print(f"   Suggestions: {len(details.suggestion)} videos")

        except Exception as e:
            print(f"❌ Search and details failed: {e}")


def batch_video_details_example(video_ids: list):
    """Get details for multiple videos."""
    print(f"📦 Batch video details for {len(video_ids)} videos")
    print("-" * 50)

    with PyTubeSearch() as client:
        successful = 0
        failed = 0

        for i, video_id in enumerate(video_ids, 1):
            try:
                print(f"{i}. Processing {video_id}...")
                details = client.get_video_details(video_id)

                print(f"   ✅ {details.title}")
                print(f"   📺 {details.channel}")
                print(
                    f"   📊 {len(details.keywords)} keywords, {len(details.suggestion)} suggestions"
                )
                successful += 1

            except Exception as e:
                print(f"   ❌ Failed: {e}")
                failed += 1

            print()

        # Summary
        print("📈 BATCH SUMMARY:")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        print(f"   Total: {len(video_ids)}")


def video_analysis_example(video_id: str):
    """Analyze video content and metadata."""
    print(f"🔬 Video analysis for: {video_id}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            details = client.get_video_details(video_id)

            # Content analysis
            title_words = len(details.title.split())
            desc_words = len(details.description.split())

            print("📊 CONTENT ANALYSIS:")
            print(f"   Title length: {len(details.title)} characters ({title_words} words)")
            print(
                f"   Description length: {len(details.description)} characters ({desc_words} words)"
            )
            print(f"   Keywords count: {len(details.keywords)}")
            print(f"   Suggestions count: {len(details.suggestion)}")
            print()

            # Category hints from keywords
            print("🏷️ CONTENT CATEGORIES (from keywords):")
            tech_keywords = [
                "python",
                "programming",
                "coding",
                "software",
                "development",
                "tutorial",
            ]
            music_keywords = ["music", "song", "audio", "beat", "melody", "artist"]
            gaming_keywords = ["game", "gaming", "play", "player", "gameplay", "review"]

            categories = {
                "Tech/Programming": sum(
                    1
                    for kw in details.keywords
                    if any(tech in kw.lower() for tech in tech_keywords)
                ),
                "Music": sum(
                    1
                    for kw in details.keywords
                    if any(music in kw.lower() for music in music_keywords)
                ),
                "Gaming": sum(
                    1
                    for kw in details.keywords
                    if any(game in kw.lower() for game in gaming_keywords)
                ),
            }

            for category, count in categories.items():
                if count > 0:
                    print(f"   {category}: {count} related keywords")
            print()

            # Suggestion analysis
            print("💡 SUGGESTION ANALYSIS:")
            if details.suggestion:
                same_channel = sum(
                    1 for s in details.suggestion if s.channel_title == details.channel
                )
                print(f"   From same channel: {same_channel}/{len(details.suggestion)}")

                # Most common words in suggested titles
                all_words = []
                for suggestion in details.suggestion:
                    all_words.extend(suggestion.title.lower().split())

                word_count = {}
                for word in all_words:
                    if len(word) > 3:  # Only count words longer than 3 characters
                        word_count[word] = word_count.get(word, 0) + 1

                top_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:5]
                if top_words:
                    print(
                        f"   Common words in suggestions: {', '.join([f'{word} ({count})' for word, count in top_words])}"
                    )
            else:
                print("   No suggestions to analyze")

        except Exception as e:
            print(f"❌ Video analysis failed: {e}")


def main():
    """Main function to run video details examples."""
    print("📹 PyTubeSearch - Video Details Examples")
    print("=" * 60)

    # Default video IDs for examples
    default_video_ids = [
        "dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
        "9bZkp7q19f0",  # PSY - GANGNAM STYLE
        "kJQP7kiw5Fk",  # DeepMind - AlphaGo
    ]

    # Get video ID from command line or use default
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
        video_ids = [video_id]
    else:
        video_id = default_video_ids[0]
        video_ids = default_video_ids

    # Run examples
    get_video_details_example(video_id)
    print("\n" + "=" * 60 + "\n")

    search_and_get_details_example("python tutorial")
    print("\n" + "=" * 60 + "\n")

    if len(video_ids) > 1:
        batch_video_details_example(video_ids)
        print("\n" + "=" * 60 + "\n")

    video_analysis_example(video_id)

    print("\n✅ All video details examples completed!")
    print("\n💡 Next steps:")
    print("   - Try playlist_extraction.py for working with playlists")
    print("   - Try pagination_example.py for handling large result sets")
    print("   - Try error_handling.py for robust error handling")


if __name__ == "__main__":
    main()
