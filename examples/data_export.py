#!/usr/bin/env python3
"""
Data Export Example - PyTubeSearch

This example demonstrates how to export search results to different formats:
- JSON export with structured data
- CSV export for spreadsheet analysis
- HTML export for web viewing
- Text export for simple reports

Usage:
    python data_export.py
    python data_export.py "machine learning" --format json
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

from pytubesearch import PyTubeSearch


def export_to_json(results, filename="search_results.json"):
    """Export search results to JSON format."""
    print(f"📄 Exporting to JSON: {filename}")

    # Convert results to JSON-serializable format
    json_data = {
        "export_info": {
            "timestamp": datetime.now().isoformat(),
            "total_items": len(results),
            "exported_by": "PyTubeSearch Data Export Example",
        },
        "results": [],
    }

    for item in results:
        item_data = {
            "id": item.id,
            "type": item.type,
            "title": item.title,
            "channel_title": item.channel_title,
            "short_byline_text": item.short_byline_text,
            "length": item.length,
            "is_live": item.is_live,
            "video_count": item.video_count,
            "thumbnail": item.thumbnail,
        }
        json_data["results"].append(item_data)

    # Write to file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"   ✅ Exported {len(results)} items to {filename}")
    return filename


def export_to_csv(results, filename="search_results.csv"):
    """Export search results to CSV format."""
    print(f"📊 Exporting to CSV: {filename}")

    # Define CSV headers
    headers = [
        "ID",
        "Type",
        "Title",
        "Channel",
        "Duration",
        "Is_Live",
        "Video_Count",
        "Thumbnail_Available",
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(headers)

        # Write data rows
        for item in results:
            row = [
                item.id,
                item.type,
                item.title,
                item.channel_title or "",
                item.length or "",
                "Yes" if item.is_live else "No",
                item.video_count or "",
                "Yes" if item.thumbnail else "No",
            ]
            writer.writerow(row)

    print(f"   ✅ Exported {len(results)} items to {filename}")
    return filename


def export_to_html(results, filename="search_results.html", query=""):
    """Export search results to HTML format."""
    print(f"🌐 Exporting to HTML: {filename}")

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Search Results - {query}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #ff0000; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .stats {{ background-color: #fff; padding: 15px; border-radius: 5px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .item {{ background-color: #fff; margin: 10px 0; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .title {{ font-size: 18px; font-weight: bold; color: #1a0dab; text-decoration: none; }}
        .title:hover {{ text-decoration: underline; }}
        .channel {{ color: #606060; font-size: 14px; }}
        .meta {{ color: #606060; font-size: 12px; margin-top: 5px; }}
        .badge {{ background-color: #ff0000; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-left: 5px; }}
        .type-video {{ border-left: 4px solid #ff0000; }}
        .type-channel {{ border-left: 4px solid #00ff00; }}
        .type-playlist {{ border-left: 4px solid #0066cc; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 YouTube Search Results</h1>
        <p>Query: "{query}" | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    
    <div class="stats">
        <h3>📊 Search Statistics</h3>
        <p><strong>Total Results:</strong> {len(results)}</p>
        <p><strong>Videos:</strong> {sum(1 for item in results if item.type == "video")}</p>
        <p><strong>Channels:</strong> {sum(1 for item in results if item.type == "channel")}</p>
        <p><strong>Playlists:</strong> {sum(1 for item in results if item.type == "playlist")}</p>
        <p><strong>Live Content:</strong> {sum(1 for item in results if item.is_live)}</p>
    </div>
    
    <div class="results">
"""

    # Add each result item
    for i, item in enumerate(results, 1):
        # Determine YouTube URL based on type
        if item.type == "video":
            url = f"https://www.youtube.com/watch?v={item.id}"
        elif item.type == "channel":
            url = f"https://www.youtube.com/channel/{item.id}"
        elif item.type == "playlist":
            url = f"https://www.youtube.com/playlist?list={item.id}"
        else:
            url = f"https://www.youtube.com/watch?v={item.id}"

        live_badge = '<span class="badge">🔴 LIVE</span>' if item.is_live else ""

        html_content += f"""
        <div class="item type-{item.type}">
            <div class="title">
                <a href="{url}" target="_blank">{i}. {item.title}</a>
                {live_badge}
            </div>
            <div class="channel">📺 {item.channel_title or 'Unknown Channel'}</div>
            <div class="meta">
                🏷️ Type: {item.type.capitalize()} | 
                🆔 ID: {item.id} | 
                ⏱️ Duration: {item.length or 'Unknown'}
                {f' | 📹 Videos: {item.video_count}' if item.video_count else ''}
            </div>
        </div>
"""

    html_content += """
    </div>
    
    <div style="text-align: center; margin-top: 40px; color: #606060;">
        <p>Generated by PyTubeSearch | <a href="https://malith.dev">malith.dev</a></p>
    </div>
</body>
</html>
"""

    # Write to file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"   ✅ Exported {len(results)} items to {filename}")
    return filename


