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

    # Device
    @property
    def device_ids(self):
        """Returns external USB storage device ids."""
        devices = []
        for device in self.get_devices:
            devices.append(device)
        return devices

    def get_device(self, device_id) -> SynoCoreExternalUSBDevice:
        """Returns a specific external USB storage device."""
        return self._data[device_id]


class SynoCoreExternalUSBDevice:
    """A representation of an external USB device."""

    def __init__(self, data):
        """Initialize a external USB device."""
        self._data = data
        for partition_data in data["partitions"]:
            self._data[partition_data["name_id"]] = SynoUSBStoragePartition(
                partition_data
            )

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
        """Total size of theexternal USB storage device."""
        return_data = int(self._data["total_size_mb"])
        return_data = SynoFormatHelper.megabytes_to_bytes(return_data)
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
        partitions = self._data["partitions"]
        device_partitions: list[SynoUSBStoragePartition] = []
        for partition in partitions:
            device_partitions.append(SynoUSBStoragePartition(partition))
        return device_partitions

    @property
    def device_partition_ids(self):
        """Returns partition ids of the external USB storage device."""
        partitions = self._data["partitions", []]
        partition_ids = []
        for partition in partitions:
            partition_ids.append(partition["name_id"])
        return partition_ids

    def get_device_partition(self, partition_id) -> SynoUSBStoragePartition:
        """Returns a partition of the external USB storage device."""
        return self._data[partition_id]

    def partitions_all_size_total(self, human_readable=False):
        """Total size of all parititions of the external USB storage device."""
        partitions = self.device_partitions
        if partitions:
            size_total = 0

            for partition in partitions:
                size_total += partition.partition_size_total(False)

            if human_readable:
                return SynoFormatHelper.bytes_to_readable(size_total)
            return size_total
        return None

    def partitions_all_size_used(self, human_readable=False):
        """Total size used of all partitions of the external USB storage device."""
        partitions = self.device_partitions
        if partitions:
            size_used = 0

            for partition in partitions:
                size_used += partition.partition_size_used(False)

            if human_readable:
                return SynoFormatHelper.bytes_to_readable(size_used)
            return size_used
        return None

    @property
    def partitions_all_percentage_used(self):
        """Used size in percentage for all partitions of the USB storage device."""
        size_total = self.partitions_all_size_total(human_readable=False)
        size_used = self.partitions_all_size_used(human_readable=False)

        if size_used >= 0 and size_total and size_total > 0:
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
        size_total = int(self._data["total_size_mb"])
        size_total = SynoFormatHelper.megabytes_to_bytes(size_total)
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(size_total)
        return size_total

    def partition_size_used(self, human_readable=False):
        """Used size of the partition."""
        size_used = int(self._data["used_size_mb"])
        size_used = SynoFormatHelper.megabytes_to_bytes(size_used)
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(size_used)
        return size_used

    @property
    def partition_percentage_used(self):
        """Used size in percentage of the partition."""
        size_total = self.partition_size_total()
        size_used = self.partition_size_used()

        if size_used >= 0 and size_total and size_total > 0:
            return round((float(size_used) / float(size_total)) * 100.0, 1)
        return None
