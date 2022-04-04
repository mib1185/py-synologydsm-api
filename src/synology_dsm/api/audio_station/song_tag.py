class SongTag:
    def __init__(self, data):
        self._data = data

    @property
    def album(self) -> str:
        """Return song album"""
        return self._data["album"]

    @property
    def album_artist(self) -> str:
        """Return song album_artist"""
        return self._data["album_artist"]

    @property
    def artist(self) -> str:
        """Return song artist"""
        return self._data["artist"]

    @property
    def comment(self) -> str:
        """Return song comment"""
        return self._data["comment"]

    @property
    def composer(self) -> str:
        """Return song composer"""
        return self._data["composer"]

    @property
    def disc(self) -> int:
        """Return song disc"""
        return self._data["disc"]

    @property
    def genre(self) -> str:
        """Return song genre"""
        return self._data["genre"]

    @property
    def track(self) -> int:
        """Return song track"""
        return self._data["track"]

    @property
    def year(self) -> int:
        """Return song year"""
        return self._data["year"]