"""Data models for Synology VideoStation Module."""
from dataclasses import dataclass

@dataclass
class SynoVideoStationMovie:
    """Representation of an Synology VideoStation Movies."""

    movie_id: str
    title: str
    summary: str
    poster: str

@dataclass
class SynoVideoStationMoviePoster:
    """Representation of an Synology VideoStation Movies."""

    movie_id: int
    movie_type: str