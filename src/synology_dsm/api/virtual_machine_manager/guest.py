"""VirtualMachineManager guest."""

from __future__ import annotations

from typing import TypedDict, Union

SynoVmmGuestData = TypedDict(
    "SynoVmmGuestData",
    {
        "autorun": int,
        "desc": str,
        "guest_id": str,
        "name": str,
        "ram_used": int,
        "status": str,
        "vcpu_num": int,
        "vcpu_usage": Union[str, int],  # empty str when offline
        "vram_size": int,
    },
    total=False,
)


class SynoVmmGuest:
    """An representation of a Synology Virtual Machine Manager guest."""

    def __init__(self, data: SynoVmmGuestData) -> None:
        """Initialize a Virtual Machine Manager guest."""
        self._data: SynoVmmGuestData = data

    def update(self, data: SynoVmmGuestData) -> None:
        """Update the vmm guest."""
        self._data = data

    @property
    def autorun(self) -> bool:
        """Return autorun of the vmm guest."""
        return bool(self._data["autorun"])

    @property
    def description(self) -> str:
        """Return description of the vmm guest."""
        return self._data["desc"]

    @property
    def guest_id(self) -> str:
        """Return guest_id of the vmm guest."""
        return self._data["guest_id"]

    @property
    def name(self) -> str:
        """Return name of the vmm guest."""
        return self._data["name"]

    @property
    def status(self) -> str:
        """Return status of the vmm guest."""
        return self._data["status"]

    @property
    def host_cpu_usage(self) -> int:
        """Return host cpu usage in one thousandth of the vmm guest."""
        if isinstance(self._data["vcpu_usage"], str):
            return 0
        return self._data["vcpu_usage"]

    @property
    def host_ram_usage(self) -> int:
        """Return host ram usage in KiByte of the vmm guest."""
        return self._data["ram_used"]

    @property
    def vcpu_num(self) -> int:
        """Return number of vcpu of the vmm guest."""
        return self._data["vcpu_num"]

    @property
    def vram_size(self) -> int:
        """Return size of vram in KiByte of the vmm guest."""
        return self._data["vram_size"]
