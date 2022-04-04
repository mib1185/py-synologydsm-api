from typing import List

from .song import Song


class Playlist:
    def __init__(self, data):
        """Initialize Player object"""
        self._data = data
        self._songs = list(map(Song, data["songs"]))

    @property
    def current(self) -> int:
        """Return current playing song index"""
        return self._data["current"]

    @property
    def mode(self) -> str:
        """Return current play mode"""
        return self._data["mode"]

    @property
    def shuffle(self) -> bool:
        """Return current shuffle mode"""
        return self._data["shuffle"]

    @property
    def songs(self) -> List[Song]:
        """Return list of songs in playlist"""
        return self._songs

    @property
    def timestamp(self) -> int:
        """Return timestamp of update"""
        return self._data["timestamp"]

    @property
    def total(self) -> int:
        """Return total size of playlist"""
        return self._data["total"]
