"""Data models for Synology Photos Module."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SynoPhotosAlbum:
    """Representation of an Synology Photos Album."""

    album_id: int
    name: str
    item_count: int
    passphrase: str


@dataclass
class SynoPhotosItem:
    """Representation of an Synology Photos Item."""

    def __init__(
        self,
        item_id: int,
        item_type: str,
        file_name: str,
        file_size: str,
        thumbnail_cache_key: str,
        thumbnail_size: str,
        is_shared: bool,
        passphrase: str,
        time: int | None = None,
        folder_id: int | None = None,
        exif: dict | None = None,
        width: int | None = None,
        height: int | None = None,
        orientation: int | None = None,
        orientation_original: int | None = None,
        person: list[dict] | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        address: dict | None = None,
    ):
        """Initializes a SynoPhotosItem."""
        self.item_id = item_id
        self.item_type = item_type
        self.file_name = file_name
        self.file_size = file_size
        self.thumbnail_cache_key = thumbnail_cache_key
        self.thumbnail_size = thumbnail_size
        self.is_shared = is_shared
        self.passphrase = passphrase
        self.time = time
        self.folder_id = folder_id
        self.exif = exif
        self.width = width
        self.height = height
        self.orientation = orientation
        self.orientation_original = orientation_original
        self.person = person
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
