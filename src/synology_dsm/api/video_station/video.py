"""Data models for Synology VideoStation Module."""
from dataclasses import dataclass

@dataclass
class SynoVideoStationDevices:
    """Representation of an Synology VideoStation Devices."""

    device_id: int
    title: str
    now_playing: str
    password_protected: bool
    volume_adjustable: bool

@dataclass
class SynoVideoStationLibrary:
    """Representation of an Synology VideoStation Poster."""

    library_id: int
    library_type: str

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
class SynoVideoStationPoster:
    """Representation of an Synology VideoStation Movies."""

    poster_bytes: bytes

@dataclass
class SynoVideoStationTVShow:
    """Representation of an Synology VideoStation Movies."""

    tvshow_id: int
    title: str
    total_seasons: int
    summary: str

@dataclass
class SynoVideoStationTVShowPoster:
    """Representation of an Synology VideoStation Movies."""

    poster_bytes: bytes

@dataclass
class SynoVideoStationTVShowEpisode:
    """Representation of an Synology VideoStation Movies."""

    episode_id: int
    tvshow_id: int
    season: int
    episode: int
    title: str
    summary: str

