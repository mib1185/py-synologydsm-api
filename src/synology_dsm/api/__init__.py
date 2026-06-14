"""Synology API models."""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from synology_dsm.exceptions import SynologyDSMAPINoDataException

if TYPE_CHECKING:
    from synology_dsm import SynologyDSM


_DataT = TypeVar("_DataT")


class SynoBaseApi(Generic[_DataT]):
    """Base api class."""

    API_KEY: str
    UPDATE_METHOD: str

    def __init__(self, dsm: "SynologyDSM") -> None:
        """Constructor method."""
        self._dsm = dsm
        self._data: _DataT = {}  # type: ignore[assignment]

    async def update(self) -> None:
        """Updates security data."""
        raw_data = await self._dsm.get(self.API_KEY, self.UPDATE_METHOD)
        if isinstance(raw_data, dict) and (data := raw_data.get("data")) is not None:
            self._data = data
        else:
            raise SynologyDSMAPINoDataException(self.API_KEY)
