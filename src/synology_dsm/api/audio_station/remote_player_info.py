from typing import Optional, List

from synology_dsm.api.audio_station import Player, SynoAudioStationApi
from synology_dsm.api.audio_station.models import RepeatMode, ShuffleMode, RemotePlayerAction, QueueMode, SongSortMode, \
    Playlist, RemotePlayerStatus


class RemotePlayerInfo:
    """Model used by library to store info about a remote player."""

    def __init__(self, api: SynoAudioStationApi, player: Player):
        """Initialize RemotePlayerInfo."""
        self._api = api
        self._player = player
        self._status: Optional[RemotePlayerStatus] = None

    async def update(self):
        self._status = await self._api.remote_player_get_player_status(self._player.id)

    @property
    def player(self) -> Player:
        return self._player

    @property
    def status(self) -> RemotePlayerStatus:
        return self._status

    async def get_current_playlist(self) -> Playlist:
        """Get current playlist"""
        return await self._api.remote_player_get_current_playlist(self._player.id)

    async def clear_playlist(self) -> bool:
        """Clear current playlist"""
        return await self.__return_success_and_update(await self._api.remote_player_clear_playlist(self._player.id))

    async def play_songs(self, song_ids: List[str], playlist_playlist_queue_mode: QueueMode,
                         play_directly: bool = True) -> bool:
        """Play songs using their ids"""
        return await self.__return_success_and_update(
            await self._api.remote_player_play_songs(self._player.id, song_ids, playlist_playlist_queue_mode,
                                                     play_directly))

    async def play_artist(self, artist: str, sort: SongSortMode, playlist_queue_mode: QueueMode,
                          play_directly: bool = True) -> bool:
        """Play all song of an artist"""
        return await self.__return_success_and_update(
            await self._api.remote_player_play_artist(self._player.id, artist, sort, playlist_queue_mode,
                                                      play_directly))

    async def play_album(self, album_name: str, album_artist: str, sort: SongSortMode, playlist_queue_mode: QueueMode,
                         play_directly: bool = True) -> bool:
        """Play an album using album name and album artist"""
        return await self.__return_success_and_update(
            await self._api.remote_player_play_album(self._player.id, album_name, album_artist, sort,
                                                     playlist_queue_mode,
                                                     play_directly))

    async def jump_to_song(self, position_in_playlist: int) -> bool:
        """Change player current song to index in playlist"""
        return await self.__return_success_and_update(
            await self._api.remote_player_jump_to_song(self._player.id, position_in_playlist))

    async def control(self, action: RemotePlayerAction) -> bool:
        """Change player current playing status"""
        return await self.__return_success_and_update(await self._api.remote_player_control(self._player.id, action))

    async def volume(self, volume: int) -> bool:
        """Change player current volume"""
        return await self.__return_success_and_update(await self._api.remote_player_volume(self._player.id, volume))

    async def shuffle(self, shuffle: ShuffleMode) -> bool:
        """Change player current shuffle mode"""
        return await self.__return_success_and_update(await self._api.remote_player_shuffle(self._player.id, shuffle))

    async def repeat(self, repeat: RepeatMode) -> bool:
        """Change player current repeat mode"""
        return await self.__return_success_and_update(await self._api.remote_player_repeat(self._player.id, repeat))

    async def __return_success_and_update(self, success: bool):
        if success:
            await self.update()
        return success

