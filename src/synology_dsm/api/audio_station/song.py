from .song_additional_info import SongAdditional


class Song:
    def __init__(self, data):
        self._data = data
        self._additional = SongAdditional(data["additional"])

    @property
    def id(self) -> str:
        """Return song id"""
        return self._data["id"]

    @property
    def path(self) -> str:
        """Return song path"""
        return self._data["path"]

    @property
    def title(self) -> str:
        """Return song title"""
        return self._data["title"]

    @property
    def type(self) -> str:
        """Return song type"""
        return self._data["type"]

    @property
    def additional(self) -> SongAdditional:
        """Return song additional information"""
        return self._additional
