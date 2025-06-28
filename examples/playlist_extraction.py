#!/usr/bin/env python3
"""
Playlist Extraction Example - PyTubeSearch

This example demonstrates how to work with YouTube playlists:
- Extracting playlist contents
- Getting playlist metadata
- Analyzing playlist structure
- Handling different playlist types

Usage:
    python playlist_extraction.py
    python playlist_extraction.py "PLI523PxNjNxwzlFjRBgDdPjlyA0_ZNtwJ"
"""

import sys

from pytubesearch import PyTubeSearch


def extract_playlist_example(playlist_id: str):
    """Extract complete playlist information."""
    print(f"📋 Extracting playlist: {playlist_id}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            playlist = client.get_playlist_data(playlist_id)

            # Metadata
            print("📊 PLAYLIST METADATA:")
            if playlist.metadata:
                print(f"   Raw metadata available: YES")
                # Try to extract common metadata fields
                if isinstance(playlist.metadata, dict):
                    title = playlist.metadata.get("title", "Unknown")
                    print(f"   Title: {title}")
            else:
                print("   Raw metadata available: NO")
            print()

            # Content analysis
            print("📹 CONTENT ANALYSIS:")
            print(f"   Total videos: {len(playlist.items)}")

            if playlist.items:
                # Video statistics
                videos_with_duration = [v for v in playlist.items if v.length]
                live_videos = [v for v in playlist.items if v.is_live]

                print(f"   Videos with duration info: {len(videos_with_duration)}")
                print(f"   Live videos: {len(live_videos)}")
                print()

                # Show first few videos
                print("🎥 FIRST 5 VIDEOS:")
                for i, video in enumerate(playlist.items[:5], 1):
                    print(f"   {i}. {video.title}")
                    print(f"      Channel: {video.channel_title or 'Unknown'}")
                    print(f"      Duration: {video.length or 'Unknown'}")
                    print(f"      Video ID: {video.id}")
                    if video.is_live:
                        print("      🔴 LIVE")
                    print()

                if len(playlist.items) > 5:
                    print(f"   ... and {len(playlist.items) - 5} more videos")
            else:
                print("   No videos found in playlist")

        except Exception as e:
            print(f"❌ Playlist extraction failed: {e}")


def search_and_extract_playlists_example(query: str):
    """Search for playlists and extract their contents."""
    print(f"🔍 Searching for playlists: {query}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            # Search for playlists
            from pytubesearch import SearchOptions

            playlist_options = [SearchOptions(type="playlist")]
            results = client.search(query, options=playlist_options, limit=3)

            if not results.items:
                print("No playlists found")
                return

            print(f"Found {len(results.items)} playlists:")
            print()

            # Extract each playlist
            for i, playlist_item in enumerate(results.items, 1):
                print(f"{i}. 📋 {playlist_item.title}")
                print(f"   ID: {playlist_item.id}")
                if playlist_item.video_count:
                    print(f"   Video Count: {playlist_item.video_count}")

                try:
                    # Get detailed playlist data
                    playlist_data = client.get_playlist_data(playlist_item.id, limit=3)
                    print(f"   Extracted Videos: {len(playlist_data.items)}")

                    for j, video in enumerate(playlist_data.items, 1):
                        print(f"      {j}. {video.title[:50]}...")
                        print(f"         Channel: {video.channel_title}")

                except Exception as e:
                    print(f"      ❌ Failed to extract: {e}")

                print()

        except Exception as e:
            print(f"❌ Playlist search failed: {e}")


def playlist_analysis_example(playlist_id: str):
    """Analyze playlist content and structure."""
    print(f"🔬 Analyzing playlist: {playlist_id}")
    print("-" * 50)

    with PyTubeSearch() as client:
        try:
            playlist = client.get_playlist_data(playlist_id)

            if not playlist.items:
                print("Playlist is empty or couldn't be accessed")
                return

            # Channel analysis
            print("📺 CHANNEL ANALYSIS:")
            channel_count = {}
            for video in playlist.items:
                if video.channel_title:
                    channel_count[video.channel_title] = (
                        channel_count.get(video.channel_title, 0) + 1
                    )

            print(f"   Unique channels: {len(channel_count)}")

            # Top channels
            top_channels = sorted(channel_count.items(), key=lambda x: x[1], reverse=True)[:5]
            print("   Top channels:")
            for channel, count in top_channels:
                print(f"      {channel}: {count} videos")
            print()

            # Title analysis
            print("📝 TITLE ANALYSIS:")
            all_words = []
            for video in playlist.items:
                all_words.extend(video.title.lower().split())

            # Word frequency
            word_count = {}
            for word in all_words:
                if len(word) > 3:  # Only count meaningful words
                    word_count[word] = word_count.get(word, 0) + 1

            top_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
            print(f"   Most common words:")
            for word, count in top_words:
                print(f"      {word}: {count} times")
            print()

            # Duration analysis (if available)
            print("⏱️ DURATION ANALYSIS:")
            videos_with_duration = [v for v in playlist.items if v.length]
            if videos_with_duration:
                print(
                    f"   Videos with duration info: {len(videos_with_duration)}/{len(playlist.items)}"
                )

                # Try to parse some common duration formats
                short_videos = []
                medium_videos = []
                long_videos = []

                for video in videos_with_duration:
                    duration_str = str(video.length)
                    if any(
                        indicator in duration_str for indicator in ["0:", "1:", "2:", "3:", "4:"]
                    ):
                        short_videos.append(video)
                    elif any(
                        indicator in duration_str
                        for indicator in ["5:", "6:", "7:", "8:", "9:", "10:"]
                    ):
                        medium_videos.append(video)
                    else:
                        long_videos.append(video)

                print(f"   Short videos (0-4 min): {len(short_videos)}")
                print(f"   Medium videos (5-10 min): {len(medium_videos)}")
                print(f"   Long videos (10+ min): {len(long_videos)}")
            else:
                print("   No duration information available")
            print()

            # Live content analysis
            live_videos = [v for v in playlist.items if v.is_live]
            print("🔴 LIVE CONTENT:")
            print(f"   Live videos: {len(live_videos)}")
            if live_videos:
                print("   Live video titles:")
                for live_video in live_videos[:3]:
                    print(f"      • {live_video.title}")

        except Exception as e:
            print(f"❌ Playlist analysis failed: {e}")


def compare_playlists_example(playlist_ids: list):
    """Compare multiple playlists."""
    print(f"⚖️ Comparing {len(playlist_ids)} playlists")
    print("-" * 50)

    with PyTubeSearch() as client:
        playlist_data = []

        # Extract all playlists
        for i, playlist_id in enumerate(playlist_ids, 1):
            try:
                print(f"📋 Extracting playlist {i}: {playlist_id}")
                data = client.get_playlist_data(playlist_id, limit=50)  # Limit for comparison
                playlist_data.append(
                    {"id": playlist_id, "data": data, "video_count": len(data.items)}
                )
                print(f"   ✅ {len(data.items)} videos extracted")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                playlist_data.append({"id": playlist_id, "data": None, "video_count": 0})

        print()

        # Comparison
        print("📊 COMPARISON RESULTS:")
        for i, pdata in enumerate(playlist_data, 1):
            print(f"Playlist {i} ({pdata['id']}):")

            if pdata["data"]:
                print(f"   Videos: {pdata['video_count']}")

                # Channel diversity
                channels = set()
                for video in pdata["data"].items:
                    if video.channel_title:
                        channels.add(video.channel_title)
                print(f"   Unique channels: {len(channels)}")

                # Live content
                live_count = sum(1 for v in pdata["data"].items if v.is_live)
                print(f"   Live videos: {live_count}")
            else:
                print("   Status: Failed to extract")
            print()

        # Find common videos
        if len([p for p in playlist_data if p["data"]]) >= 2:
            print("🔗 OVERLAP ANALYSIS:")
            valid_playlists = [p for p in playlist_data if p["data"]]

            for i, playlist1 in enumerate(valid_playlists):
                for j, playlist2 in enumerate(valid_playlists[i + 1 :], i + 1):
                    videos1 = set(v.id for v in playlist1["data"].items)
                    videos2 = set(v.id for v in playlist2["data"].items)

                    overlap = videos1.intersection(videos2)
                    print(f"   Playlist {i+1} ↔ Playlist {j+1}: {len(overlap)} common videos")


def main():
    """Main function to run playlist extraction examples."""
    print("📋 PyTubeSearch - Playlist Extraction Examples")
    print("=" * 60)

    # Default playlist IDs for examples
    default_playlists = [
        "PLI523PxNjNxwzlFjRBgDdPjlyA0_ZNtwJ",  # Example tech playlist
        "PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi",  # 3Blue1Brown Linear Algebra
    ]

    # Get playlist ID from command line or use default
    if len(sys.argv) > 1:
        playlist_id = sys.argv[1]
        playlist_ids = [playlist_id]
    else:
        playlist_id = default_playlists[0]
        playlist_ids = default_playlists

    # Run examples
    extract_playlist_example(playlist_id)
    print("\n" + "=" * 60 + "\n")

    search_and_extract_playlists_example("python tutorial")
    print("\n" + "=" * 60 + "\n")

    playlist_analysis_example(playlist_id)
    print("\n" + "=" * 60 + "\n")

    if len(playlist_ids) > 1:
        compare_playlists_example(playlist_ids)

    print("\n✅ All playlist extraction examples completed!")
    print("\n💡 Next steps:")
    print("   - Try pagination_example.py for handling large result sets")
    print("   - Try batch_processing.py for multiple queries")
    print("   - Try error_handling.py for robust error handling")


if __name__ == "__main__":
    main()
