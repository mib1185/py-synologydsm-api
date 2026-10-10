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

    async def update(self) -> None:
        """Update network data."""
        await super().update()

        if self.interfaces:
            return

        raw_data = await self._dsm.get(
            "SYNO.Core.System",
            "info",
            {"type": "network"},
            max_version=1,
        )
        if not isinstance(raw_data, dict):
            return

        data = raw_data.get("data")
        if not isinstance(data, dict):
            return

        nif = data.get("nif")
        if not isinstance(nif, list):
            return

        interfaces: list[NetworkInterface] = []

        for item in nif:
            if not isinstance(item, dict):
                continue

            interface_id = item.get("id")
            if not isinstance(interface_id, str):
                continue

            interface: NetworkInterface = {
                "id": interface_id,
                "ipv6": [],
            }

            interface_type = item.get("type")
            if isinstance(interface_type, str):
                interface["type"] = interface_type

            mac = item.get("mac")
            if isinstance(mac, str):
                interface["mac"] = mac

            address = item.get("addr")
            netmask = item.get("mask")
            if isinstance(address, str) and isinstance(netmask, str):
                interface["ip"] = [
                    {
                        "address": address,
                        "netmask": netmask,
                    }
                ]

            interfaces.append(interface)

        if interfaces:
            self._data["interfaces"] = interfaces

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
