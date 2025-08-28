from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RemotePlayerAction(str, Enum):
    play = "play"
    pause = "pause"
    stop = "stop"
    next = "next"
    prev = "prev"


class LibraryShareType(str, Enum):
    personal = "personal"
    shared = "shared"


class PlaylistStatus(str, Enum):
    transitioning = "transitioning"
    playing = "playing"
    stopped = "stopped"
    pause = "pause"


class QueueMode(str, Enum):
    """Enum used by library, indicates if songs should be added to queue or replace"""
    enqueue = "enqueue"
    replace = "replace"


class RepeatMode(str, Enum):
    all = "all"
    none = "none"
    one = "one"


class ShuffleMode(str, Enum):
    auto = "auto"
    none = "none"


class SongSortMode(str, Enum):
    track = "track"
    album = "album"
    name = "name"


@dataclass(init=False)
class PlayMode:
    repeat: RepeatMode
    shuffle: bool

    def __init__(self, **kwargs):
        self.repeat = kwargs['repeat']
        self.shuffle = kwargs['shuffle']


@dataclass(init=False)
class Player:
    id: str
    is_multiple: bool
    name: str
    password_protected: bool
    support_seek: bool
    support_set_volume: bool
    type: bool

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.is_multiple = kwargs['is_multiple']
        self.name = kwargs['name']
        self.password_protected = kwargs['password_protected']
        self.support_seek = kwargs['support_seek']
        self.support_set_volume = kwargs['support_set_volume']
        self.type = kwargs['type']


@dataclass(init=False)
class AudioStationPrivilege:
    playlist_edit: bool
    remote_player: bool
    sharing: bool
    tag_edit: bool
    upnp_browse: bool

    def __init__(self, **kwargs):
        self.playlist_edit = kwargs['playlist_edit']
        self.remote_player = kwargs['remote_player']
        self.sharing = kwargs['sharing']
        self.tag_edit = kwargs['tag_edit']
        self.upnp_browse = kwargs['upnp_browse']


@dataclass(init=False)
class AudioStationSettings:
    audio_show_virtual_library: bool
    disable_upnp: bool
    enable_download: bool
    prefer_using_html5: bool
    transcode_to_mp3: bool

    def __init__(self, **kwargs):
        self.audio_show_virtual_library = kwargs['audio_show_virtual_library']
        self.disable_upnp = kwargs['disable_upnp']
        self.enable_download = kwargs['enable_download']
        self.prefer_using_html5 = kwargs['prefer_using_html5']
        self.transcode_to_mp3 = kwargs['transcode_to_mp3']


@dataclass(init=False)
class AudioStationInfo:
    browse_personal_library: bool
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

    def __init__(self, **kwargs):
        self.browse_personal_library = kwargs['browse_personal_library']
        self.dsd_decode_capability = kwargs['dsd_decode_capability']
        self.enable_equalizer = kwargs['enable_equalizer']
        self.enable_personal_library = kwargs['enable_personal_library']
        self.enable_user_home = kwargs['enable_user_home']
        self.has_music_share = kwargs['has_music_share']
        self.is_manager = kwargs['is_manager']
        self.playing_queue_max = kwargs['playing_queue_max']
        self.privilege = AudioStationPrivilege(**kwargs['privilege'])
        self.remote_controller = kwargs['remote_controller']
        self.same_subnet = kwargs['same_subnet']
        self.serial_number = kwargs['serial_number']
        self.settings = AudioStationSettings(**kwargs['settings'])
        self.sid = kwargs['sid']
        self.support_bluetooth = kwargs['support_bluetooth']
        self.support_usb = kwargs['support_usb']
        self.support_virtual_library = kwargs['support_virtual_library']
        self.transcode_capability = kwargs['transcode_capability']
        self.version = kwargs['version']
        self.version_string = kwargs['version_string']


@dataclass(init=False)
class SongTag:
    album: str
    album_artist: str
    artist: str
    comment: str
    composer: str
    disc: int
    genre: str
    track: int
    year: int

    def __init__(self, **kwargs):
        self.album = kwargs['album']
        self.album_artist = kwargs['album_artist']
        self.artist = kwargs['artist']
        self.comment = kwargs['comment']
        self.composer = kwargs['composer']
        self.disc = kwargs['disc']
        self.genre = kwargs['genre']
        self.track = kwargs['track']
        self.year = kwargs['year']


@dataclass(init=False)
class SongAudio:
    bitrate: int
    channel: int
    duration: int
    filesize: int
    frequency: int

    def __init__(self, **kwargs):
        self.bitrate = kwargs['bitrate']
        self.channel = kwargs['channel']
        self.duration = kwargs['duration']
        self.filesize = kwargs['filesize']
        self.frequency = kwargs['frequency']


@dataclass(init=False)
class SongAdditional:
    song_audio: SongAudio
    song_tag: SongTag

    def __init__(self, **kwargs):
        self.song_audio = SongAudio(**kwargs['song_audio'])
        self.song_tag = SongTag(**kwargs['song_tag'])


@dataclass(init=False)
class Song:
    additional: SongAdditional
    id: str
    path: str
    title: str
    type: str

    def __init__(self, **kwargs):
        self.additional = SongAdditional(**kwargs['additional'])
        self.id = kwargs['id']
        self.path = kwargs['path']
        self.title = kwargs['title']
        self.type = kwargs['type']


@dataclass(init=False)
class Playlist:
    songs: list[Song]
    current: int
    mode: str
    shuffle: bool
    timestamp: int
    total: int

    def __init__(self, **kwargs):
        self.songs = [Song(**s) for s in kwargs['songs']]
        self.current = kwargs['current']
        self.mode = kwargs['mode']
        self.shuffle = kwargs['shuffle']
        self.timestamp = kwargs['timestamp']
        self.total = kwargs['total']


@dataclass(init=False)
class RemotePlayerStatus:
    song: Song or None
    play_mode: PlayMode
    playlist_timestamp: int
    playlist_total: int
    position: int
    state: PlaylistStatus
    stop_index: int
    subplayer_volume: Optional[int]
    volume: int

    def __init__(self, **kwargs):
        if 'song' in kwargs and kwargs['song'] is not None:
            self.song = Song(**kwargs['song'])
        else:
            self.song = None
        self.play_mode = kwargs['play_mode']
        self.playlist_timestamp = kwargs['playlist_timestamp']
        self.playlist_total = kwargs['playlist_total']
        self.position = kwargs['position']
        self.state = kwargs['state']
        self.stop_index = kwargs['stop_index']
        self.subplayer_volume = kwargs['subplayer_volume']
        self.volume = kwargs['volume']
