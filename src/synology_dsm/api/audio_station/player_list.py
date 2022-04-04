from typing import List

from .player import Player


class PlayerList:
    def __init__(self, data):
        """Initialize PlayerList object"""
        self._players = list(map(Player, data["players"]))

    @property
    def id(self) -> List[Player]:
        """Return player id"""
        return self._players
