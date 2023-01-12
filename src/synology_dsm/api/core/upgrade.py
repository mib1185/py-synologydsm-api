"""DSM Upgrade data and actions."""
from synology_dsm.api import SynoBaseApi


class SynoCoreUpgrade(SynoBaseApi):
    """Class containing upgrade data and actions."""

    API_KEY = "SYNO.Core.Upgrade"
    API_SERVER_KEY = API_KEY + ".Server"

    async def update(self):
        """Updates Upgrade data."""
        raw_data = await self._dsm.get(self.API_SERVER_KEY, "check")
        if raw_data:
            self._data = raw_data["data"].get("update", raw_data["data"])

    @property
    def update_available(self):
        """Gets available update info."""
        return self._data.get("available")

    @property
    def available_version(self):
        """Gets available verion info."""
        return self._data.get("version")

    @property
    def available_version_details(self):
        """Gets details about available verion."""
        return self._data.get("version_details")

    @property
    def reboot_needed(self):
        """Gets info if reboot is needed."""
        return self._data.get("reboot")

    @property
    def service_restarts(self):
        """Gets info if services are restarted."""
        return self._data.get("restart")
