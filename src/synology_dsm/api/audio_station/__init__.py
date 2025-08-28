"""Synology AudioStation API wrapper."""
import asyncio
from typing import List, Optional, TYPE_CHECKING

from .models import (Player, RemotePlayerStatus, RepeatMode, ShuffleMode,
                     RemotePlayerAction, LibraryShareType, QueueMode, SongSortMode, Playlist, AudioStationInfo)
from .remote_player_info import RemotePlayerInfo
from .syno_audio_station_api import SynoAudioStationApi
from .. import SynoBaseApi

if TYPE_CHECKING:
    from synology_dsm import SynologyDSM


class SynoAudioStation(SynoBaseApi):
    """An implementation of a Synology AudioStation."""

    def __init__(self, dsm: "SynologyDSM"):
        super().__init__(dsm)
        self._api = SynoAudioStationApi(dsm)
        self._info: Optional[AudioStationInfo] = None
        self._remote_players: List[RemotePlayerInfo] = []

    async def update(self):
        self._info = await self._api.get_info()
        self._remote_players = await self.__get_players()

    @property
    def info(self) -> Optional[AudioStationInfo]:
        return self._info

    @property
    def remote_players(self) -> List[RemotePlayerInfo]:
        return self._remote_players

    def get_remote_player(self, player_id: str) -> Optional[RemotePlayerInfo]:
        for player in self.remote_players:
            if player.player.id == player_id:
                return player
        return None

    async def __add_status_to_player(self, player: Player):
        player = RemotePlayerInfo(self._api, player)
        await player.update()
        return player

    async def __get_players(self) -> List[RemotePlayerInfo]:
        players = await self._api.remote_player_get_players()

        tasks = []
        for player in players:
            tasks.append(self.__add_status_to_player(player))

        player_infos = await asyncio.gather(*tasks)
        return player_infos




