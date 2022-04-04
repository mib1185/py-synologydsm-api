from enum import Enum


class QueueMode(str, Enum):
    """Enum used by library, indicates if songs should be added to queue or replace"""
    enqueue = "enqueue"
    replace = "replace"
