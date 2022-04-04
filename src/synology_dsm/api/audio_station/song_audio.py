class SongAudio:
    def __init__(self, data):
        self._data = data

    @property
    def bitrate(self) -> int:
        """Return song bitrate"""
        return self._data["bitrate"]

    @property
    def channel(self) -> int:
        """Return song channel"""
        return self._data["channel"]

    @property
    def duration(self) -> int:
        """Return song duration"""
        return self._data["duration"]

    @property
    def filesize(self) -> int:
        """Return song filesize"""
        return self._data["filesize"]

    @property
    def frequency(self) -> int:
        """Return song frequency"""
        return self._data["frequency"]
