from enum import Enum


class RemotePlayerAction(str, Enum):
    play = "play"
    pause = "pause"
    stop = "stop"
    next = "next"
    prev = "prev"