def export_to_text(results, filename="search_results.txt", query=""):
    """Export search results to plain text format."""
    print(f"📝 Exporting to Text: {filename}")

    with open(filename, "w", encoding="utf-8") as f:
        # Header
        f.write("=" * 60 + "\n")
        f.write("📺 YOUTUBE SEARCH RESULTS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Query: {query}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Results: {len(results)}\n")
        f.write("=" * 60 + "\n\n")

        # Statistics
        videos = sum(1 for item in results if item.type == "video")
        channels = sum(1 for item in results if item.type == "channel")
        playlists = sum(1 for item in results if item.type == "playlist")
        live_content = sum(1 for item in results if item.is_live)

        f.write("📊 STATISTICS:\n")
        f.write(f"   Videos: {videos}\n")
        f.write(f"   Channels: {channels}\n")
        f.write(f"   Playlists: {playlists}\n")
        f.write(f"   Live Content: {live_content}\n")
        f.write("\n" + "-" * 60 + "\n\n")

        # Results
        f.write("🔍 SEARCH RESULTS:\n\n")

        for i, item in enumerate(results, 1):
            emoji = {"video": "📹", "channel": "📺", "playlist": "📋"}.get(item.type, "📄")

            f.write(f"{i}. {emoji} {item.title}\n")
            f.write(f"   Type: {item.type.upper()}\n")
            f.write(f"   ID: {item.id}\n")

            if item.channel_title:
                f.write(f"   Channel: {item.channel_title}\n")

            if item.length:
                f.write(f"   Duration: {item.length}\n")

            if item.is_live:
                f.write("   🔴 LIVE CONTENT\n")

            if item.video_count:
                f.write(f"   Videos in playlist: {item.video_count}\n")

            # YouTube URL
            if item.type == "video":
                f.write(f"   URL: https://www.youtube.com/watch?v={item.id}\n")
            elif item.type == "channel":
                f.write(f"   URL: https://www.youtube.com/channel/{item.id}\n")
            elif item.type == "playlist":
                f.write(f"   URL: https://www.youtube.com/playlist?list={item.id}\n")

            f.write("\n" + "-" * 40 + "\n\n")

        # Footer
        f.write("=" * 60 + "\n")
        f.write("Generated by PyTubeSearch\n")
        f.write("https://github.com/Malith-Rukshan/PyTubeSearch\n")
        f.write("=" * 60 + "\n")

    print(f"   ✅ Exported {len(results)} items to {filename}")
    return filename


