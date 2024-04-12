"""Synology VideoStation API wrapper"""

from __future__ import annotations
import json

from synology_dsm.api import SynoBaseApi

from .video import SynoVideoStationDevices, SynoVideoStationLibrary
from .video import SynoVideoStationMovie
from .video import SynoVideoStationTVShow, SynoVideoStationTVShowEpisode


class SynoVideoStation(SynoBaseApi):
    """An implementation of a Synology VideoStation."""

    API_KEY = "SYNO.VideoStation2.*"
    LIBRARY_API_KEY = "SYNO.VideoStation2.AcrossLibrary"
    MOVIE_API_KEY = "SYNO.VideoStation2.Movie"
    POSTER_API_KEY = "SYNO.VideoStation2.Poster"
    TVSHOW_API_KEY = "SYNO.VideoStation2.TVShow"
    TVSHOW_EPISODE_API_KEY = "SYNO.VideoStation2.TVShowEpisode"
    CONTROLLER_DEVICE_API_KEY = "SYNO.VideoStation2.Controller.Device"

    async def get_devices(self)-> list[SynoVideoStationDevices] | None:
        """Get a Devices."""
        devices: list[SynoVideoStationDevices] = []
        raw_data = await self._dsm.get(
            self.CONTROLLER_DEVICE_API_KEY,
            "list",
            {
                "limit": 50000
            },
        )
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return None


        for device in data["device"]:
            devices.append(
                SynoVideoStationDevices(
                    device["id"],
                    device["title"],
                    device["now_playing"],
                    device["password_protected"],
                    device["volume_adjustable"],
                )
            )
        return devices

    async def get_library(self, policy: str = "recently_added") -> list[SynoVideoStationLibrary] | None:
        """Get a list library."""
        library: list[SynoVideoStationLibrary] = []
        raw_data = await self._dsm.get(
            self.LIBRARY_API_KEY,
            "list_library", 
            {
                "policy": policy,
            }
        )

        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return None
        
        for lib in data["library"]:
            library.append(
                SynoVideoStationLibrary(
                    lib["id"],
                    lib["type"]
                )
            )
        
        return library

    async def get_list_movie(
        self, offset: int = 0, limit: int = 100, sort_by: bool = True, sort_direction: str = 'desc', library_id: int = 0
    ) -> list[SynoVideoStationMovie] | None:
        """Get a list of all movies."""
        if bool(sort_by):
            sort_list = 'added'
        else:
            sort_list = ''
            sort_direction = 'asc'

        additional_1 = '["summary", "poster_mtime", "backdrop_mtime","file", '
        additional_2 = '"collection", "watched_ratio", "conversion_produced", '
        additional_3 = '"actor", "director", "genre", "writer", "extra"]'
        additional = ''.join([additional_1, additional_2, additional_3])

        raw_data = await self._dsm.get(
            self.MOVIE_API_KEY,
            "list", 
            {
                "offset": offset,
                "limit": limit,
                "sort_by": sort_list,
                "sort_direction": sort_direction,
                "library_id": library_id,
                "additional": additional
            }
        )

        movies: list[SynoVideoStationMovie] = []
        poster_url = ''
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return None

        for movie in data["movie"]:
            additional_data = movie["additional"]["extra"]
            additional = json.loads(additional_data)
            if (additional["com.synology.TheMovieDb"]["poster"]) is not None:
                poster_url = additional["com.synology.TheMovieDb"]["poster"]

            # raw_data_poster = await self._dsm.get(
            #     self.POSTER_API_KEY,
            #     "get",
            #     {
            #         "id": movie["id"],
            #         "type": "movie"
            #     },
            # )

            movies.append(
                SynoVideoStationMovie(
                    movie["id"],
                    movie["title"],
                    movie["additional"]["summary"],
                    poster_url,
                    # raw_data_poster,
                    movie["additional"]["file"][0]["id"],
                    movie["additional"]["file"][0]["path"],
                    movie["additional"]["file"][0]["path"],
                    movie["additional"]["file"][0]["video_codec"],
                    movie["additional"]["file"][0]["audio_codec"]
                )
            )
        
        return movies
    
    async def get_list_tvshow(
        self, offset: int = 0, limit: int = 100, sort_by: bool = True, sort_direction: str = 'desc', library_id: int = 0
    ) -> list[SynoVideoStationTVShow] | None:
        """Get a list of all Tvshow."""
        if bool(sort_by):
            sort_list = 'added'
        else:
            sort_list = ''
            sort_direction = 'asc'

        raw_data = await self._dsm.get(
            self.TVSHOW_API_KEY,
            "list", 
            {
                "offset": offset,
                "limit": limit,
                "sort_by": sort_list,
                "sort_direction": sort_direction,
                "library_id": library_id,
                "additional": '["poster_mtime","summary"]'
            
            }
        )

        tvshow: list[SynoVideoStationTVShow] = []
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return None

        for serie in data["tvshow"]:

            summary = ""
            if "summary" in serie["additional"]:
                summary = serie["additional"]["summary"]

            tvshow.append(
                SynoVideoStationTVShow(
                    serie["id"],
                    serie["title"],
                    serie["additional"]["total_seasons"],
                    summary
                )
            )
        
        return tvshow
    
    async def get_list_episode_tvshow(
            self, library_id: int, tvshow_id: int
    ) -> list[SynoVideoStationTVShowEpisode] | None:
        """Get a list of all Tvshow Episode."""

        additional_1 = '["summary", "poster_mtime", "backdrop_mtime","file", '
        additional_2 = '"collection", "watched_ratio", "conversion_produced", '
        additional_3 = '"actor", "director", "genre", "writer", "extra"]'
        additional = ''.join([additional_1, additional_2, additional_3])

        raw_data = await self._dsm.get(
            self.TVSHOW_EPISODE_API_KEY,
            "list",
            {
                "library_id": library_id,
                "tvshow_id": tvshow_id,
                "additional": additional,
                "limit": 500000
            }
        )

        tvshow_episode: list[SynoVideoStationTVShowEpisode] = []
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return None
        
        for episode in data["episode"]:

            summary = ""
            if "summary" in episode["additional"]:
                summary = episode["additional"]["summary"]

            tvshow_episode.append(
                SynoVideoStationTVShowEpisode(
                    episode["id"],
                    episode["tvshow_id"],
                    episode["season"],
                    episode["episode"],
                    episode["tagline"],
                    summary
                )
            )

        return tvshow_episode 

    async def get_poster(
        self, lib: SynoVideoStationLibrary, movie: SynoVideoStationMovie, tvshow: SynoVideoStationTVShow
    ) -> bytes | None:
        
        if movie is None:
            raw_data = await self._dsm.get(
                self.POSTER_API_KEY,
                "get",
                {
                    "id": tvshow.tvshow_id,
                    "type": lib.library_type
                },
            )
        else:
            raw_data = await self._dsm.get(
                self.POSTER_API_KEY,
                "get",
                {
                    "id": movie.movie_id,
                    "type": lib.library_type
                },
            )
        
        if isinstance(raw_data, bytes):
            return raw_data
        return None