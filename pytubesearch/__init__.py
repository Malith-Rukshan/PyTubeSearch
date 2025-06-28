"""PyTubeSearch - A Python package for searching YouTube by keywords."""

from .client import DataExtractionError, PyTubeSearch, PyTubeSearchError
from .models import (
    ChannelResult,
    PlaylistResult,
    SearchItem,
    SearchOptions,
    SearchResult,
    ShortVideo,
    VideoDetails,
)

__version__ = "1.0.0"
__author__ = "Malith Rukshan"
__email__ = "hello@malith.dev"

__all__ = [
    "PyTubeSearch",
    "PyTubeSearchError",
    "DataExtractionError",
    "SearchResult",
    "SearchItem",
    "PlaylistResult",
    "ChannelResult",
    "VideoDetails",
    "ShortVideo",
    "SearchOptions",
]
