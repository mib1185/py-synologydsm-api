from .song import Song
from .play_mode import PlayMode
from .playlist_status import PlaylistStatus


class RemotePlayerStatus:
    """An representation of a Synology Remote player status."""

    def __init__(self, data):
        """Initialize a Synology Remote player status."""
        self._data = data
        self._play_mode = PlayMode(data["play_mode"])
        self._song = Song(data["song"])

    def update(self, data):
        """Update the player."""
        self._data = data

    @property
    def play_mode(self) -> PlayMode:
        """Return player playmode information"""
        return self._play_mode

    @property
    def playlist_timestamp(self) -> int:
        """Return title of the task."""
        return self._data["playlist_timestamp"]

    @property
    def playlist_total(self) -> int:
        """Return playlist size"""
        return self._data["playlist_total"]

    @property
    def position(self) -> int:
        """Return position in playlist"""
        return self._data["position"]

    @property
    def song(self) -> Song:
        """Return current song information"""
        return self._song

    @property
    def state(self) -> PlaylistStatus:
        """Return player state"""
        return self._data["state"]

    @property
    def stop_index(self) -> int:
        """Return stop_index"""
        return self._data["stop_index"]

    @property
    def subplayer_volume(self) -> int:
        """Return subplayer_volume"""
        return self._data["subplayer_volume"]

    @property
    def volume(self) -> int:
        """Return volume"""
        return self._data["volume"]
