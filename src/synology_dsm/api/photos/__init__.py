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
    BROWSE_ITEM_FOTOTEAM_API_KEY = "SYNO.FotoTeam.Browse.Item"
    BROWSE_SHARING_API_KEY = "SYNO.Foto.Sharing.Misc"

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

    async def get_albums_shared_with_me(
        self, offset: int = 0, limit: int = 100
    ) -> list[SynoPhotosAlbum] | None:
        """Get a list of all albums shared with me."""
        albums: list[SynoPhotosAlbum] = []
        raw_data = await self._dsm.get(
            self.BROWSE_SHARING_API_KEY,
            "list_shared_with_me_album",
            {"offset": offset, "limit": limit},
        )
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return None

        for album in data["list"]:
            albums.append(
                SynoPhotosAlbum(
                    album["id"], album["name"], album["item_count"], album["passphrase"]
                )
            )
        return albums

    def _raw_data_to_items(
        self, raw_data: bytes | dict | str
    ) -> list[SynoPhotosItem] | None:
        """Parse the raw data response to a list of photo items."""
        items: list[SynoPhotosItem] = []
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
        return self._raw_data_to_items(raw_data)

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
        return self._raw_data_to_items(raw_data)

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
