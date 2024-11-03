"""Synology Virtual Machine Manager API models."""

from __future__ import annotations

from synology_dsm.api import SynoBaseApi

from .guest import SynoVmmGuest


class SynoVirtualMachineManager(SynoBaseApi["dict[str, SynoVmmGuest]"]):
    """Class containing Virtual Machine Guests."""

    API_KEY = "SYNO.Virtualization.*"
    GUEST_API_KEY = "SYNO.Virtualization.Guest"
    ACTION_API_KEY = "SYNO.Virtualization.Guest.Action"

    async def update(self) -> None:
        """Updates Virtual Machine Manager data."""
        raw_data = await self._dsm.get(self.GUEST_API_KEY, "list")
        print(raw_data)
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return

        for guest in data["guests"]:
            if guest["guest_id"] in self._data:
                self._data[guest["guest_id"]].update(guest)
            else:
                self._data[guest["guest_id"]] = SynoVmmGuest(guest)

    def get_all_guests(self) -> list[SynoVmmGuest]:
        """Return a list of all vmm guests."""
        return list(self._data.values())

    def get_guest(self, guest_id: str) -> SynoVmmGuest | None:
        """Return vmm guest by guest_id."""
        return self._data.get(guest_id)

    async def _guest_action(self, guest_id: str, action: str) -> bool | None:
        raw_data = await self._dsm.post(
            self.ACTION_API_KEY,
            "pwr_ctl",
            {
                "guest_id": guest_id,
                "action": action,
            },
        )
        if (
            isinstance(raw_data, dict)
            and (result := raw_data.get("success")) is not None
        ):
            return bool(result)
        return None

    async def guest_poweron(self, guest_id: str) -> bool | None:
        """Power on a vmm guest."""
        return await self._guest_action(guest_id, "poweron")

    async def guest_poweroff(self, guest_id: str) -> bool | None:
        """Power off a vmm guest."""
        return await self._guest_action(guest_id, "poweroff")

    async def guest_shutdown(self, guest_id: str) -> bool | None:
        """Graceful shutdown a vmm guest."""
        return await self._guest_action(guest_id, "shutdown")

    async def guest_restart(self, guest_id: str) -> bool | None:
        """Graceful restart a vmm guest."""
        return await self._guest_action(guest_id, "reboot")
