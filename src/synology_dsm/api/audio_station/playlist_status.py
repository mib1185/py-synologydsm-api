from enum import Enum


class PlaylistStatus(str, Enum):
    playing = "playing"
    stopped = "stopped"
    pause = "pause"
