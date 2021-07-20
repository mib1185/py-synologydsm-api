"""DSM Upgrade data and actions."""
from __future__ import annotations

from synology_dsm import SynologyDSM


class SynoCoreUpgrade:
    """Class containing upgrade data and actions."""

    API_KEY = "SYNO.Core.Upgrade"
    API_SERVER_KEY = API_KEY + ".Server"

    def __init__(self, dsm: SynologyDSM) -> None:
        """Constructor method."""
        self._dsm = dsm
        self._data: dict = {}

    def update(self) -> None:
        """Updates Upgrade data."""
        raw_data = self._dsm.get(self.API_SERVER_KEY, "check")
        if raw_data:
            self._data = raw_data["data"].get("update", raw_data["data"])

    @property
    def update_available(self) -> bool | None:
        """Gets available update info."""
        return self._data.get("available")

    @property
    def available_version(self) -> str | None:
        """Gets available verion info."""
        return self._data.get("version")

    @property
    def reboot_needed(self) -> str | None:
        """Gets info if reboot is needed."""
        return self._data.get("reboot")

    @property
    def service_restarts(self) -> str | None:
        """Gets info if services are restarted."""
        return self._data.get("restart")
