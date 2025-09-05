"""Data models for Synology AudioStation Module."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RemotePlayerAction(Enum):
    """Representation of a Synology AudioStation remote player action."""

    play = "play"
    pause = "pause"
    stop = "stop"
    next = "next"
    prev = "prev"


class LibraryShareType(Enum):
    """Representation of a Synology AudioStation Music Library Share Type."""

    personal = "personal"
    shared = "shared"


class PlaylistStatus(Enum):
    """Representation of a Synology AudioStation Playlist current status."""

    transitioning = "transitioning"
    playing = "playing"
    stopped = "stopped"
    pause = "pause"


class QueueMode(Enum):
    """Internal Enum, indicates if songs should be added to queue or replace."""

    enqueue = "enqueue"
    replace = "replace"


class RepeatMode(Enum):
    """Representation of a Synology AudioStation Playlist repeat mode."""

    all = "all"
    none = "none"
    one = "one"


class ShuffleMode(Enum):
    """Representation of a Synology AudioStation Playlist shuffle mode."""

    auto = "auto"
    none = "none"


class SongSortMode(Enum):
    """Representation of a Synology AudioStation Playlist track sort mode."""

    track = "track"
    album = "album"
    name = "name"


@dataclass
class PlayMode:
    """Representation of a Synology AudioStation PlayMode."""

    repeat: RepeatMode
    shuffle: bool


@dataclass
class Player:
    """Representation of a Synology AudioStation Player."""

    id: str
    is_multiple: bool
    name: str
    password_protected: bool
    support_seek: bool
    support_set_volume: bool
    type: str


@dataclass
class Players:
    """Representation of a Synology AudioStation Players."""

    players: list[Player]


@dataclass
class AudioStationPrivilege:
    """Representation of a Synology AudioStation Privilege."""

    playlist_edit: bool
    remote_player: bool
    sharing: bool
    tag_edit: bool
    upnp_browse: bool


@dataclass
class AudioStationSettings:
    """Representation of a Synology AudioStation Settings."""

    audio_show_virtual_library: bool
    disable_upnp: bool
    enable_download: bool
    prefer_using_html5: bool
    transcode_to_mp3: bool


@dataclass
class AudioStationInfo:
    """Representation of a Synology AudioStation Info."""

    browse_personal_library: str
    dsd_decode_capability: bool
    enable_equalizer: bool
    enable_personal_library: bool
    enable_user_home: bool
    has_music_share: bool
    is_manager: bool
    playing_queue_max: int
    privilege: AudioStationPrivilege
    remote_controller: bool
    same_subnet: bool
    serial_number: str
    settings: AudioStationSettings
    sid: str
    support_bluetooth: bool
    support_usb: bool
    support_virtual_library: bool
    transcode_capability: list[str]
    version: int
    version_string: str


@dataclass
class SongTag:
    """Representation of a Synology AudioStation Song Tag."""

    album: str
    album_artist: str
    artist: str
    comment: str
    composer: str
    disc: int
    genre: str
    track: int
    year: int


@dataclass
class SongAudio:
    """Representation of a Synology AudioStation SongAudio."""

    bitrate: int
    channel: int
    duration: int
    filesize: int
    frequency: int


@dataclass
class SongAdditional:
    """Representation of a Synology AudioStation SongAdditional."""

    song_audio: SongAudio
    song_tag: SongTag


@dataclass
class Song:
    """Representation of a Synology AudioStation Song."""

    additional: SongAdditional
    id: str
    path: str
    title: str
    type: str


@dataclass
class Playlist:
    """Representation of a Synology AudioStation Playlist."""

    songs: list[Song]
    current: int
    mode: str
    shuffle: bool
    timestamp: int
    total: int


@dataclass
class RemotePlayerStatus:
    """Representation of a Synology AudioStation RemotePlayerStatus."""

    song: Optional[Song]
    play_mode: PlayMode
    playlist_timestamp: int
    playlist_total: int
    position: int
    state: PlaylistStatus
    stop_index: int
    subplayer_volume: Optional[int]
    volume: int
