"""DSM Storage data."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, TypedDict, cast

from synology_dsm.api import SynoBaseApi
from synology_dsm.exceptions import SynologyDSMAPINoDataException
from synology_dsm.helpers import SynoFormatHelper

if TYPE_CHECKING:
    from synology_dsm import SynologyDSM

SCRUBBING_POOL_STATUS = "background_scrubbing"


class SynoStorageDisk(TypedDict, total=False):
    """Synology Storage Disk."""

    id: str
    name: str
    device: str
    firm: str
    diskType: str  # noqa: N815
    smart_status: str
    status: str
    exceed_bad_sector_thr: bool
    below_remain_life_thr: bool
    temp: int
    model: str
    vendor: str
    size_total: int


class SynoStorageProgress(TypedDict, total=False):
    """Synology Storage progress of a running background task."""

    percent: str  # e.g. "50.72", "-1" when nothing is running
    step: str
    remaining_time: int  # seconds, 0 when DSM has no estimate
    cur_step: int
    total_step: int
    is_resync_speed_limited: bool


SynoStoragePoolChild = TypedDict(
    "SynoStoragePoolChild", {"id": str, "size": dict}, total=False
)


class SynoStoragePool(TypedDict, total=False):
    """Synology Storage Pool."""

    id: str
    deploy_path: str
    disks: list[str]
    pool_child: list[SynoStoragePoolChild]
    progress: SynoStorageProgress
    scrubbingStatus: str  # noqa: N815
    status: str


SynoStorageVolumeSize = TypedDict(
    "SynoStorageVolumeSize",
    {
        "free_inode": str,
        "total": str,
        "total_device": str,
        "total_inode": str,
        "used": str,
    },
)


class SynoStorageVolume(TypedDict, total=False):
    """Synology Storage Volume."""

    id: str
    device_type: str
    size: SynoStorageVolumeSize
    status: str
    fs_type: str
    pool_path: str


class StorageDataType(TypedDict, total=False):
    """Synology Storage Data type."""

    disks: list[SynoStorageDisk]
    env: dict
    storagePools: list[SynoStoragePool]  # noqa: N815
    volumes: list[SynoStorageVolume]


class SynoStorage(SynoBaseApi[StorageDataType]):
    """Class containing Storage data."""

    API_KEY = "SYNO.Storage.CGI.Storage"

    def __init__(self, dsm: SynologyDSM) -> None:
        """Constructor method."""
        super().__init__(dsm)
        # pool id -> (monotonic time, percent) of the first sample seen
        # for the running scrub, used to estimate the remaining time.
        self._scrub_start: dict[str, tuple[float, float]] = {}
        self._scrub_last: dict[str, tuple[float, float]] = {}

    async def update(self) -> None:
        """Updates storage data."""
        raw_data = await self._dsm.get(self.API_KEY, "load_info")
        if isinstance(raw_data, dict):
            if (data := raw_data.get("data")) is not None:
                self._data = data
            elif "disks" in raw_data:
                self._data = cast(StorageDataType, raw_data)
            else:
                raise SynologyDSMAPINoDataException(self.API_KEY)
        else:
            raise SynologyDSMAPINoDataException(self.API_KEY)
        self._track_scrubbing()

    def _track_scrubbing(self) -> None:
        """Record scrubbing progress samples to estimate remaining time."""
        now = time.monotonic()
        running: set[str] = set()
        for pool in self.storage_pools:
            pool_id = pool.get("id")
            if pool_id is None:
                continue
            percent = self.pool_scrubbing_percentage(pool_id)
            if percent is None:
                continue
            running.add(pool_id)
            last = self._scrub_last.get(pool_id)
            if pool_id not in self._scrub_start or (last and percent < last[1]):
                # new scrub, or progress went backwards (restarted)
                self._scrub_start[pool_id] = (now, percent)
            if last is None or percent != last[1]:
                self._scrub_last[pool_id] = (now, percent)
        for pool_id in set(self._scrub_start) - running:
            self._scrub_start.pop(pool_id, None)
            self._scrub_last.pop(pool_id, None)

    # Root
    @property
    def disks(self) -> list[SynoStorageDisk]:
        """Gets all (internal) disks."""
        return self._data.get("disks", [])

    @property
    def env(self) -> dict | None:
        """Gets storage env."""
        return self._data.get("env")

    @property
    def storage_pools(self) -> list[SynoStoragePool]:
        """Gets all storage pools."""
        return self._data.get("storagePools", [])

    @property
    def volumes(self) -> list[SynoStorageVolume]:
        """Gets all volumes."""
        return self._data.get("volumes", [])

    # Volume
    @property
    def volumes_ids(self) -> list[str]:
        """Returns volumes ids."""
        volumes: list[str] = []
        for volume in self.volumes:
            volumes.append(volume["id"])
        return volumes

    def get_volume(self, volume_id: str) -> SynoStorageVolume | None:
        """Returns a specific volume."""
        for volume in self.volumes:
            if volume["id"] == volume_id:
                return volume
        return None

    def volume_status(self, volume_id: str) -> str | None:
        """Status of the volume (normal, degraded, etc)."""
        if volume := self.get_volume(volume_id):
            return volume.get("status")
        return None

    def volume_device_type(self, volume_id: str) -> str | None:
        """Returns the volume type (RAID1, RAID2, etc)."""
        if volume := self.get_volume(volume_id):
            return volume.get("device_type")
        return None

    def volume_size_total(
        self, volume_id: str, human_readable: bool = False
    ) -> int | str | None:
        """Total size of volume."""
        if (volume := self.get_volume(volume_id)) is None or (
            size := volume.get("size")
        ) is None:
            return None
        return_data = int(size["total"])
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(return_data)
        return return_data

    def volume_size_used(
        self, volume_id: str, human_readable: bool = False
    ) -> int | str | None:
        """Total used size in volume."""
        if (volume := self.get_volume(volume_id)) is None or (
            size := volume.get("size")
        ) is None:
            return None
        return_data = int(size["used"])
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(return_data)
        return return_data

    def volume_percentage_used(self, volume_id: str) -> float | None:
        """Total used size in percentage for volume."""
        if (volume := self.get_volume(volume_id)) is None or (
            size := volume.get("size")
        ) is None:
            return None
        total = int(size["total"])
        used = int(size["used"])
        return round((float(used) / float(total)) * 100.0, 1)

    def volume_disk_temp_avg(self, volume_id: str) -> float | None:
        """Average temperature of all disks making up the volume."""
        total_temp = 0
        total_disks = 0
        disks = self._get_disks_for_volume(volume_id)
        for disk in disks:
            if disk_temp := self.disk_temp(disk["id"]):
                total_disks += 1
                total_temp += disk_temp

        if total_temp > 0 and total_disks > 0:
            return round(total_temp / total_disks, 0)
        return None

    def volume_disk_temp_max(self, volume_id: str) -> int | None:
        """Maximum temperature of all disks making up the volume."""
        disks = self._get_disks_for_volume(volume_id)
        if not disks:
            return None

        disk_temps: list[int] = [0]
        for disk in disks:
            if disk_temp := self.disk_temp(disk["id"]):
                disk_temps.append(disk_temp)
        return max(disk_temps)

    def volume_is_scrubbing(self, volume_id: str) -> bool | None:
        """Checks if the storage pool of the volume is being scrubbed."""
        if pool := self._get_pool_for_volume(volume_id):
            return self.pool_is_scrubbing(pool["id"])
        return None

    def volume_scrubbing_percentage(self, volume_id: str) -> float | None:
        """Scrubbing progress in percent of the volume's storage pool."""
        if pool := self._get_pool_for_volume(volume_id):
            return self.pool_scrubbing_percentage(pool["id"])
        return None

    def volume_scrubbing_remaining_time(self, volume_id: str) -> int | None:
        """Estimated remaining scrubbing time (seconds) of the volume's pool."""
        if pool := self._get_pool_for_volume(volume_id):
            return self.pool_scrubbing_remaining_time(pool["id"])
        return None

    def _get_pool_for_volume(self, volume_id: str) -> SynoStoragePool | None:
        """Returns the storage pool a volume is located on."""
        volume = self.get_volume(volume_id)
        if volume and (pool_path := volume.get("pool_path")):
            if pool := self.get_storage_pool(pool_path):
                return pool
        for pool in self.storage_pools:
            if pool.get("deploy_path") == volume_id:
                return pool
            for pool_child in pool.get("pool_child", []):
                if pool_child.get("id") == volume_id:
                    return pool
        return None

    # Storage pool
    @property
    def storage_pools_ids(self) -> list[str]:
        """Returns storage pools ids."""
        return [pool["id"] for pool in self.storage_pools if "id" in pool]

    def get_storage_pool(self, pool_id: str) -> SynoStoragePool | None:
        """Returns a specific storage pool."""
        for pool in self.storage_pools:
            if pool.get("id") == pool_id:
                return pool
        return None

    def pool_status(self, pool_id: str) -> str | None:
        """Status of the storage pool (normal, background_scrubbing, etc)."""
        if pool := self.get_storage_pool(pool_id):
            return pool.get("status")
        return None

    def pool_is_scrubbing(self, pool_id: str) -> bool | None:
        """Checks if a data scrubbing is currently running on the pool."""
        if (pool := self.get_storage_pool(pool_id)) is None:
            return None
        return pool.get("status") == SCRUBBING_POOL_STATUS or pool.get(
            "scrubbingStatus", ""
        ).endswith("_running")

    def pool_scrubbing_percentage(self, pool_id: str) -> float | None:
        """Data scrubbing progress in percent, None if not scrubbing."""
        if not self.pool_is_scrubbing(pool_id):
            return None
        pool = cast(SynoStoragePool, self.get_storage_pool(pool_id))
        try:
            percent = float(pool.get("progress", {}).get("percent", -1))
        except (TypeError, ValueError):
            return 0.0
        # DSM reports -1 until the scrub has made measurable progress
        return round(min(max(percent, 0.0), 100.0), 2)

    def pool_scrubbing_remaining_time(self, pool_id: str) -> int | None:
        """Estimated remaining data scrubbing time in seconds.

        Uses the remaining time reported by DSM when available. DSM usually
        reports 0 while scrubbing, so otherwise the time is estimated from
        the progress observed across calls of update(). Returns None when
        not scrubbing or when there is not enough data for an estimate yet.
        """
        if (percent := self.pool_scrubbing_percentage(pool_id)) is None:
            return None
        pool = cast(SynoStoragePool, self.get_storage_pool(pool_id))
        try:
            remaining = int(pool.get("progress", {}).get("remaining_time", 0))
        except (TypeError, ValueError):
            remaining = 0
        if remaining > 0:
            return remaining

        start = self._scrub_start.get(pool_id)
        last = self._scrub_last.get(pool_id)
        if not start or not last or last[0] <= start[0]:
            return None
        rate = (last[1] - start[1]) / (last[0] - start[0])  # percent / second
        if rate <= 0:
            return None
        return round((100.0 - percent) / rate)

    # Disk
    @property
    def disks_ids(self) -> list[str]:
        """Returns (internal) disks ids."""
        disks: list[str] = []
        for disk in self.disks:
            disks.append(disk["id"])
        return disks

    def get_disk(self, disk_id: str) -> SynoStorageDisk | None:
        """Returns a specific disk."""
        for disk in self.disks:
            if disk["id"] == disk_id:
                return disk
        return None

    def _get_disks_for_volume(self, volume_id: str) -> list[SynoStorageDisk]:
        """Returns a list of disk for a specific volume."""
        disks: list[SynoStorageDisk] = []
        for pool in self.storage_pools:
            if pool.get("deploy_path") == volume_id:
                # RAID disk redundancy
                for disk_id in pool["disks"]:
                    if disk := self.get_disk(disk_id):
                        disks.append(disk)

            if pool.get("pool_child"):
                # SHR disk redundancy
                for pool_child in pool["pool_child"]:
                    if pool_child["id"] != volume_id:
                        continue
                    for disk_id in pool["disks"]:
                        if disk := self.get_disk(disk_id):
                            disks.append(disk)

        return disks

    def disk_name(self, disk_id: str) -> str | None:
        """The name of this disk."""
        if disk := self.get_disk(disk_id):
            return disk.get("name")
        return None

    def disk_device(self, disk_id: str) -> str | None:
        """The mount point of this disk."""
        if disk := self.get_disk(disk_id):
            return disk.get("device")
        return None

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

    def disk_exceed_bad_sector_thr(self, disk_id: str) -> bool | None:
        """Checks if disk has exceeded maximum bad sector threshold."""
        if disk := self.get_disk(disk_id):
            return disk.get("exceed_bad_sector_thr")
        return None

    def disk_below_remain_life_thr(self, disk_id: str) -> bool | None:
        """Checks if disk has fallen below minimum life threshold."""
        if disk := self.get_disk(disk_id):
            return disk.get("below_remain_life_thr")
        return None

    def disk_temp(self, disk_id: str) -> int | None:
        """Returns the temperature of the disk."""
        if disk := self.get_disk(disk_id):
            return disk.get("temp")
        return None
