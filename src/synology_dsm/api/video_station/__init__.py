"""Synology VideoStation API wrapper."""

from __future__ import annotations
import json

from synology_dsm.api import SynoBaseApi

from .video import SynoVideoStationMovie, SynoVideoStationMoviePoster


class SynoVideoStation(SynoBaseApi):
    """An implementation of a Synology VideoStation."""

    API_KEY = "SYNO.VideoStation2.*"
    MOVIE_API_KEY = "SYNO.VideoStation2.Movie"
    POSTER_API_KEY = "SYNO.VideoStation2.Poster"
    TVSHOW_API_KEY = "SYNO.VideoStation2.TVShow"
    TVSHOW_EPISODE_API_KEY = "SYNO.VideoStation2.TVShowEpisode"

    async def get_movies(
        self, offset: int = 0, limit: int = 100, sort_by: bool = True, sort_direction: str = 'desc', library_id: int = 0
    ) -> list[SynoVideoStationMovie] | None:
        """Get a list of all movies."""
        movies: list[SynoVideoStationMovie] = []
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
                "additional": '["poster_mtime","summary","watched_ratio","extra","file"]'
            }
        )
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return None
        for movie in data["movie"]:
            poster_str = movie["additional"]["extra"]
            poster = json.loads(poster_str)
            movies.append(
                SynoVideoStationMovie(
                    movie["id"],
                    movie["title"],
                    movie["additional"]["summary"],
                    poster["com.synology.TheMovieDb"]["poster"]
                )
            )
        return movies

    async def get_poster_from_movie(
        self, movie: SynoVideoStationMovie
    ) -> list[SynoVideoStationMoviePoster] | None:
        """Get a poster from movie."""
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
