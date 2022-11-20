"""Synology API models."""


class SynoBaseApi:
    """Base api class."""

    def __init__(self, dsm):
        """Constructor method."""
        self._dsm = dsm
        self._data = {}
