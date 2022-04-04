from enum import Enum


class RepeatMode(str, Enum):
    all = "all"
    none = "none"
    one = "one"
