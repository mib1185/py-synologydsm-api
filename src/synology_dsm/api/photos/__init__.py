"""Synology Photos API wrapper."""

from __future__ import annotations

import datetime

from synology_dsm.api import SynoBaseApi

from .model import SynoPhotosAlbum, SynoPhotosItem


class SynoPhotos(SynoBaseApi):
    """An implementation of a Synology Photos."""

    API_KEY = "SYNO.Foto.*"
    BROWSE_ALBUMS_API_KEY = "SYNO.Foto.Browse.Album"
    BROWSE_ITEM_API_KEY = "SYNO.Foto.Browse.Item"
    DOWNLOAD_API_KEY = "SYNO.Foto.Download"
    DOWNLOAD_FOTOTEAM_API_KEY = "SYNO.FotoTeam.Download"
    SEARCH_API_KEY = "SYNO.Foto.Search.Search"
    THUMBNAIL_API_KEY = "SYNO.Foto.Thumbnail"
    THUMBNAIL_FOTOTEAM_API_KEY = "SYNO.FotoTeam.Thumbnail"
    BROWSE_ITEM_FOTOTEAM_API_KEY = "SYNO.FotoTeam.Browse.Item"

    async def get_memories_full(
        self,
        min_year: int = 1990,
        excluded_folders: list[int] | None = None,
        excluded_extensions: tuple[str, ...] = (".raw", ".rw1", ".rw2"),
        excluded_persons: list[int] | None = None,
    ) -> list[dict] | None:
        """Get memories with additional information.

        A memory is an item (photo/video) recorded the same day (day and month)
        but in the previous years. Compared to get_memories(), this function
        returns additional information, e.g. recognized persons, exif data,
        etc.

        Arguments:
            min_year: earliest year considered.
            excluded_folders: folder_ids to exclude.
            excluded_extensions: file extensions to exclude.
            excluded_persons: person_ids to exclude.

        Returns:
            Memories with the most recent ones first. Within the same year,
            memories are sorted by descending recording time (i.e. from morning
            to evening). Duplicates (based on file name, file size, and
            recording time) are removed from result.
        """
        if excluded_folders is None:
            excluded_folders = []
        if excluded_persons is None:
            excluded_persons = []

        all_photos = []
        limit = 1000

        current_date = datetime.date.today()
        current_day = current_date.day
        current_month = current_date.month
        current_year = current_date.year

        for i in range(current_year, min_year - 1, -1):
            year_photos: list[dict] = []
            has_more = True
            offset = 0

            start_date = datetime.datetime(
                i, current_month, current_day, 0, 0, 0, tzinfo=datetime.timezone.utc
            ).timestamp()
            end_date = datetime.datetime(
                i, current_month, current_day, 23, 59, 59, tzinfo=datetime.timezone.utc
            ).timestamp()

            while has_more:
                raw_data = await self._dsm.get(
                    self.BROWSE_ITEM_API_KEY,
                    method="list_with_filter",
                    params={
                        "version": 2,
                        "offset": offset,
                        "limit": limit,
                        "time": (
                            f'[{{"start_time":{start_date:.0f},'
                            f'"end_time":{end_date:.0f}}}]'
                        ),
                        "additional": (
                            '["thumbnail", "resolution", "exif", "person", ',
                            '"address","gps"]',
                        ),
                    },
                )
                if (
                    not isinstance(raw_data, dict)
                    or (data := raw_data.get("data")) is None
                ):
                    has_more = False
                    continue
                if "list" in data and len(data["list"]) > 0:
                    year_photos += data["list"]
                    offset += limit
                else:
                    has_more = False

            # sort by time photo was taken
            year_photos.sort(key=lambda x: x["time"])

            # basic duplicate check
            final_year_photos = []
            seen: set[tuple] = set()
            for photo in year_photos:
                key = (photo["filename"], photo["filesize"], photo["time"])
                if (
                    key not in seen  # exclude duplicates
                    # exclude based on folder
                    and photo["folder_id"] not in excluded_folders
                    and not photo["filename"].lower()
                    # exclude based on extension
                    .endswith(excluded_extensions)
                    and not any(
                        sub.get("id") in excluded_persons
                        for sub in photo["additional"]["person"]
                    )
                ):  # exclude based on person(s)
                    final_year_photos.append(photo)
                    seen.add(key)

            if len(final_year_photos) == 0:
                continue

            all_photos.extend(final_year_photos)

        return all_photos

    async def get_memories(
        self,
        min_year: int = 1990,
        excluded_folders: list[int] | None = None,
        excluded_extensions: tuple[str, ...] = (".raw", ".rw1", ".rw2"),
        excluded_persons: list[int] | None = None,
    ) -> list[SynoPhotosItem] | None:
        """Get memories with additional information.

        A memory is an item (photo/video) recorded the same day (day and month)
        but in the previous years. Compared to get_memories(), this function
        returns additional information, e.g. recognized persons, exif data,
        etc.

        Arguments:
            min_year: earliest year considered.
            excluded_folders: folder_ids to exclude.
            excluded_extensions: file extensions to exclude.
            excluded_persons: person_ids to exclude.

        Returns:
            Memories with the most recent ones first. Within the same year,
            memories are sorted by descending recording time (i.e. from morning
            to evening). Duplicates (based on file name, file size, and
            recording time) are removed from result.
        """
        all_photos: list[SynoPhotosItem] = []
        photos = await self.get_memories_full(
            min_year, excluded_folders, excluded_extensions, excluded_persons
        )
        items = self._raw_data_to_items({"data": {"list": photos}})
        if items is not None:
            all_photos.extend(items)

        return all_photos

    async def get_albums(
        self, offset: int = 0, limit: int = 100
    ) -> list[SynoPhotosAlbum] | None:
        """Get a list of all albums."""
        albums: list[SynoPhotosAlbum] = []
        raw_data = await self._dsm.get(
            self.BROWSE_ALBUMS_API_KEY,
            "list",
            {"offset": offset, "limit": limit, "category": "normal_share_with_me"},
        )
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return None

        for album in data["list"]:
            albums.append(
                SynoPhotosAlbum(
                    album["id"],
                    album["name"],
                    album["item_count"],
                    album["passphrase"],
                )
            )
        return albums

    def _raw_data_to_items(  # noqa: S107
        self, raw_data: dict, passphrase: str = ""
    ) -> list[SynoPhotosItem] | None:
        """Parse the raw data response to a list of photo items."""
        items: list[SynoPhotosItem] = []
        if (data := raw_data.get("data")) is None:
            return None

        for item in data["list"]:
            if item["additional"]["thumbnail"]["xl"] == "ready":
                size = "xl"
            elif item["additional"]["thumbnail"]["m"] == "ready":
                size = "m"
            else:
                size = "sm"

            items.append(
                SynoPhotosItem(
                    item["id"],
                    item["type"],
                    item["filename"],
                    item["filesize"],
                    item["additional"]["thumbnail"]["cache_key"],
                    size,
                    item["owner_user_id"] == 0,
                    passphrase,
                )
            )
        return items

    async def get_items_from_album(
        self, album: SynoPhotosAlbum, offset: int = 0, limit: int = 100
    ) -> list[SynoPhotosItem] | None:
        """Get a list of all items from given album."""
        params = {
            "offset": offset,
            "limit": limit,
            "additional": '["thumbnail"]',
        }
        if album.passphrase:
            params["passphrase"] = album.passphrase
        else:
            params["album_id"] = album.album_id

        raw_data = await self._dsm.get(
            self.BROWSE_ITEM_API_KEY,
            "list",
            params,
        )
        if not isinstance(raw_data, dict):
            return None
        return self._raw_data_to_items(raw_data, album.passphrase)

    async def get_items_from_shared_space(
        self, offset: int = 0, limit: int = 100
    ) -> list[SynoPhotosItem] | None:
        """Get a list of all items from the shared space."""
        raw_data = await self._dsm.get(
            self.BROWSE_ITEM_FOTOTEAM_API_KEY,
            "list",
            {
                "offset": offset,
                "limit": limit,
                "additional": '["thumbnail"]',
            },
        )
        if not isinstance(raw_data, dict):
            return None
        return self._raw_data_to_items(raw_data)

    async def get_items_from_search(
        self, search_string: str, offset: int = 0, limit: int = 100
    ) -> list[SynoPhotosItem] | None:
        """Get a list of all items matching the keyword."""
        raw_data = await self._dsm.get(
            self.SEARCH_API_KEY,
            "list_item",
            {
                "keyword": search_string,
                "offset": offset,
                "limit": limit,
                "additional": '["thumbnail"]',
            },
        )
        if not isinstance(raw_data, dict):
            return None
        return self._raw_data_to_items(raw_data)

    async def download_item(self, item: SynoPhotosItem) -> bytes | None:
        """Download the given item."""
        download_api = self.DOWNLOAD_API_KEY
        if item.is_shared:
            download_api = self.DOWNLOAD_FOTOTEAM_API_KEY

        params = {
            "unit_id": f"[{item.item_id}]",
            "cache_key": item.thumbnail_cache_key,
        }

        if item.passphrase:
            params["passphrase"] = item.passphrase

        raw_data = await self._dsm.get(
            download_api,
            "download",
            params,
        )
        if isinstance(raw_data, bytes):
            return raw_data
        return None

    async def download_item_thumbnail(self, item: SynoPhotosItem) -> bytes | None:
        """Download the given items thumbnail."""
        download_api = self.THUMBNAIL_API_KEY
        if item.is_shared:
            download_api = self.THUMBNAIL_FOTOTEAM_API_KEY

        params = {
            "id": item.item_id,
            "cache_key": item.thumbnail_cache_key,
            "size": item.thumbnail_size,
            "type": "unit",
        }

        if item.passphrase:
            params["passphrase"] = item.passphrase

        raw_data = await self._dsm.get(
            download_api,
            "get",
            params,
        )
        if isinstance(raw_data, bytes):
            return raw_data
        return None

    async def get_item_thumbnail_url(self, item: SynoPhotosItem) -> str:
        """Get the url of given items thumbnail."""
        download_api = self.THUMBNAIL_API_KEY
        if item.is_shared:
            download_api = self.THUMBNAIL_FOTOTEAM_API_KEY

        params = {
            "id": item.item_id,
            "cache_key": item.thumbnail_cache_key,
            "size": item.thumbnail_size,
            "type": "unit",
        }

        if item.passphrase:
            params["passphrase"] = item.passphrase

        return await self._dsm.generate_url(
            download_api,
            "get",
            params,
        )
