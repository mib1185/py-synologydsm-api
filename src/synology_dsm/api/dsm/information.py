"""DSM Information data."""

from __future__ import annotations

import re
from typing import TypedDict

from awesomeversion import AwesomeVersion

from synology_dsm.api import SynoBaseApi
from synology_dsm.exceptions import SynologyDSMException


class DsmInformationDataType(TypedDict, total=False):
    """Data type."""

    model: str
    ram: int
    serial: str
    temperature: int
    temperature_warn: bool
    uptime: int
    version: str
    version_string: str


class SynoDSMInformation(SynoBaseApi[DsmInformationDataType]):
    """Class containing Information data."""

    API_KEY = "SYNO.DSM.Info"

    async def update(self) -> None:
        """Updates information data."""
        raw_data = await self._dsm.get(self.API_KEY, "getinfo")
        if isinstance(raw_data, dict) and (data := raw_data.get("data")) is not None:
            self._data = data

    @property
    def model(self) -> str:
        """Model of the NAS."""
        return self._data["model"]

    @property
    def ram(self) -> int:
        """RAM of the NAS (in MB)."""
        return self._data["ram"]

    @property
    def serial(self) -> str:
        """Serial of the NAS."""
        return self._data["serial"]

    @property
    def temperature(self) -> int | None:
        """Temperature of the NAS."""
        return self._data.get("temperature")

    @property
    def temperature_warn(self) -> bool:
        """Temperature warning of the NAS."""
        # some very old nas may not provide this attribute
        return self._data.get("temperature_warn", False)

    @property
    def uptime(self) -> int:
        """Uptime of the NAS."""
        return self._data["uptime"]

    @property
    def version(self) -> str:
        """Version of the NAS (build version)."""
        return self._data["version"]

    @property
    def version_string(self) -> str:
        """Version of the NAS."""
        return self._data["version_string"]

    @property
    def awesome_version(self) -> AwesomeVersion:
        """Awesome version representation."""
        pattern = (
            r"DSM (?P<major>\d+)\.(?P<minor>\d+)"
            r"(\.(?P<micro>\d+))?-(?P<buildnumber>\d+)"
            r"( Update (?P<smallfixnumber>\d+))?"
        )
        match = re.match(pattern, self.version_string)
        if not match:
            raise SynologyDSMException(
                api=self.API_KEY,
                code=0,
                details=f"Could not parse version string {self.version_string}",
            )
        parts = match.groupdict()
        version = f"{parts['major']}.{parts['minor']}.{parts['micro'] or '0'}"
        if (smallfixnumber := parts.get("smallfixnumber")) is not None:
            version += f".{smallfixnumber}"

        return AwesomeVersion(version)
