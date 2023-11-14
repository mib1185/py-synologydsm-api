"""Synology VideoStation API wrapper."""

from __future__ import annotations
import json

from synology_dsm.api import SynoBaseApi

from .video import SynoVideoStationMovie, SynoVideoStationMoviePoster, SynoVideoStationDevices, SynoVideoStationMetadataMovie


class SynoVideoStation(SynoBaseApi):
    """An implementation of a Synology VideoStation."""

    API_KEY = "SYNO.VideoStation2.*"
    MOVIE_API_KEY = "SYNO.VideoStation2.Movie"
    POSTER_API_KEY = "SYNO.VideoStation2.Poster"
    TVSHOW_API_KEY = "SYNO.VideoStation2.TVShow"
    TVSHOW_EPISODE_API_KEY = "SYNO.VideoStation2.TVShowEpisode"
    CONTROLLER_DEVICE_API_KEY = "SYNO.VideoStation2.Controller.Device"

    async def get_list_movie(
        self, offset: int = 0, limit: int = 100, sort_by: bool = True, sort_direction: str = 'desc', library_id: int = 0
    ) -> list[SynoVideoStationMovie] | None:
        """Get a list of all movies."""
        if bool(sort_by):
            sort_by = 'added'
        else:
            sort_by = ''
            sort_direction = 'asc'

        raw_data = await self._dsm.get(
            self.MOVIE_API_KEY, "list", 
            {
                "offset": offset,
                "limit": limit,
                "sort_by": sort_by,
                "sort_direction": sort_direction,
                "library_id": library_id,
                "additional": '["poster_mtime","summary","watched_ratio","extra","collection"]'
            }
        )
        return self._raw_data_to_movies(raw_data)
    
    def _raw_data_to_movies(
        self, raw_data: bytes | dict | str
    ) -> list[SynoVideoStationMovie] | None:
        """Parse the raw data response to a list of photo items."""
        movies: list[SynoVideoStationMovie] = []
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return None

        for movie in data["movie"]:
            poster_str = movie["additional"]["extra"]
            poster = json.loads(poster_str)

            movies.append(
                SynoVideoStationMovie(
                    movie["id"],
                    movie["title"],
                    movie["additional"]["summary"]
                    # poster["com.synology.TheMovieDb"]["poster"]
                )
            )
        return movies

    async def get_url_poster(
        self, movie: SynoVideoStationMovie) -> bytes | None:
        """Get a poster from movie or TV Show."""
        raw_data = await self._dsm.get(
            self.POSTER_API_KEY,
            "get",
            {
                "id": movie.movie_id,
                "type": "movie",
            },
        )

        if isinstance(raw_data, bytes):
            return raw_data
        return None
    
    async def get_devices(self)-> list[SynoVideoStationDevices] | None:
        """Get a Devices."""
        raw_data = await self._dsm.get(
            self.CONTROLLER_DEVICE_API_KEY,
            "list",
            {
                "limit": 50000
            },
        )
        return raw_data
    
    async def get_metadata_movie(
        self, movie: SynoVideoStationMovie)-> list[SynoVideoStationMetadataMovie] | None:
        """Get a metadata in movie."""
        raw_data = await self._dsm.get(
            self.MOVIE_API_KEY,
            "getinfo",
            {
                "id": movie.movie_id,
                "additional": '["summary","poster_mtime","backdrop_mtime","file","collection","watched_ratio","conversion_produced","actor","director","genre","writer","extra"]'
            },
        )
        return raw_data
