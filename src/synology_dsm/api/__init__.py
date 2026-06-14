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
        """Updates data."""
        if not getattr(self, "API_KEY", None) or not getattr(
            self, "UPDATE_METHOD", None
        ):
            raise NotImplementedError(
                f"{self.__class__.__name__} does not define API_KEY/UPDATE_METHOD, "
                "so it needs to implement its own update method."
            )

        raw_data = await self._dsm.get(self.API_KEY, self.UPDATE_METHOD)
        if isinstance(raw_data, dict) and (data := raw_data.get("data")) is not None:
            self._data = data
            return
        raise SynologyDSMAPINoDataException(self.API_KEY)
