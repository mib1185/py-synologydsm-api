"""DSM Network data."""

from __future__ import annotations

from typing import TypedDict

from synology_dsm.api import SynoBaseApi

InterfaceIp = TypedDict("InterfaceIp", {"address": str, "netmask": str})
InterfaceIpv6 = TypedDict(
    "InterfaceIpv6", {"address": str, "prefix_length": int, "scope": str}
)

NetworkInterface = TypedDict(
    "NetworkInterface",
    {
        "id": str,
        "ip": "list[InterfaceIp]",
        "ipv6": "list[InterfaceIpv6]",
        "mac": str,
        "type": str,
    },
    total=False,
)


class DsmNetworkDataType(TypedDict, total=False):
    """Data type."""

    dns: list[str]
    gateway: str
    hostname: str
    interfaces: list[NetworkInterface]
    workgroup: str


class SynoDSMNetwork(SynoBaseApi[DsmNetworkDataType]):
    """Class containing Network data."""

    API_KEY = "SYNO.DSM.Network"
    UPDATE_METHOD = "list"

    @property
    def dns(self) -> list[str]:
        """DNS of the NAS."""
        return self._data["dns"]

    @property
    def gateway(self) -> str:
        """Gateway of the NAS."""
        return self._data["gateway"]

    @property
    def hostname(self) -> str:
        """Host name of the NAS."""
        return self._data["hostname"]

    @property
    def interfaces(self) -> list[NetworkInterface]:
        """Interfaces of the NAS."""
        return self._data["interfaces"]

    def interface(self, eth_id: str) -> NetworkInterface | None:
        """Interface of the NAS."""
        for interface in self.interfaces:
            if interface["id"] == eth_id:
                return interface
        return None

    @property
    def macs(self) -> list[str]:
        """List of MACs of the NAS."""
        macs: list[str] = []
        for interface in self.interfaces:
            if (mac := interface.get("mac")) is not None:
                macs.append(mac)
        return macs

    @property
    def workgroup(self) -> str:
        """Workgroup of the NAS."""
        return self._data["workgroup"]
