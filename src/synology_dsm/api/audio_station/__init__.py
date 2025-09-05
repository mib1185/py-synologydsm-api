"""Synology AudioStation API wrapper."""

import asyncio
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
        self._remote_players: List[RemotePlayerInfo] = []

    async def update(self) -> None:
        """Update state from API."""
        self._info = await self._api.get_info()
        self._remote_players = await self.__get_players()

    @property
    def info(self) -> Optional[AudioStationInfo]:
        """Return a information about audio station."""
        return self._info

    @property
    def remote_players(self) -> List[RemotePlayerInfo]:
        """Return a list of players."""
        return self._remote_players

    def get_remote_player(self, player_id: str) -> Optional[RemotePlayerInfo]:
        """Return a specific player."""
        for player in self.remote_players:
            if player.player.id == player_id:
                return player
        return None

    async def __get_player_info(self, player: Player) -> RemotePlayerInfo:
        """Fetch player info and update player."""
        player_info = RemotePlayerInfo(self._api, player)
        await player_info.update()
        return player_info

    async def __get_players(self) -> List[RemotePlayerInfo]:
        """Return a list of players."""
        players = await self._api.remote_player_get_players()

        if players is None:
            return []

        tasks = []
        for player in players.players:
            tasks.append(self.__get_player_info(player))

        player_infos = await asyncio.gather(*tasks)
        return player_infos
