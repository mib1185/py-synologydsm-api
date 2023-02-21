"""DSM external USB device data."""

from __future__ import annotations

from synology_dsm.api import SynoBaseApi
from synology_dsm.helpers import SynoFormatHelper


class SynoCoreExternalUSB(SynoBaseApi):
    """Class for external USB storage devices."""

    API_KEY = "SYNO.Core.ExternalDevice.Storage.USB"
    REQUEST_DATA = {"additional": '["all"]'}

    async def update(self):
        """Updates external USB storage device data."""
        raw_data = await self._dsm.post(self.API_KEY, "list", data=self.REQUEST_DATA)
        if raw_data:
            device_data = raw_data["data"]
            for device in device_data["devices"]:
                self._data[device["dev_id"]] = SynoCoreExternalUSBDevice(device)

    # Root
    @property
    def get_devices(self):
        """Gets all external USB storage devices."""
        return self._data

    def get_device(self, device_id) -> SynoCoreExternalUSBDevice:
        """Returns a specific external USB storage device."""
        return self._data.get(device_id)


class SynoCoreExternalUSBDevice:
    """A representation of an external USB device."""

    def __init__(self, data):
        """Initialize a external USB device."""
        partitions: dict[str, SynoUSBStoragePartition] = {}
        for partition in data["partitions"]:
            partitions[partition["name_id"]] = SynoUSBStoragePartition(partition)
        self._data = {**data, "partitions": partitions}

    @property
    def device_id(self):
        """Return id of the device."""
        return self._data["dev_id"]

    @property
    def device_name(self):
        """The title of the external USB storage device."""
        return self._data["dev_title"]

    @property
    def device_type(self):
        """The type of the external USB storage device."""
        return self._data["dev_type"]

    def device_size_total(self, human_readable=False):
        """Total size of the external USB storage device."""
        return_data = SynoFormatHelper.megabytes_to_bytes(
            int(self._data["total_size_mb"])
        )
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(return_data)
        return return_data

    @property
    def device_status(self):
        """The status of the external USB storage device."""
        return self._data["status"]

    @property
    def device_formatable(self):
        """Whether the external USB storage device can be formatted."""
        return self._data["formatable"]

    @property
    def device_progress(self):
        """The progress the external USB storage device."""
        return self._data["progress"]

    @property
    def device_product_name(self):
        """The product name of the external USB storage device."""
        return self._data["product"]

    @property
    def device_manufacturer(self):
        """The producer name of the external USB storage device."""
        return self._data["producer"]

    # Partition
    @property
    def device_partitions(self) -> list[SynoUSBStoragePartition]:
        """Returns all partitions of the external USB storage device."""
        return self._data["partitions"]

    def get_device_partition(self, partition_id) -> SynoUSBStoragePartition:
        """Returns a partition of the external USB storage device."""
        return self._data["partitions"].get(partition_id)

    def partitions_all_size_total(self, human_readable=False):
        """Total size of all parititions of the external USB storage device."""
        partitions = self._data.get("partitions")
        if not partitions:
            return None

        size_total = 0
        for partition in partitions.values():
            partition_size = partition.partition_size_total()
            # Partitions may be reported without a size
            if partition_size:
                size_total += partition.partition_size_total()

        if human_readable:
            return SynoFormatHelper.bytes_to_readable(size_total)
        return size_total

    def partitions_all_size_used(self, human_readable=False):
        """Total size used of all partitions of the external USB storage device."""
        partitions = self._data.get("partitions")
        if not partitions:
            return None

        size_used = 0
        for partition in partitions.values():
            partition_used = partition.partition_size_used()
            # Partitions may be reported without a size
            if partition_used:
                size_used += partition.partition_size_used()

        if human_readable:
            return SynoFormatHelper.bytes_to_readable(size_used)
        return size_used

    @property
    def partitions_all_percentage_used(self):
        """Used size in percentage for all partitions of the USB storage device."""
        size_total = self.partitions_all_size_total()
        size_used = self.partitions_all_size_used()

        if size_used and size_used >= 0 and size_total and size_total > 0:
            return round((float(size_used) / float(size_total)) * 100.0, 1)
        return None


class SynoUSBStoragePartition:
    """A representation of a parition of an external USB storage device."""

    def __init__(self, data):
        """Initialize a partition object of an external USB storage device."""
        self._data = data

    @property
    def fstype(self):
        """Return the dev_fstype for the partition."""
        return self._data["dev_fstype"]

    @property
    def filesystem(self):
        """Return the filesystem for the partition."""
        return self._data["filesystem"]

    @property
    def name_id(self):
        """Return the name_id for the partition."""
        return self._data["name_id"]

    @property
    def partition_title(self):
        """Return the title for the partition."""
        return self._data["partition_title"]

    @property
    def share_name(self):
        """Return the share name for the partition."""
        return self._data["share_name"]

    @property
    def status(self):
        """Return the status for the partition."""
        return self._data["status"]

    def partition_size_total(self, human_readable=False):
        """Total size of the partition."""
        # API returns property as empty string if a partition has no size
        size_total = self._data.get("total_size_mb")
        if size_total == "":
            return None
        size_total = SynoFormatHelper.megabytes_to_bytes(int(size_total))
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(size_total)
        return size_total

    def partition_size_used(self, human_readable=False):
        """Used size of the partition."""
        # API does not return property if a partition has no size
        size_used = self._data.get("used_size_mb")
        if size_used is None or size_used == "":
            return None
        size_used = SynoFormatHelper.megabytes_to_bytes(int(size_used))
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(size_used)
        return size_used

    @property
    def partition_percentage_used(self):
        """Used size in percentage of the partition."""
        size_total = self.partition_size_total()
        size_used = self.partition_size_used()
        if size_total is None or size_used is None:
            return None

        if size_used and size_used >= 0 and size_total and size_total > 0:
            return round((float(size_used) / float(size_total)) * 100.0, 1)
        return None

    def is_mounted(self):
        """Is the partition formatted."""
        return self._data.get("share_name") != ""

    def is_supported(self):
        """Is the partition formatted."""
        return self._data.get("filesystem") != ""
