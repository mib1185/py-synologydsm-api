"""Synology Photos API wrapper."""

from __future__ import annotations

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

    async def get_albums(
        self, offset: int = 0, limit: int = 100
    ) -> list[SynoPhotosAlbum] | None:
        """Get a list of all albums."""
        albums: list[SynoPhotosAlbum] = []
        raw_data = await self._dsm.get(
            self.BROWSE_ALBUMS_API_KEY, "list", {"offset": offset, "limit": limit}
        )
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return None

        for album in data["list"]:
            albums.append(
                SynoPhotosAlbum(album["id"], album["name"], album["item_count"])
            )
        return albums

    async def get_items_from_album(
        self, album: SynoPhotosAlbum, offset: int = 0, limit: int = 100
    ) -> list[SynoPhotosItem] | None:
        """Get a list of all items from given album."""
        items: list[SynoPhotosItem] = []
        raw_data = await self._dsm.get(
            self.BROWSE_ITEM_API_KEY,
            "list",
            {
                "album_id": album.album_id,
                "offset": offset,
                "limit": limit,
                "additional": '["thumbnail"]',
            },
        )
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
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
                )
            )
        return items

    async def get_items_from_search(
        self, search_string: str, offset: int = 0, limit: int = 100
    ) -> list[SynoPhotosItem] | None:
        """Get a list of all items matching the keyword."""
        items: list[SynoPhotosItem] = []
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
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
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
                )
            )
        return items

    async def download_item(self, item: SynoPhotosItem) -> bytes | None:
        """Download the given item."""
        download_api = self.DOWNLOAD_API_KEY
        if item.is_shared:
            download_api = self.DOWNLOAD_FOTOTEAM_API_KEY
        raw_data = await self._dsm.get(
            download_api,
            "download",
            {
                "unit_id": f"[{item.item_id}]",
                "cache_key": item.thumbnail_cache_key,
            },
        )
        if isinstance(raw_data, bytes):
            return raw_data
        return None

    async def download_item_thumbnail(self, item: SynoPhotosItem) -> bytes | None:
        """Download the given items thumbnail."""
        download_api = self.THUMBNAIL_API_KEY
        if item.is_shared:
            download_api = self.THUMBNAIL_FOTOTEAM_API_KEY
        raw_data = await self._dsm.get(
            download_api,
            "get",
            {
                "id": item.item_id,
                "cache_key": item.thumbnail_cache_key,
                "size": item.thumbnail_size,
                "type": "unit",
            },
        )
        if isinstance(raw_data, bytes):
            return raw_data
        return None

    async def get_item_thumbnail_url(self, item: SynoPhotosItem) -> str:
        """Get the url of given items thumbnail."""
        download_api = self.THUMBNAIL_API_KEY
        if item.is_shared:
            download_api = self.THUMBNAIL_FOTOTEAM_API_KEY
        return await self._dsm.generate_url(
            download_api,
            "get",
            {
                "id": item.item_id,
                "cache_key": item.thumbnail_cache_key,
                "size": item.thumbnail_size,
                "type": "unit",
            },
        )
