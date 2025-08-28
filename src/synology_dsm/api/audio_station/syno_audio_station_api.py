import json
from typing import Dict, Any, List, Optional

from .models import (Player, RemotePlayerStatus, RepeatMode, ShuffleMode,
                     RemotePlayerAction, LibraryShareType, QueueMode, SongSortMode, Playlist, AudioStationInfo)
from .. import SynoBaseApi


def comma_join(value) -> str:
    return ",".join(value) if isinstance(value, list) else value

class SynoAudioStationApi(SynoBaseApi):
    API_KEY = "SYNO.AudioStation.*"
    INFO_API_KEY = "SYNO.AudioStation.Info"
    REMOTE_PLAYER_KEY = "SYNO.AudioStation.RemotePlayer"
    REMOTE_PLAYER_STATUS_KEY = "SYNO.AudioStation.RemotePlayerStatus"

    async def get_info(self) -> Optional[AudioStationInfo]:
        res = await self._dsm.get(self.INFO_API_KEY, "getinfo")
        if res["success"]:
            return AudioStationInfo(**res["data"])
        return None

    async def remote_player_get_current_playlist(self, player_id: str) -> Optional[Playlist]:
        """Get current playlist of player"""
        opts = {
            "id": player_id,
            "limit": 0,
            "additional": "song_tag,song_audio,song_rating",
            "version": 3,
        }

        res = await self._dsm.post(self.REMOTE_PLAYER_KEY, "getplaylist", data=opts)

        if res["success"]:
            return Playlist(**res["data"])
        return None

    async def __remote_update_playlist(self, player_id: str, playlist_queue_mode: QueueMode,
                                       opts: Dict[str, Any]) -> bool:
        """Update playlist of remote player"""

        base_opts = {
            "id": player_id,
            "version": 3,
        }

        current = await self.remote_player_get_current_playlist(player_id)

        if playlist_queue_mode == QueueMode.replace:
            base_opts["offset"] = 0
            base_opts["limit"] = current.total
            base_opts["keep_shuffle_order"] = "false"
        else:
            base_opts["offset"] = current.total
            base_opts["limit"] = 0
            base_opts["keep_shuffle_order"] = "true"

        final_opts = {**base_opts, **opts}
        res = await self._dsm.post(self.REMOTE_PLAYER_KEY, "updateplaylist", data=final_opts)

        return res["success"]

    async def remote_player_clear_playlist(self, player_id: str) -> bool:
        """Clear current playlist"""

        opts = {
            "updated_index": -1
        }

        return await self.__remote_update_playlist(player_id, QueueMode.replace, opts)

    async def remote_player_play_songs(self, player_id: str, song_ids: List[str],
                                       playlist_playlist_queue_mode: QueueMode, play_directly: bool = True) -> bool:
        """Play songs using their ids"""

        opts = {
            "songs": comma_join(song_ids),
            "library": LibraryShareType.shared.value,
            "play": play_directly
        }

        return await self.__remote_update_playlist(player_id, playlist_playlist_queue_mode, opts)

    async def remote_player_play_artist(self, player_id: str, artist: str, sort: SongSortMode,
                                        playlist_queue_mode: QueueMode, play_directly: bool = True) -> bool:
        """Play all song of an artist"""

        container_json = {
            "type": "artist",
            "sort_by": sort,
            "sort_direction": "ASC",
            "artist": artist
        }

        opts = {
            "library": LibraryShareType.shared.value,
            "play": play_directly,
            "containers_json": json.dumps([container_json])
        }

        return await self.__remote_update_playlist(player_id, playlist_queue_mode, opts)

    async def remote_player_play_album(self, player_id: str, album_name: str, album_artist: str,
                                       sort: SongSortMode, playlist_queue_mode: QueueMode,
                                       play_directly: bool = True) -> bool:
        """Play an album using album name and album artist"""

        container_json = {
            "type": "album",
            "sort_by": sort,
            "sort_direction": "ASC",
            "album": album_name,
            "album_artist": album_artist
        }

        opts = {
            "library": LibraryShareType.shared.value,
            "play": play_directly,
            "containers_json": json.dumps([container_json])
        }

        return await self.__remote_update_playlist(player_id, playlist_queue_mode, opts)

    async def remote_player_jump_to_song(self, player_id: str, position_in_playlist: int) -> bool:
        """Change player current song to index in playlist"""

        res = await self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={
                "id": player_id,
                "action": RemotePlayerAction.play.value,
                "value": position_in_playlist
            },
        )

        return res["success"]

    async def remote_player_control(self, player_id: str, action: RemotePlayerAction) -> bool:
        """Change player current playing status"""
        res = await self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={
                "id": player_id,
                "action": action.value
            },
        )

        return res["success"]

    async def remote_player_volume(self, player_id: str, volume: int) -> bool:
        """Change player current volume"""

        if not 0 <= volume <= 100:
            raise ValueError('Volume should be between 0 and 100')

        res = await self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={
                "id": player_id,
                "action": "set_volume",
                "value": volume
            },
        )
        return res["success"]

    async def remote_player_shuffle(self, player_id: str, shuffle: ShuffleMode) -> bool:
        """Change player current shuffle mode"""

        res = await self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={
                "id": player_id,
                "action": "set_shuffle",
                "value": shuffle.value
            },
        )

        return res["success"]

    async def remote_player_repeat(self, player_id: str, repeat: RepeatMode) -> bool:
        """Change player current repeat mode"""

        res = await self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={
                "id": player_id,
                "action": "set_repeat",
                "value": repeat.value
            },
        )

        return res["success"]

    async def remote_player_get_player_status(self, player_id: str) -> Optional[RemotePlayerStatus]:
        """Get status of remote player"""
        res = await self._dsm.get(
            self.REMOTE_PLAYER_STATUS_KEY,
            "getstatus",
            {
                "id": player_id,
                "additional": "song_tag,song_audio,subplayer_volume"
            },
        )

        if res["success"]:
            return RemotePlayerStatus(**res["data"])
        return None

    async def remote_player_get_players(self) -> List[Player]:
        """Get list of remote players"""
        res = await self._dsm.get(
            self.REMOTE_PLAYER_KEY,
            "list",
            {
                "type": "all",
                "additional": "subplayer_list"
            },
        )

        if res["success"]:
            return [Player(**p) for p in res["data"]["players"]]
        return []
