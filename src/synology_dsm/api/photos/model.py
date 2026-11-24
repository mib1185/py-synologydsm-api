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

    item_id: int
    item_type: str
    file_name: str
    file_size: str
    thumbnail_cache_key: str
    thumbnail_size: str
    is_shared: bool
    passphrase: str
    time: int | None = None
    folder_id: int | None = None
    exif: dict | None = None
    width: int | None = None
    height: int | None = None
    orientation: int | None = None
    orientation_original: int | None = None
    person: list[dict] | None = None
    latitude: float | None = None
    longitude: float | None = None
    address: dict | None = None
