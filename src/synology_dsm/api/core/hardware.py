"""DSM hardware data."""

from __future__ import annotations

from enum import StrEnum
from typing import TypedDict

from synology_dsm.api import SynoBaseApi


class FanSpeed(StrEnum):
    """Possible fan speed modes."""

    FULL = "fullfan"
    COOL = "coolfan"
    QUIET = "quietfan"


class HardwareFan(TypedDict):
    """Data type."""

    all_disk_temp_fail: bool
    cool_fan: bool
    dual_fan_speed: FanSpeed
    fan_support_adjust_by_ext_nic: bool
    fan_type: int


class HardwareDataType(TypedDict):
    """Data type."""

    fan_speed: HardwareFan


class SynoCoreHardware(SynoBaseApi[HardwareDataType]):
    """Class containing hardware data and actions."""

    API_KEY = "SYNO.Core.Hardware"
    API_KEY_FANSPEED = f"{API_KEY}.FanSpeed"

    async def update(self) -> None:
        """Updates hardware data."""
        raw_data_fan_speed = await self._dsm.get(self.API_KEY_FANSPEED, "get")
        if (
            isinstance(raw_data_fan_speed, dict)
            and (data := raw_data_fan_speed.get("data")) is not None
        ):
            fan_speed = HardwareFan(
                all_disk_temp_fail=data["all_disk_temp_fail"] == "yes",
                cool_fan=data["cool_fan"] == "yes",
                dual_fan_speed=FanSpeed(data["dual_fan_speed"]),
                fan_support_adjust_by_ext_nic=data["fan_support_adjust_by_ext_nic"]
                == "yes",
                fan_type=data["fan_type"],
            )

            self._data = HardwareDataType(fan_speed=fan_speed)

    @property
    def data(self) -> HardwareDataType:
        """Return system hardware data."""
        return self._data

    @property
    def fan_speed(self) -> FanSpeed:
        """Return current system fan speed mode."""
        return self._data["fan_speed"]["dual_fan_speed"]

    async def set_fan_speed(self, speed: FanSpeed) -> None:
        """Set system fan speed mode."""
        await self._dsm.post(
            self.API_KEY_FANSPEED, "set", {"dual_fan_speed": speed.value}
        )
