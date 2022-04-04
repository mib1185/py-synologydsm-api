from .song_audio import SongAudio
from .song_tag import SongTag


class SongAdditional:
    def __init__(self, data):
        self._song_audio = SongAudio(data["song_audio"])
        self._song_tag = SongTag(data["song_tag"])

    @property
    def song_audio(self) -> SongAudio:
        """Return SongAudio information"""
        return self._song_audio

    @property
    def song_tag(self) -> SongTag:
        """Return SongTag information"""
        return self._song_tag
