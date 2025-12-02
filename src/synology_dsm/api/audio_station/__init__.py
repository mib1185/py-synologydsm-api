"""Synology AudioStation API wrapper."""

from typing import TYPE_CHECKING, List, Optional

from .. import SynoBaseApi
from .models import AudioStationInfo, Player
from .remote_player_info import RemotePlayerInfo
from .syno_audio_station_api import SynoAudioStationApi

if TYPE_CHECKING:
    from synology_dsm import SynologyDSM


class SynoAudioStation(SynoBaseApi):
    """An implementation of a Synology AudioStation."""

    def __init__(self, dsm: "SynologyDSM"):
        """Constructor method."""
        super().__init__(dsm)
        self._api = SynoAudioStationApi(dsm)
        self._info: Optional[AudioStationInfo] = None
        self._players: List[Player] = []

    async def update(self) -> None:
        """Update state from API."""
        self._info = await self._api.get_info()

        players = await self._api.remote_player_get_players()
        if players is not None:
            self._players = players.players

    @property
    def info(self) -> Optional[AudioStationInfo]:
        """Return a information about audio station."""
        return self._info

    @property
    def players(self) -> List[Player]:
        """Return a list of players."""
        return self._players

    async def get_remote_player(self, player_id: str) -> Optional[RemotePlayerInfo]:
        """Return a remote player, representing a player with all helpers."""
        player = await self.__get_player_by_id(player_id)
        if player is None:
            return None
        return RemotePlayerInfo(self._api, player)

    async def __get_player_by_id(self, player_id: str) -> Optional[Player]:
        """Return a player by id."""
        for player in self._players:
            if player.id == player_id:
                return player
        return None
