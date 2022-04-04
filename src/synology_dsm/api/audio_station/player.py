class Player:
    def __init__(self, data):
        """Initialize Player object"""
        self._data = data

    @property
    def id(self) -> str:
        """Return player id"""
        return self._data["id"]

    @property
    def is_multiple(self) -> bool:
        """Return player is_multiple info"""
        return self._data["is_multiple"]

    @property
    def name(self) -> str:
        """Return player name"""
        return self._data["name"]

    @property
    def password_protected(self) -> bool:
        """Return if player is password protected"""
        return self._data["password_protected"]

    @property
    def support_seek(self) -> bool:
        """Return if player supports seeking"""
        return self._data["support_seek"]

    @property
    def support_set_volume(self) -> bool:
        """Return if player supports volume setting"""
        return self._data["support_set_volume"]

    @property
    def type(self) -> bool:
        """Return player type"""
        return self._data["type"]
