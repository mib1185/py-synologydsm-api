"""Data models for Synology VideoStation Module."""
from dataclasses import dataclass

@dataclass
class SynoVideoStationMovie:
    """Representation of an Synology VideoStation Movies."""

    movie_id: int
    title: str
    summary: str
    poster_url: str
    file_id: int
    file_name: str
    file_path: str
    file_video_codec: str
    file_audio_codec: str

@dataclass
class SynoVideoStationMoviePoster:
    """Representation of an Synology VideoStation Poster."""

    movie_id: int
    movie_type: str

@dataclass
class SynoVideoStationDevices:
    """Representation of an Synology VideoStation Devices."""

    device_id: int
    device_title: str
    device_now_playing: str
    device_password_protected: bool

@dataclass
class SynoVideoStationMetadataMovie:
    """Representation of an Synology VideoStation Metadata."""

    file_id: int
    certificate: str