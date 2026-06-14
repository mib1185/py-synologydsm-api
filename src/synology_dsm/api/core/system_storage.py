"""DSM System Storage data and actions."""

from __future__ import annotations

from typing import TypedDict

from synology_dsm.api import SynoBaseApi
from synology_dsm.helpers import SynoFormatHelper


class SystemStorageDataType(TypedDict, total=False):
    """Synology Storage Data type."""

    vol_info: list[SystemStorageVolume]
    hdd_info: list[SystemStorageDisk]


class SystemStorageVolume(TypedDict, total=False):
    """Synology System Storage Volume."""

    is_encrypted: bool
    name: str
    status: str
    total_size: str
    used_size: str
    vol_desc: str
    volume: str


class SystemStorageDisk(TypedDict, total=False):
    """Synology System Storage Disc."""

    below_remain_life_thr: bool
    device: str
    diskType: str  # noqa: N815
    firm: str
    id: str
    model: str
    name: str
    remain_life_danger: bool
    serial: str
    size_total: int
    smart_status: str
    status: str
    temp: int
    vendor: str


class SynoSystemStorage(SynoBaseApi[SystemStorageDataType]):
    """Class containing System Storage data."""

    API_KEY = "SYNO.Core.System"

    async def update(self) -> None:
        """Updates storage data."""
        raw_data = await self._dsm.get(self.API_KEY, "info", {"type": "storage_v2"})
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return
        self._data = data

    # Root
    @property
    def disks(self) -> list[SystemStorageDisk]:
        """Gets all (internal) disks."""
        return self._data.get("hdd_info", [])

    @property
    def volumes(self) -> list[SystemStorageVolume]:
        """Gets all volumes."""
        return self._data.get("vol_info", [])

    # Disk
    @property
    def disks_ids(self) -> list[str]:
        """Returns (internal) disks ids."""
        disks: list[str] = []
        for disk in self.disks:
            disks.append(disk["id"])
        return disks

    def get_disk(self, disk_id: str) -> SystemStorageDisk | None:
        """Returns a specific disk."""
        for disk in self.disks:
            if disk["id"] == disk_id:
                return disk
        return None

    def disk_below_remain_life_thr(self, disk_id: str) -> bool | None:
        """Checks if disk has fallen below minimum life threshold."""
        if disk := self.get_disk(disk_id):
            return disk.get("below_remain_life_thr")
        return None

    def disk_device(self, disk_id: str) -> str | None:
        """The mount point of this disk."""
        if disk := self.get_disk(disk_id):
            return disk.get("device")
        return None

    def disk_firmware(self, disk_id: str) -> str | None:
        """Returns the firmware version of the disk."""
        if disk := self.get_disk(disk_id):
            return disk.get("firm")
        return None

    def disk_model(self, disk_id: str) -> str | None:
        """Returns the model of the disk."""
        if disk := self.get_disk(disk_id):
            return disk.get("model")
        return None

    def disk_name(self, disk_id: str) -> str | None:
        """The name of this disk."""
        if disk := self.get_disk(disk_id):
            return disk.get("name")
        return None

    def disk_remain_life_danger(self, disk_id: str) -> bool | None:
        """Checks if disk is in remain life danger."""
        if disk := self.get_disk(disk_id):
            return disk.get("remain_life_danger")
        return None

    def disk_serial(self, disk_id: str) -> str | None:
        """Returns the serial number of the disk."""
        if disk := self.get_disk(disk_id):
            return disk.get("serial")
        return None

    def disk_size_total(
        self, disk_id: str, human_readable: bool = False
    ) -> int | str | None:
        """Returns the total size of the disk."""
        if (disk := self.get_disk(disk_id)) is None or (
            size := disk.get("size_total")
        ) is None:
            return None
        return_data = int(size)
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(return_data)
        return return_data

    def disk_smart_status(self, disk_id: str) -> str | None:
        """Status of disk according to S.M.A.R.T)."""
        if disk := self.get_disk(disk_id):
            return disk.get("smart_status")
        return None

    def disk_status(self, disk_id: str) -> str | None:
        """Status of disk."""
        if disk := self.get_disk(disk_id):
            return disk.get("status")
        return None

    def disk_temp(self, disk_id: str) -> int | None:
        """Returns the temperature of the disk."""
        if disk := self.get_disk(disk_id):
            return disk.get("temp")
        return None

    def disk_type(self, disk_id: str) -> str | None:
        """Returns the type of the disk."""
        if disk := self.get_disk(disk_id):
            return disk.get("diskType")
        return None

    def disk_vendor(self, disk_id: str) -> str | None:
        """Returns the vendor of the disk."""
        if disk := self.get_disk(disk_id):
            return disk.get("vendor")
        return None

    # Volume
    @property
    def volumes_names(self) -> list[str]:
        """Returns volumes ids."""
        volumes: list[str] = []
        for volume in self.volumes:
            volumes.append(volume["name"])
        return volumes

    def get_volume(self, volume_name: str) -> SystemStorageVolume | None:
        """Returns a specific volume."""
        for volume in self.volumes:
            if volume["name"] == volume_name:
                return volume
        return None

    def volume_description(self, volume_name: str) -> str | None:
        """Description of the volume."""
        if volume := self.get_volume(volume_name):
            return volume.get("vol_desc")
        return None

    def volume_is_encrypted(self, volume_name: str) -> bool | None:
        """Checks if the volume is encrypted."""
        if volume := self.get_volume(volume_name):
            return bool(volume.get("is_encrypted"))
        return None

    def volume_percentage_used(self, volume_id: str) -> float | None:
        """Total used size in percentage for volume."""
        if (
            (volume := self.get_volume(volume_id)) is None
            or (total_size := volume.get("total_size")) is None
            or (used_size := volume.get("used_size")) is None
        ):
            return None
        total = int(total_size)
        used = int(used_size)
        return round((float(used) / float(total)) * 100.0, 1)

    def volume_size_total(
        self, volume_name: str, human_readable: bool = False
    ) -> int | str | None:
        """Total size of volume."""
        if (volume := self.get_volume(volume_name)) is None or (
            size := volume.get("total_size")
        ) is None:
            return None
        return_data = int(size)
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(return_data)
        return return_data

    def volume_size_used(
        self, volume_id: str, human_readable: bool = False
    ) -> int | str | None:
        """Total used size in volume."""
        if (volume := self.get_volume(volume_id)) is None or (
            size := volume.get("used_size")
        ) is None:
            return None
        return_data = int(size)
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(return_data)
        return return_data

    def volume_status(self, volume_name: str) -> str | None:
        """Status of the volume (normal, degraded, etc)."""
        if volume := self.get_volume(volume_name):
            return volume.get("status")
        return None
