"""Main PyTubeSearch client implementation."""

import json
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import httpx

from .models import (
    ChannelResult,
    NextPageData,
    PlaylistResult,
    SearchItem,
    SearchOptions,
    SearchResult,
    ShortVideo,
    VideoDetails,
    YoutubeInitData,
    YoutubePlayerDetail,
)


class PyTubeSearchError(Exception):
    """Base exception for PyTubeSearch."""

    pass


class DataExtractionError(PyTubeSearchError):
    """Raised when data extraction from YouTube fails."""

    pass


class PyTubeSearch:
    """Main client for searching YouTube content."""

    YOUTUBE_ENDPOINT = "https://www.youtube.com"

    def __init__(self, timeout: float = 30.0):
        """Initialize the PyTubeSearch client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def __enter__(self) -> "PyTubeSearch":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.client.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    async def __aenter__(self) -> "PyTubeSearch":
        self.client = httpx.AsyncClient(timeout=self.timeout)  # type: ignore
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if hasattr(self.client, "aclose"):
            await self.client.aclose()

    def _get_youtube_init_data(self, url: str) -> YoutubeInitData:
        """Extract YouTube initialization data from page."""
        try:
            response = self.client.get(url)
            response.raise_for_status()
            page_content = response.text

            # Extract ytInitialData
            init_data_match = re.search(r"var ytInitialData = ({.+?});", page_content)
            if not init_data_match:
                raise DataExtractionError("Cannot extract YouTube initialization data")

            initdata = json.loads(init_data_match.group(1))

            # Extract API token
            api_token = None
            api_token_match = re.search(r'"innertubeApiKey":"([^"]+)"', page_content)
            if api_token_match:
                api_token = api_token_match.group(1)

            # Extract context
            context = None
            context_match = re.search(
                r'"INNERTUBE_CONTEXT":({.+?}),"INNERTUBE_CONTEXT_CLIENT_NAME"', page_content
            )
            if context_match:
                context = json.loads(context_match.group(1))

            return YoutubeInitData(initdata=initdata, apiToken=api_token, context=context)

        except (httpx.RequestError, json.JSONDecodeError) as e:
            raise DataExtractionError(f"Failed to get YouTube init data: {e}")

    def _get_youtube_player_detail(self, url: str) -> YoutubePlayerDetail:
        """Extract YouTube player details from page."""
        try:
            response = self.client.get(url)
            response.raise_for_status()
            page_content = response.text

            # Extract video ID from URL
            video_id = ""
            video_id_match = re.search(r"[?&]v=([^&]+)", url)
            if video_id_match:
                video_id = video_id_match.group(1)

            # Extract ytInitialPlayerResponse - try multiple patterns
            player_data = None
            patterns = [
                r"var ytInitialPlayerResponse = ({.+?});",
                r"\"ytInitialPlayerResponse\":\s*({.+?}),",
                r"ytInitialPlayerResponse\s*=\s*({.+?});",
                r"window\[\"ytInitialPlayerResponse\"\]\s*=\s*({.+?});",
            ]

            for pattern in patterns:
                player_match = re.search(pattern, page_content)
                if player_match:
                    try:
                        player_data = json.loads(player_match.group(1))
                        break
                    except json.JSONDecodeError:
                        continue

            if not player_data:
                raise DataExtractionError("Cannot extract YouTube player data")

            video_details = player_data.get("videoDetails", {})

            # If videoDetails is not available, try microformat
            if not video_details and "microformat" in player_data:
                microformat = player_data["microformat"]
                if isinstance(microformat, dict) and "playerMicroformatRenderer" in microformat:
                    pmr = microformat["playerMicroformatRenderer"]
                    video_details = {
                        "videoId": pmr.get("videoId", video_id),
                        "author": pmr.get("ownerChannelName", ""),
                        "channelId": pmr.get("externalChannelId", ""),
                        "shortDescription": pmr.get("description", {}).get("simpleText", ""),
                        "keywords": pmr.get("keywords", []),
                        "thumbnail": (
                            pmr.get("thumbnail", {}).get("thumbnails", [{}])[0]
                            if pmr.get("thumbnail", {}).get("thumbnails")
                            else None
                        ),
                    }

            return YoutubePlayerDetail(
                videoId=video_details.get("videoId", video_id),
                thumbnail=video_details.get("thumbnail"),
                author=video_details.get("author"),
                channelId=video_details.get("channelId", ""),
                shortDescription=video_details.get("shortDescription", ""),
                keywords=video_details.get("keywords", []),
            )

        except (httpx.RequestError, json.JSONDecodeError) as e:
            raise DataExtractionError(f"Failed to get YouTube player detail: {e}")

    def _render_video_item(self, item_data: Dict[str, Any]) -> SearchItem:
        """Render video item from YouTube data."""
        video_renderer = item_data.get("videoRenderer") or item_data.get("playlistVideoRenderer")
        if not video_renderer:
            return SearchItem(
                id="",
                type="",
                title="",
                thumbnail=None,
                channelTitle=None,
                shortBylineText=None,
                length=None,
                isLive=False,
                videos=None,
                videoCount=None,
            )

        # Check if live
        is_live = False
        badges = video_renderer.get("badges", [])
        if badges:  # Check if badges is not None
            for badge in badges:
                if badge:  # Check if badge is not None
                    metadata_badge = badge.get("metadataBadgeRenderer", {})
                    if (
                        metadata_badge
                        and metadata_badge.get("style") == "BADGE_STYLE_TYPE_LIVE_NOW"
                    ):
                        is_live = True
                        break

        thumbnail_overlays = video_renderer.get("thumbnailOverlays", [])
        for overlay in thumbnail_overlays:
            time_status = overlay.get("thumbnailOverlayTimeStatusRenderer", {})
            if time_status.get("style") == "LIVE":
                is_live = True
                break

        # Extract data with type conversion and null checks
        video_id = str(video_renderer.get("videoId", ""))
        thumbnail = video_renderer.get("thumbnail")
        title = ""
        title_data = video_renderer.get("title", {})
        if isinstance(title_data, dict):
            if "runs" in title_data and title_data["runs"]:
                # Handle multiple runs by concatenating them
                title_parts = []
                for run in title_data["runs"]:
                    if run and "text" in run:
                        title_parts.append(str(run["text"]))
                title = "".join(title_parts)
            elif "simpleText" in title_data:
                title = str(title_data["simpleText"])
        else:
            title = str(title_data) if title_data else ""

        channel_title = ""
        owner_text = video_renderer.get("ownerText")
        if (
            owner_text
            and isinstance(owner_text, dict)
            and "runs" in owner_text
            and owner_text["runs"]
        ):
            channel_title = str(owner_text["runs"][0].get("text", ""))
        elif owner_text:
            channel_title = str(owner_text)

        short_byline_text = ""
        short_byline_data = video_renderer.get("shortBylineText", {})
        if (
            isinstance(short_byline_data, dict)
            and "runs" in short_byline_data
            and short_byline_data["runs"]
        ):
            short_byline_text = str(short_byline_data["runs"][0].get("text", ""))
        elif short_byline_data:
            short_byline_text = str(short_byline_data)

        length_text = ""
        length_data = video_renderer.get("lengthText", "")
        if length_data:
            length_text = str(length_data)

        return SearchItem(
            id=video_id,
            type="video",
            thumbnail=thumbnail,
            title=title,
            channelTitle=channel_title,
            shortBylineText=short_byline_text,
            length=length_text,
            isLive=is_live,
            videos=None,
            videoCount=None,
        )

    def _render_compact_video(self, item_data: Dict[str, Any]) -> SearchItem:
        """Render compact video item from YouTube data."""
        compact_renderer = item_data.get("compactVideoRenderer", {})

        # Check if live
        is_live = False
        badges = compact_renderer.get("badges", [])
        for badge in badges:
            metadata_badge = badge.get("metadataBadgeRenderer", {})
            if metadata_badge.get("style") == "BADGE_STYLE_TYPE_LIVE_NOW":
                is_live = True
                break

        title = compact_renderer.get("title", {}).get("simpleText", "")
        channel_title = ""
        short_byline = compact_renderer.get("shortBylineText", {})
        if "runs" in short_byline and short_byline["runs"]:
            channel_title = short_byline["runs"][0].get("text", "")

        return SearchItem(
            id=compact_renderer.get("videoId", ""),
            type="video",
            thumbnail=compact_renderer.get("thumbnail", {}).get("thumbnails"),
            title=title,
            channelTitle=channel_title,
            shortBylineText=channel_title,
            length=compact_renderer.get("lengthText"),
            isLive=is_live,
            videos=None,
            videoCount=None,
        )

    def search(
        self,
        keyword: str,
        with_playlist: bool = False,
        limit: int = 0,
        options: Optional[List[SearchOptions]] = None,
    ) -> SearchResult:
        """Search YouTube by keyword.

        Args:
            keyword: Search keyword
            with_playlist: Include playlists in results
            limit: Maximum number of results (0 for all)
            options: Search options for filtering

        Returns:
            SearchResult containing items and pagination data
        """
        endpoint = f"{self.YOUTUBE_ENDPOINT}/results?search_query={quote_plus(keyword)}"

        # Apply search filters
        if options:
            for option in options:
                if option.type.lower() == "video":
                    endpoint += "&sp=EgIQAQ%3D%3D"
                elif option.type.lower() == "channel":
                    endpoint += "&sp=EgIQAg%3D%3D"
                elif option.type.lower() == "playlist":
                    endpoint += "&sp=EgIQAw%3D%3D"
                elif option.type.lower() == "movie":
                    endpoint += "&sp=EgIQBA%3D%3D"
                break

        try:
            page_data = self._get_youtube_init_data(endpoint)

            # Navigate to search results
            contents = page_data.initdata.get("contents", {})
            two_column = contents.get("twoColumnSearchResultsRenderer", {})
            primary_contents = two_column.get("primaryContents", {})
            section_list = primary_contents.get("sectionListRenderer", {})

            items = []
            continuation_token = None

            for content in section_list.get("contents", []):
                if "continuationItemRenderer" in content:
                    continuation_data = content["continuationItemRenderer"]
                    continuation_endpoint = continuation_data.get("continuationEndpoint", {})
                    continuation_command = continuation_endpoint.get("continuationCommand", {})
                    continuation_token = continuation_command.get("token")

                elif "itemSectionRenderer" in content:
                    item_section = content["itemSectionRenderer"]
                    for item in item_section.get("contents", []):
                        if "channelRenderer" in item:
                            channel_renderer = item["channelRenderer"]
                            items.append(
                                SearchItem(
                                    id=channel_renderer.get("channelId", ""),
                                    type="channel",
                                    thumbnail=channel_renderer.get("thumbnail"),
                                    title=channel_renderer.get("title", {}).get("simpleText", ""),
                                    channelTitle=None,
                                    shortBylineText=None,
                                    length=None,
                                    isLive=False,
                                    videos=None,
                                    videoCount=None,
                                )
                            )

                        elif "videoRenderer" in item:
                            items.append(self._render_video_item(item))

                        elif with_playlist and "playlistRenderer" in item:
                            playlist_renderer = item["playlistRenderer"]
                            items.append(
                                SearchItem(
                                    id=playlist_renderer.get("playlistId", ""),
                                    type="playlist",
                                    thumbnail=playlist_renderer.get("thumbnails"),
                                    title=playlist_renderer.get("title", {}).get("simpleText", ""),
                                    channelTitle=None,
                                    shortBylineText=None,
                                    length=playlist_renderer.get("videoCount"),
                                    isLive=False,
                                    videos=playlist_renderer.get("videos"),
                                    videoCount=playlist_renderer.get("videoCount"),
                                )
                            )

            # Apply limit
            if limit > 0:
                items = items[:limit]

            next_page_context = {"context": page_data.context, "continuation": continuation_token}

            next_page = NextPageData(
                nextPageToken=page_data.api_token, nextPageContext=next_page_context
            )

            return SearchResult(items=items, nextPage=next_page)

        except Exception as e:
            raise PyTubeSearchError(f"Search failed: {e}")

    def next_page(
        self, next_page_data: NextPageData, with_playlist: bool = False, limit: int = 0
    ) -> SearchResult:
        """Get next page of search results.

        Args:
            next_page_data: Next page data from previous search
            with_playlist: Include playlists in results
            limit: Maximum number of results

        Returns:
            SearchResult with next page items
        """
        if not next_page_data.next_page_token:
            raise PyTubeSearchError("No next page token available")

        endpoint = (
            f"{self.YOUTUBE_ENDPOINT}/youtubei/v1/search?key={next_page_data.next_page_token}"
        )

        try:
            response = self.client.post(endpoint, json=next_page_data.next_page_context)
            response.raise_for_status()
            data = response.json()

            items = []

            commands = data.get("onResponseReceivedCommands", [])
            if commands:
                append_action = commands[0].get("appendContinuationItemsAction", {})
                continuation_items = append_action.get("continuationItems", [])

                for item in continuation_items:
                    if "itemSectionRenderer" in item:
                        section_contents = item["itemSectionRenderer"].get("contents", [])
                        for content in section_contents:
                            if "videoRenderer" in content:
                                items.append(self._render_video_item(content))
                            elif with_playlist and "playlistRenderer" in content:
                                playlist_renderer = content["playlistRenderer"]
                                # Get playlist data if needed
                                playlist_items = []
                                if playlist_renderer.get("playlistId"):
                                    try:
                                        playlist_result = self.get_playlist_data(
                                            playlist_renderer["playlistId"]
                                        )
                                        playlist_items = playlist_result.items
                                    except Exception:
                                        pass

                                items.append(
                                    SearchItem(
                                        id=playlist_renderer.get("playlistId", ""),
                                        type="playlist",
                                        thumbnail=playlist_renderer.get("thumbnails"),
                                        title=playlist_renderer.get("title", {}).get(
                                            "simpleText", ""
                                        ),
                                        channelTitle=None,
                                        shortBylineText=None,
                                        length=playlist_renderer.get("videoCount"),
                                        isLive=False,
                                        videos=playlist_items,
                                        videoCount=playlist_renderer.get("videoCount"),
                                    )
                                )

                    elif "continuationItemRenderer" in item:
                        continuation_data = item["continuationItemRenderer"]
                        continuation_endpoint = continuation_data.get("continuationEndpoint", {})
                        continuation_command = continuation_endpoint.get("continuationCommand", {})
                        if next_page_data.next_page_context:
                            next_page_data.next_page_context["continuation"] = (
                                continuation_command.get("token")
                            )

            # Apply limit
            if limit > 0:
                items = items[:limit]

            # Create a new NextPageData instance for the return
            return_next_page = NextPageData(
                nextPageToken=next_page_data.next_page_token,
                nextPageContext=next_page_data.next_page_context,
            )
            return SearchResult(items=items, nextPage=return_next_page)

        except Exception as e:
            raise PyTubeSearchError(f"Next page request failed: {e}")

    def get_playlist_data(self, playlist_id: str, limit: int = 0) -> PlaylistResult:
        """Get playlist data by ID.

        Args:
            playlist_id: YouTube playlist ID
            limit: Maximum number of items

        Returns:
            PlaylistResult with playlist items and metadata
        """
        endpoint = f"{self.YOUTUBE_ENDPOINT}/playlist?list={playlist_id}"

        try:
            init_data = self._get_youtube_init_data(endpoint)
            section_list = init_data.initdata
            metadata = section_list.get("metadata")

            contents = section_list.get("contents", {})
            two_column = contents.get("twoColumnBrowseResultsRenderer", {})
            tabs = two_column.get("tabs", [])

            items = []

            if tabs:
                tab_content = tabs[0].get("tabRenderer", {}).get("content", {})
                section_list_renderer = tab_content.get("sectionListRenderer", {})
                section_contents = section_list_renderer.get("contents", [])

                if section_contents:
                    item_section = section_contents[0].get("itemSectionRenderer", {})
                    playlist_content = item_section.get("contents", [])

                    if playlist_content:
                        playlist_renderer = playlist_content[0].get("playlistVideoListRenderer", {})
                        video_items = playlist_renderer.get("contents", [])

                        for item in video_items:
                            if "playlistVideoRenderer" in item:
                                items.append(self._render_video_item(item))

            # Apply limit
            if limit > 0:
                items = items[:limit]

            return PlaylistResult(items=items, metadata=metadata)

        except Exception as e:
            raise PyTubeSearchError(f"Failed to get playlist data: {e}")

    def get_video_details(self, video_id: str) -> VideoDetails:
        """Get detailed video information.

        Args:
            video_id: YouTube video ID

        Returns:
            VideoDetails with comprehensive video information
        """
        endpoint = f"{self.YOUTUBE_ENDPOINT}/watch?v={video_id}"

        try:
            page_data = self._get_youtube_init_data(endpoint)
            player_data = self._get_youtube_player_detail(endpoint)

            contents = page_data.initdata.get("contents", {})
            two_column = contents.get("twoColumnWatchNextResults", {})
            results = two_column.get("results", {}).get("results", {})
            result_contents = results.get("contents", [])

            title = ""
            is_live = False
            channel = ""

            if len(result_contents) > 0:
                primary_info = result_contents[0].get("videoPrimaryInfoRenderer", {})
                title_data = primary_info.get("title", {})
                if "runs" in title_data and title_data["runs"]:
                    title = title_data["runs"][0].get("text", "")

                view_count = primary_info.get("viewCount", {})
                video_view_count = view_count.get("videoViewCountRenderer", {})
                is_live = video_view_count.get("isLive", False)

            if len(result_contents) > 1:
                secondary_info = result_contents[1].get("videoSecondaryInfoRenderer", {})
                owner = secondary_info.get("owner", {}).get("videoOwnerRenderer", {})
                owner_title = owner.get("title", {})
                if "runs" in owner_title and owner_title["runs"]:
                    channel = owner_title["runs"][0].get("text", "")

            # Get suggestions
            suggestions = []
            secondary_results = two_column.get("secondaryResults", {}).get("secondaryResults", {})
            suggestion_results = secondary_results.get("results", [])

            for suggestion in suggestion_results:
                if "compactVideoRenderer" in suggestion:
                    suggestions.append(self._render_compact_video(suggestion))

            return VideoDetails(
                id=player_data.video_id,
                title=title or "",
                thumbnail=player_data.thumbnail,
                isLive=is_live,
                channel=player_data.author or channel,
                channelId=player_data.channel_id,
                description=player_data.short_description,
                keywords=player_data.keywords,
                suggestion=suggestions,
            )

        except Exception as e:
            raise PyTubeSearchError(f"Failed to get video details: {e}")

    def get_channel_by_id(self, channel_id: str) -> List[ChannelResult]:
        """Get channel information by ID.

        Args:
            channel_id: YouTube channel ID

        Returns:
            List of ChannelResult with channel tabs
        """
        endpoint = f"{self.YOUTUBE_ENDPOINT}/channel/{channel_id}"

        try:
            page_data = self._get_youtube_init_data(endpoint)

            contents = page_data.initdata.get("contents", {})
            two_column = contents.get("twoColumnBrowseResultsRenderer", {})
            tabs = two_column.get("tabs", [])

            results = []
            for tab in tabs:
                tab_renderer = tab.get("tabRenderer")
                if tab_renderer:
                    title = tab_renderer.get("title", "")
                    content = tab_renderer.get("content")
                    results.append(ChannelResult(title=title, content=content))

            return results

        except Exception as e:
            raise PyTubeSearchError(f"Failed to get channel data: {e}")

    def get_suggestions(self, limit: int = 0) -> List[SearchItem]:
        """Get YouTube homepage suggestions.

        Args:
            limit: Maximum number of suggestions

        Returns:
            List of suggested videos
        """
        try:
            page_data = self._get_youtube_init_data(self.YOUTUBE_ENDPOINT)

            contents = page_data.initdata.get("contents", {})
            two_column = contents.get("twoColumnBrowseResultsRenderer", {})
            tabs = two_column.get("tabs", [])

            items = []

            if tabs:
                tab_content = tabs[0].get("tabRenderer", {}).get("content", {})
                rich_grid = tab_content.get("richGridRenderer", {})
                grid_contents = rich_grid.get("contents", [])

                for item in grid_contents:
                    rich_item = item.get("richItemRenderer")
                    if rich_item and rich_item.get("content"):
                        video_renderer = rich_item["content"].get("videoRenderer")
                        if video_renderer and video_renderer.get("videoId"):
                            items.append(self._render_video_item(rich_item["content"]))

            # Apply limit
            if limit > 0:
                items = items[:limit]

            return items

        except Exception as e:
            raise PyTubeSearchError(f"Failed to get suggestions: {e}")

    def get_short_videos(self) -> List[ShortVideo]:
        """Get YouTube Shorts videos.

        Returns:
            List of ShortVideo items
        """
        try:
            page_data = self._get_youtube_init_data(self.YOUTUBE_ENDPOINT)

            contents = page_data.initdata.get("contents", {})
            two_column = contents.get("twoColumnBrowseResultsRenderer", {})
            tabs = two_column.get("tabs", [])

            short_videos = []

            if tabs:
                tab_content = tabs[0].get("tabRenderer", {}).get("content", {})
                rich_grid = tab_content.get("richGridRenderer", {})
                grid_contents = rich_grid.get("contents", [])

                # Find Shorts section
                for item in grid_contents:
                    rich_section = item.get("richSectionRenderer")
                    if rich_section:
                        section_content = rich_section.get("content", {})
                        rich_shelf = section_content.get("richShelfRenderer", {})

                        title_data = rich_shelf.get("title", {})
                        if "runs" in title_data and title_data["runs"]:
                            section_title = title_data["runs"][0].get("text", "")
                            if "Shorts" in section_title:
                                shelf_contents = rich_shelf.get("contents", [])

                                for shelf_item in shelf_contents:
                                    rich_item = shelf_item.get("richItemRenderer", {})
                                    reel_item = rich_item.get("content", {}).get(
                                        "reelItemRenderer", {}
                                    )

                                    if reel_item:
                                        thumbnail_data = reel_item.get("thumbnail", {})
                                        thumbnails = thumbnail_data.get("thumbnails", [])
                                        thumbnail = thumbnails[0] if thumbnails else None

                                        headline = reel_item.get("headline", {}).get(
                                            "simpleText", ""
                                        )

                                        short_videos.append(
                                            ShortVideo(
                                                id=reel_item.get("videoId", ""),
                                                type="reel",
                                                thumbnail=thumbnail,
                                                title=headline,
                                                inlinePlaybackEndpoint=reel_item.get(
                                                    "inlinePlaybackEndpoint", {}
                                                ),
                                            )
                                        )

            return short_videos

        except Exception as e:
            raise PyTubeSearchError(f"Failed to get short videos: {e}")
