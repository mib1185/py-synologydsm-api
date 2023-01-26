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
    SEARCH_API_KEY = "SYNO.Foto.Search.Search"
    THUMBNAIL_API_KEY = "SYNO.Foto.Thumbnail"

    async def get_albums(self, offset=0, limit=100) -> list[SynoPhotosAlbum]:
        """Get a list of all albums."""
        albums: list[SynoPhotosAlbum] = []
        res = (
            await self._dsm.get(
                self.BROWSE_ALBUMS_API_KEY, "list", {"offset": offset, "limit": limit}
            )
        )["data"]["list"]
        for album in res:
            albums.append(
                SynoPhotosAlbum(album["id"], album["name"], album["item_count"])
            )
        return albums

    async def get_items_from_album(
        self, album: SynoPhotosAlbum, offset=0, limit=100
    ) -> list[SynoPhotosItem]:
        """Get a list of all items from given album."""
        items: list[SynoPhotosItem] = []
        res = (
            await self._dsm.get(
                self.BROWSE_ITEM_API_KEY,
                "list",
                {
                    "album_id": album.album_id,
                    "offset": offset,
                    "limit": limit,
                    "additional": '["thumbnail"]',
                },
            )
        )["data"]["list"]

        for item in res:
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
                )
            )
        return items

    async def get_items_from_search(
        self, search_string: str, offset=0, limit=100
    ) -> list[SynoPhotosItem]:
        """Get a list of all items matching the keyword."""
        items: list[SynoPhotosItem] = []
        res = (
            await self._dsm.get(
                self.SEARCH_API_KEY,
                "list_item",
                {
                    "keyword": search_string,
                    "offset": offset,
                    "limit": limit,
                    "additional": '["thumbnail"]',
                },
            )
        )["data"]["list"]

        for item in res:
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
                )
            )
        return items

    async def download_item(self, item: SynoPhotosItem) -> bytearray:
        """Download the given item."""
        return bytearray(
            await self._dsm.get(
                self.DOWNLOAD_API_KEY,
                "download",
                {
                    "unit_id": f"[{item.item_id}]",
                    "cache_key": item.thumbnail_cache_key,
                },
            )
        )

    async def download_item_thumbnail(self, item: SynoPhotosItem) -> bytearray:
        """Download the given items thumbnail."""
        return bytearray(
            await self._dsm.get(
                self.THUMBNAIL_API_KEY,
                "get",
                {
                    "id": item.item_id,
                    "cache_key": item.thumbnail_cache_key,
                    "size": item.thumbnail_size,
                    "type": "unit",
                },
            )
        )

    async def get_item_thumbnail_url(self, item: SynoPhotosItem) -> str:
        """Get the url of given items thumbnail."""
        return await self._dsm.generate_url(
            self.THUMBNAIL_API_KEY,
            "get",
            {
                "id": item.item_id,
                "cache_key": item.thumbnail_cache_key,
                "size": item.thumbnail_size,
                "type": "unit",
            },
        )
