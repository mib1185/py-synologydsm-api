from .repeat_mode import RepeatMode


class PlayMode:
    def __init__(self, data):
        """Initialize play mode object"""
        self._data = data

    @property
    def play_mode_repeat(self) -> RepeatMode:
        """Return current player repeat mode"""
        return self._data["repeat"]

    @property
    def play_mode_shuffle(self) -> bool:
        """Return current player shuffle mode"""
        return self._data["shuffle"]
