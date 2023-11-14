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
    """Representation of an Synology VideoStation Poster."""

    movie_id: int
    movie_type: str

@dataclass
class SynoVideoStationDevices:
    """Representation of an Synology VideoStation Devices."""

    device_id: str
    device_now_playing: str
    password_protected: bool
    device_title: str

@dataclass
class SynoVideoStationMetadataMovie:
    """Representation of an Synology VideoStation Metadata."""

    file_id: int
    certificate: str