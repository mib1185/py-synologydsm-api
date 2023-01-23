"""DSM Network data."""
from synology_dsm.api import SynoBaseApi


class SynoDSMNetwork(SynoBaseApi):
    """Class containing Network data."""

    API_KEY = "SYNO.DSM.Network"

    async def update(self):
        """Updates network data."""
        raw_data = await self._dsm.get(self.API_KEY, "list")
        if raw_data:
            self._data = raw_data["data"]

    @property
    def dns(self):
        """DNS of the NAS."""
        return self._data.get("dns")

    @property
    def gateway(self):
        """Gateway of the NAS."""
        return self._data.get("gateway")

    @property
    def hostname(self):
        """Host name of the NAS."""
        return self._data.get("hostname")

    @property
    def interfaces(self):
        """Interfaces of the NAS."""
        return self._data.get("interfaces", [])

    def interface(self, eth_id):
        """Interface of the NAS."""
        for interface in self.interfaces:
            if interface["id"] == eth_id:
                return interface
        return None

    @property
    def macs(self):
        """MACs of the NAS."""  # noqa: D403
        macs = []
        for interface in self.interfaces:
            if interface.get("mac"):
                macs.append(interface["mac"])
        return macs

    @property
    def workgroup(self):
        """Workgroup of the NAS."""
        return self._data.get("workgroup")
