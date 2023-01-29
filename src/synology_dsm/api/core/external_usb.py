"""DSM Storage data."""
from synology_dsm.api import SynoBaseApi
from synology_dsm.helpers import SynoFormatHelper


class SynoCoreExternalUSB(SynoBaseApi):
    """Class containing external USB storage data."""

    API_KEY = "SYNO.Core.ExternalDevice.Storage.USB"
    REQUEST_DATA = {"additional": '["all"]'}

    async def update(self):
        """Updates external USB storage data."""
        raw_data = await self._dsm.post(self.API_KEY, "list", data=self.REQUEST_DATA)
        if raw_data:
            self._data = raw_data
            if raw_data.get("data"):
                self._data = raw_data["data"]

    # Root
    @property
    def devices(self):
        """Gets all external USB storage devices."""
        return self._data.get("devices", [])

    # Device
    @property
    def device_ids(self):
        """Returns external USB storage device ids."""
        devices = []
        for device in self.devices:
            devices.append(device["dev_id"])
        return devices

    def get_device(self, device_id):
        """Returns a specific device."""
        for device in self.devices:
            if device["dev_id"] == device_id:
                return device
        return {}

    def device_name(self, device_id):
        """The title of this device."""
        return self.get_device(device_id).get("dev_title")

    def device_type(self, device_id):
        """The type of this device."""
        return self.get_device(device_id).get("dev_type")

    def device_total_size(self, device_id, human_readable=False):
        """Total size of the device."""
        return_data = int(self.get_device(device_id).get("total_size_mb"))
        return_data = SynoFormatHelper.megabytes_to_bytes(return_data)
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(return_data)
        return return_data

    def device_status(self, device_id):
        """The status of this device."""
        return self.get_device(device_id).get("status")

    def device_formatable(self, device_id):
        """Whether the device is able to be formatted."""
        return self.get_device(device_id).get("formatable")

    def device_progress(self, device_id):
        """The progress this device."""
        return self.get_device(device_id).get("progress")

    def product_name(self, device_id):
        """The product name of this device."""
        return self.get_device(device_id).get("product")

    def producer(self, device_id):
        """The producer name of this device."""
        return self.get_device(device_id).get("producer")

    # Partition
    def device_partitions(self, device_id):
        """Returns partitions of a device."""
        partitions = self.get_device(device_id).get("partitions", [])
        device_partitions = []
        for partition in partitions:
            device_partitions.append((partition))
        return device_partitions

    def device_partition_ids(self, device_id):
        """Returns partition ids of a device."""
        partitions = self.get_device(device_id).get("partitions", [])
        partition_ids = []
        for partition in partitions:
            partition_ids.append(partition["name_id"])
        return partition_ids

    def device_partition(self, device_id, partition_id):
        """Partition of a device."""
        # partitions = self.device_partitions(device_id)
        for partition in self.device_partitions(device_id):
            if partition["name_id"] == partition_id:
                return SynoUSBStoragePartition(partition)
        return None

    def partitions_size_total(self, device_id, human_readable=False):
        """Total size of all parititions."""
        partitions = self.device_partitions(device_id)
        if partitions:
            total_size = 0

            for partition in partitions:
                partition = SynoUSBStoragePartition(partition)
                total_size += partition.partition_size_total(False)

            if human_readable:
                return SynoFormatHelper.bytes_to_readable(total_size)
            return total_size
        return None

    def partitions_used_total(self, device_id, human_readable=False):
        """Total used size of all partitions."""
        partitions = self.device_partitions(device_id)
        if partitions:
            total_used = 0

            for partition in partitions:
                partition = SynoUSBStoragePartition(partition)
                total_used += partition.partition_size_used(False)

            if human_readable:
                return SynoFormatHelper.bytes_to_readable(total_used)
            return total_used
        return None

    def partitions_percentage_used_total(self, device_id):
        """Used size in percentage for all partitions."""
        total = self.partitions_size_total(device_id, human_readable=False)
        used = self.partitions_used_total(device_id, human_readable=False)

        if used >= 0 and total and total > 0:
            return round((float(used) / float(total)) * 100.0, 1)
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
        return_data = int(self._data["total_size_mb"])
        return_data = SynoFormatHelper.megabytes_to_bytes(return_data)
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(return_data)
        return return_data

    def partition_size_used(self, human_readable=False):
        """Used size of the partition."""
        return_data = int(self._data["used_size_mb"])
        return_data = SynoFormatHelper.megabytes_to_bytes(return_data)
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(return_data)
        return return_data

    @property
    def partition_percentage_used(self):
        """Used size in percentage of the partition."""
        total = self.partition_size_total()
        used = self.partition_size_used()

        if used >= 0 and total and total > 0:
            return round((float(used) / float(total)) * 100.0, 1)
        return None
