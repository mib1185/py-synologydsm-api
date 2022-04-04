"""Synology AudioStation API wrapper."""
from typing import List, Dict, Any

from .library_share_type import LibraryShareType
from .player_list import PlayerList
from .playlist import Playlist
from .remote_player_action import RemotePlayerAction
from .remote_player_status import RemotePlayerStatus

import json

from .repeat_mode import RepeatMode
from .shuffle_mode import ShuffleMode
from .song_sort_mode import SongSortMode
from .queue_mode import QueueMode


def comma_join(value) -> str:
    return ",".join(value) if isinstance(value, list) else value


class SynoAudioStation:
    """An implementation of a Synology AudioStation."""

    API_KEY = "SYNO.AudioStation.*"
    REMOTE_PLAYER_KEY = "SYNO.AudioStation.RemotePlayer"
    REMOTE_PLAYER_STATUS_KEY = "SYNO.AudioStation.RemotePlayerStatus"

    def __init__(self, dsm):
        """Initialize Audio Station."""
        self._dsm = dsm

    def remote_player_get_player_status(self, player_uuid) -> RemotePlayerStatus:
        """Get status of remote player"""
        res = self._dsm.get(
            self.REMOTE_PLAYER_STATUS_KEY,
            "getstatus",
            {
                "id": "uuid:" + player_uuid,
                "additional": "song_tag,song_audio,subplayer_volume"
            },
        )
        return RemotePlayerStatus(res)

    def remote_player_get_players(self) -> PlayerList:
        """Get list of remote players"""
        res = self._dsm.get(
            self.REMOTE_PLAYER_KEY,
            "list",
            {
                "type": "all",
                "additional": "subplayer_list"
            },
        )

        return PlayerList(res["data"])

    def remote_player_get_current_playlist(self, player_uuid: str) -> Playlist:
        """Get current playlist of player"""
        opts = {
            "id": "uuid:" + player_uuid,
            "limit": 0,
            "additional": "song_tag,song_audio,song_rating",
            "version": 3,
        }

        res = self._dsm.post(self.REMOTE_PLAYER_KEY, "getplaylist", data=opts)

        return Playlist(res["data"])

    def __remote_update_playlist(self, player_uuid: str, playlist_queue_mode: QueueMode, opts: Dict[str, Any]) -> bool:
        """Update playlist of remote player"""

        base_opts = {
            "id": "uuid:" + player_uuid,
            "version": 3,
        }

        current = self.remote_player_get_current_playlist(player_uuid)

        if playlist_queue_mode == QueueMode.replace:
            base_opts["offset"] = 0
            base_opts["limit"] = current.total
            base_opts["keep_shuffle_order"] = "false"
        else:
            base_opts["offset"] = current.total
            base_opts["limit"] = 0
            base_opts["keep_shuffle_order"] = "true"

        final_opts = {**base_opts, **opts}
        res = self._dsm.post(self.REMOTE_PLAYER_KEY, "updateplaylist", data=final_opts)

        return res["success"]

    def remote_player_clear_playlist(self, player_uuid: str) -> bool:
        """Clear current playlist"""

        opts = {
            "updated_index": -1
        }

        return self.__remote_update_playlist(player_uuid, QueueMode.replace, opts)

    def remote_player_play_songs(self, player_uuid: str, song_ids: List[str],
                                 playlist_playlist_queue_mode: QueueMode, play_directly: bool = True) -> bool:
        """Play songs using their ids"""

        opts = {
            "songs": comma_join(song_ids),
            "library": LibraryShareType.shared.value,
            "play": play_directly
        }

        return self.__remote_update_playlist(player_uuid, playlist_playlist_queue_mode, opts)

    def remote_player_play_artist(self, player_uuid: str, artist: str, sort: SongSortMode,
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

        return self.__remote_update_playlist(player_uuid, playlist_queue_mode, opts)

    def remote_player_play_album(self, player_uuid: str, album_name: str, album_artist: str,
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

        return self.__remote_update_playlist(player_uuid, playlist_queue_mode, opts)

    def remote_player_jump_to_song(self, player_uuid: str, position_in_playlist: int) -> bool:
        """Change player current song to index in playlist"""

        res = self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={
                "id": "uuid:" + player_uuid,
                "action": RemotePlayerAction.play.value,
                "value": position_in_playlist
            },
        )

        return res["success"]

    def remote_player_control(self, player_uuid: str, action: RemotePlayerAction) -> bool:
        """Change player current playing status"""
        res = self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={
                "id": "uuid:" + player_uuid,
                "action": action.value
            },
        )

        return res["success"]

    def remote_player_volume(self, player_uuid: str, volume: int) -> bool:
        """Change player current volume"""

        if not 0 <= volume <= 100:
            raise ValueError('Volume should be between 0 and 100')

        res = self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={
                "id": "uuid:" + player_uuid,
                "action": "set_volume",
                "value": volume
            },
        )

        return res["success"]

    def remote_player_shuffle(self, player_uuid: str, shuffle: ShuffleMode) -> bool:
        """Change player current shuffle mode"""

        res = self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={
                "id": "uuid:" + player_uuid,
                "action": "set_shuffle",
                "value": shuffle.value
            },
        )

        return res["success"]

    def remote_player_repeat(self, player_uuid: str, repeat: RepeatMode) -> bool:
        """Change player current repeat mode"""

        res = self._dsm.post(
            self.REMOTE_PLAYER_KEY,
            "control",
            data={
                "id": "uuid:" + player_uuid,
                "action": "set_repeat",
                "value": repeat.value
            },
        )

        return res["success"]
