from enum import Enum


class SongSortMode(str, Enum):
    track = "track"
    album = "album"
    name = "name"
