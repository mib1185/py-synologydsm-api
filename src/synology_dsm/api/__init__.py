"""Synology API models."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from synology_dsm import SynologyDSM


class SynoBaseApi:
    """Base api class."""

    def __init__(self, dsm: "SynologyDSM") -> None:
        """Constructor method."""
        self._dsm = dsm
        self._data: dict[str, Any] = {}