def export_detailed_analysis(results, filename="analysis_report.txt", query=""):
    """Export detailed analysis report."""
    print(f"📈 Exporting detailed analysis: {filename}")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("📊 DETAILED ANALYSIS REPORT\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"Query: {query}\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Results Analyzed: {len(results)}\n\n")

        # Content type analysis
        content_types = {}
        for item in results:
            content_types[item.type] = content_types.get(item.type, 0) + 1

        f.write("📋 CONTENT TYPE DISTRIBUTION:\n")
        for content_type, count in sorted(content_types.items()):
            percentage = (count / len(results)) * 100
            f.write(f"   {content_type.capitalize()}s: {count} ({percentage:.1f}%)\n")
        f.write("\n")

        # Channel analysis
        channels = {}
        for item in results:
            if item.channel_title:
                channels[item.channel_title] = channels.get(item.channel_title, 0) + 1

        if channels:
            f.write("📺 TOP CHANNELS:\n")
            top_channels = sorted(channels.items(), key=lambda x: x[1], reverse=True)[:10]
            for channel, count in top_channels:
                f.write(f"   {channel}: {count} items\n")
            f.write("\n")

        # Live content analysis
        live_items = [item for item in results if item.is_live]
        f.write(f"🔴 LIVE CONTENT ANALYSIS:\n")
        f.write(f"   Live items: {len(live_items)} ({len(live_items)/len(results)*100:.1f}%)\n")

        if live_items:
            f.write("   Live content titles:\n")
            for item in live_items[:5]:  # Show first 5
                f.write(f"      • {item.title}\n")
        f.write("\n")

        # Title analysis
        all_words = []
        for item in results:
            all_words.extend(item.title.lower().split())

        word_count = {}
        for word in all_words:
            if len(word) > 3:  # Only meaningful words
                word_count[word] = word_count.get(word, 0) + 1

        if word_count:
            f.write("🏷️ MOST COMMON WORDS IN TITLES:\n")
            top_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:15]
            for word, count in top_words:
                f.write(f"   {word}: {count} occurrences\n")
        f.write("\n")

        # Duration analysis (for videos with duration info)
        videos_with_duration = [item for item in results if item.type == "video" and item.length]
        if videos_with_duration:
            f.write("⏱️ DURATION ANALYSIS:\n")
            f.write(
                f"   Videos with duration info: {len(videos_with_duration)}/{sum(1 for item in results if item.type == 'video')}\n"
            )

            # Simple duration categorization
            short_videos = []
            medium_videos = []
            long_videos = []

            for video in videos_with_duration:
                duration_str = str(video.length).lower()
                if any(x in duration_str for x in ["0:", "1:", "2:", "3:", "4:"]):
                    short_videos.append(video)
                elif any(x in duration_str for x in ["5:", "6:", "7:", "8:", "9:", "10:"]):
                    medium_videos.append(video)
                else:
                    long_videos.append(video)

            f.write(f"   Short videos (≤4 min): {len(short_videos)}\n")
            f.write(f"   Medium videos (5-10 min): {len(medium_videos)}\n")
            f.write(f"   Long videos (>10 min): {len(long_videos)}\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write("Report generated by PyTubeSearch\n")

    print(f"   ✅ Analysis report exported to {filename}")
    return filename


def multi_format_export(query, results, base_filename="youtube_search"):
    """Export results to multiple formats."""
    print(f"📦 Multi-format export for query: {query}")
    print("-" * 50)

    # Create output directory
    output_dir = Path("exports")
    output_dir.mkdir(exist_ok=True)

    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    exported_files = []

    # Export to all formats
    formats = [
        ("json", export_to_json),
        ("csv", export_to_csv),
        ("html", export_to_html),
        ("txt", export_to_text),
    ]

    for format_name, export_func in formats:
        try:
            filename = output_dir / f"{base_filename}_{timestamp}.{format_name}"

            if format_name in ["html", "txt"]:
                # These functions need the query parameter
                export_func(results, filename, query)
            else:
                export_func(results, filename)

            exported_files.append(filename)

        except Exception as e:
            print(f"   ❌ Failed to export {format_name}: {e}")

    # Export detailed analysis
    try:
        analysis_filename = output_dir / f"{base_filename}_analysis_{timestamp}.txt"
        export_detailed_analysis(results, analysis_filename, query)
        exported_files.append(analysis_filename)
    except Exception as e:
        print(f"   ❌ Failed to export analysis: {e}")

    # Summary
    print(f"\n📊 EXPORT SUMMARY:")
    print(f"   Total files exported: {len(exported_files)}")
    print(f"   Export directory: {output_dir.absolute()}")
    print("   Exported files:")
    for filename in exported_files:
        file_size = filename.stat().st_size if filename.exists() else 0
        print(f"      📄 {filename.name} ({file_size:,} bytes)")

    return exported_files


def main():
    """Main function to run data export examples."""
    parser = argparse.ArgumentParser(description="PyTubeSearch Data Export Examples")
    parser.add_argument("query", nargs="?", default="python programming", help="Search query")
    parser.add_argument(
        "--format",
        choices=["json", "csv", "html", "txt", "all"],
        default="all",
        help="Export format",
    )
    parser.add_argument("--limit", type=int, default=10, help="Number of results to fetch")

    args = parser.parse_args()

    print("📊 PyTubeSearch - Data Export Examples")
    print("=" * 60)

    # Fetch search results
    print(f"🔍 Searching for: {args.query}")
    with PyTubeSearch() as client:
        try:
            results = client.search(args.query, limit=args.limit)
            print(f"   ✅ Found {len(results.items)} results")
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
            return

    if not results.items:
        print("No results to export")
        return

    print("\n" + "-" * 60 + "\n")

    # Export based on format selection
    if args.format == "all":
        exported_files = multi_format_export(args.query, results.items)
    else:
        # Single format export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"search_results_{timestamp}.{args.format}"

        export_functions = {
            "json": export_to_json,
            "csv": export_to_csv,
            "html": lambda r, f: export_to_html(r, f, args.query),
            "txt": lambda r, f: export_to_text(r, f, args.query),
        }

        try:
            export_functions[args.format](results.items, filename)
            print(f"\n✅ Export completed: {filename}")
        except Exception as e:
            print(f"\n❌ Export failed: {e}")

    print("\n💡 Next steps:")
    print("   - Open HTML files in your web browser for visual viewing")
    print("   - Import CSV files into Excel or Google Sheets for analysis")
    print("   - Use JSON files for programmatic data processing")
    print("   - Share text files for simple reports")


if __name__ == "__main__":
    main()
