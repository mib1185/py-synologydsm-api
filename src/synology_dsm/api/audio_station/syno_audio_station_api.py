"""Synology AudioStation Api calls wrapper."""

import json
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

from aiohttp import StreamReader
from dacite import Config, from_dict
from dacite.core import T

from .. import SynoBaseApi
from .models import (
    AudioStationInfo,
    LibraryShareType,
    Players,
    Playlist,
    QueueMode,
    RemotePlayerAction,
    RemotePlayerStatus,
    RepeatMode,
    ShuffleMode,
    SongSortMode,
)


def comma_join(value: Union[list, str]) -> str:
    """Join a list with commas."""
    return ",".join(value) if isinstance(value, list) else value


def parse_success(raw_data: Union[bytes, dict[Any, Any], str, StreamReader]) -> bool:
    """Parse api call was successful."""
    if not isinstance(raw_data, dict) or raw_data.get("success") is False:
        return False

    return True


def parse_data_if_success(
    data_class: Type[T], raw_data: Union[bytes, dict[Any, Any], str, StreamReader]
) -> Optional[T]:
    """Parse api data if call successful."""
    if (
        not isinstance(raw_data, dict)
        or raw_data.get("success") is False
        or (data := raw_data.get("data")) is None
    ):
        return None

    return from_dict(data_class=data_class, data=data, config=Config(cast=[Enum]))


class SynoAudioStationApi(SynoBaseApi):
    """Helper to make all api call to AudioStation."""

    API_KEY = "SYNO.AudioStation.*"
    INFO_API_KEY = "SYNO.AudioStation.Info"
    REMOTE_PLAYER_KEY = "SYNO.AudioStation.RemotePlayer"
    REMOTE_PLAYER_STATUS_KEY = "SYNO.AudioStation.RemotePlayerStatus"

    async def get_info(self) -> Optional[AudioStationInfo]:
        """Get AudioStation information."""
        res = await self._dsm.get(self.INFO_API_KEY, "getinfo")
        return parse_data_if_success(AudioStationInfo, res)

    async def remote_player_get_current_playlist(
        self, player_id: str
    ) -> Optional[Playlist]:
        """Get current playlist of player."""
        opts = {
            "id": player_id,
            "limit": 0,
            "additional": "song_tag,song_audio,song_rating",
            "version": 3,
        }

        res = await self._dsm.post(self.REMOTE_PLAYER_KEY, "getplaylist", data=opts)
        return parse_data_if_success(Playlist, res)

    async def __remote_update_playlist(
        self, player_id: str, playlist_queue_mode: QueueMode, opts: Dict[str, Any]
    ) -> bool:
        """Update playlist of remote player."""
        base_opts = {
            "id": player_id,
            "version": 3,
        }

        current = await self.remote_player_get_current_playlist(player_id)
        if current is None:
            return False

        if playlist_queue_mode == QueueMode.replace:
            base_opts["offset"] = 0
            base_opts["limit"] = current.total
            base_opts["keep_shuffle_order"] = "false"
        else:
            base_opts["offset"] = current.total
            base_opts["limit"] = 0
            base_opts["keep_shuffle_order"] = "true"

        final_opts = {**base_opts, **opts}
        res = await self._dsm.post(
            self.REMOTE_PLAYER_KEY, "updateplaylist", data=final_opts
        )

        return parse_success(res)

    async def remote_player_clear_playlist(self, player_id: str) -> bool:
        """Clear current playlist."""
        opts = {"updated_index": -1}

        return await self.__remote_update_playlist(player_id, QueueMode.replace, opts)

    async def remote_player_play_songs(
        self,
        player_id: str,
        song_ids: List[str],
        playlist_playlist_queue_mode: QueueMode,
        play_directly: bool = True,
    ) -> bool:
        """Play songs using their ids."""
        opts = {
            "songs": comma_join(song_ids),
            "library": LibraryShareType.shared.value,
            "play": play_directly,
        }

        return await self.__remote_update_playlist(
            player_id, playlist_playlist_queue_mode, opts
        )

    async def remote_player_play_artist(
        self,
        player_id: str,
        artist: str,
        sort: SongSortMode,
        playlist_queue_mode: QueueMode,
        play_directly: bool = True,
    ) -> bool:
        """Play all song of an artist."""
        container_json = {
            "type": "artist",
            "sort_by": sort,
            "sort_direction": "ASC",
            "artist": artist,
        }

        opts = {
            "library": LibraryShareType.shared.value,
            "play": play_directly,
            "containers_json": json.dumps([container_json]),
        }

        return await self.__remote_update_playlist(player_id, playlist_queue_mode, opts)

    async def remote_player_play_album(
        self,
        player_id: str,
        album_name: str,
        album_artist: str,
        sort: SongSortMode,
        playlist_queue_mode: QueueMode,
        play_directly: bool = True,
    ) -> bool:
        """Play an album using album name and album artist."""
        container_json = {
            "type": "album",
            "sort_by": sort,
            "sort_direction": "ASC",
            "album": album_name,
            "album_artist": album_artist,
        }

        opts = {
            "library": LibraryShareType.shared.value,
            "play": play_directly,
            "containers_json": json.dumps([container_json]),
        }

        return await self.__remote_update_playlist(player_id, playlist_queue_mode, opts)

    async def remote_player_jump_to_song(
        self, player_id: str, position_in_playlist: int
    ) -> bool:
        """Change player current song to index in playlist."""
        res = await self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={
                "id": player_id,
                "action": RemotePlayerAction.play.value,
                "value": position_in_playlist,
            },
        )

        return parse_success(res)

    async def remote_player_control(
        self, player_id: str, action: RemotePlayerAction
    ) -> bool:
        """Change player current playing status."""
        res = await self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={"id": player_id, "action": action.value},
        )

        return parse_success(res)

    async def remote_player_volume(self, player_id: str, volume: int) -> bool:
        """Change player current volume."""
        if not 0 <= volume <= 100:
            raise ValueError("Volume should be between 0 and 100")

        res = await self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={"id": player_id, "action": "set_volume", "value": volume},
        )

        return parse_success(res)

    async def remote_player_shuffle(self, player_id: str, shuffle: ShuffleMode) -> bool:
        """Change player current shuffle mode."""
        res = await self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={"id": player_id, "action": "set_shuffle", "value": shuffle.value},
        )

        return parse_success(res)

    async def remote_player_repeat(self, player_id: str, repeat: RepeatMode) -> bool:
        """Change player current repeat mode."""
        res = await self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={"id": player_id, "action": "set_repeat", "value": repeat.value},
        )

        return parse_success(res)

    async def remote_player_get_player_status(
        self, player_id: str
    ) -> Optional[RemotePlayerStatus]:
        """Get status of remote player."""
        res = await self._dsm.get(
            self.REMOTE_PLAYER_STATUS_KEY,
            "getstatus",
            {"id": player_id, "additional": "song_tag,song_audio,subplayer_volume"},
        )

        return parse_data_if_success(RemotePlayerStatus, res)

    async def remote_player_get_players(self) -> Optional[Players]:
        """Get list of remote players."""
        res = await self._dsm.get(
            self.REMOTE_PLAYER_KEY,
            "list",
            {"type": "all", "additional": "subplayer_list"},
        )
        return parse_data_if_success(Players, res)
