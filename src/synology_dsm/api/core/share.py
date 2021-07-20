"""Shared Folders data."""
from __future__ import annotations

from typing import Any

from . import SynoCoreShareType
from synology_dsm import SynologyDSM
from synology_dsm.helpers import SynoFormatHelper


class SynoCoreShare:
    """Class containing Share data."""

    API_KEY = "SYNO.Core.Share"
    # Syno supports two methods to retrieve resource details, GET and POST.
    # GET returns a limited set of keys. With POST the same keys as GET
    # are returned plus any keys listed in the "additional" parameter.
    # NOTE: The value of the additional key must be a string.
    REQUEST_DATA = {
        "additional": '["hidden","encryption","is_aclmode","unite_permission",'
        '"is_support_acl","is_sync_share","is_force_readonly","force_readonly_reason",'
        '"recyclebin","is_share_moving","is_cluster_share","is_exfat_share",'
        '"is_cold_storage_share","support_snapshot","share_quota",'
        '"enable_share_compress","enable_share_cow","include_cold_storage_share",'
        '"is_cold_storage_share"]',
        "shareType": "all",
    }

    def __init__(self, dsm: SynologyDSM) -> None:
        """Constructor method."""
        self._dsm = dsm
        self._data: dict = {}

    def update(self) -> None:
        """Updates share data."""
        raw_data = self._dsm.post(self.API_KEY, "list", data=self.REQUEST_DATA)
        if raw_data:
            self._data = raw_data["data"]

    @property
    def shares(self) -> list[SynoCoreShareType]:
        """Gets all shares."""
        return self._data.get("shares", [])

    @property
    def shares_uuids(self) -> list[str]:
        """Return (internal) share ids."""
        shares = []
        for share in self.shares:
            shares.append(share["uuid"])
        return shares

    def get_share(self, share_uuid: str) -> SynoCoreShareType | dict:
        """Returns a specific share by uuid.."""
        for share in self.shares:
            if share["uuid"] == share_uuid:
                return share
        return {}

    def share_name(self, share_uuid: str) -> str | None:
        """Return the name of this share."""
        return self.get_share(share_uuid).get("name")

    def share_path(self, share_uuid: str) -> str | None:
        """Return the volume path of this share."""
        return self.get_share(share_uuid).get("vol_path")

    def share_recycle_bin(self, share_uuid: str) -> bool | None:
        """Is the recycle bin enabled for this share?"""
        return self.get_share(share_uuid).get("enable_recycle_bin")

    def share_size(
        self, share_uuid: str, human_readable: bool = False
    ) -> str | int | float:
        """Total size of share."""
        share_size_mb = self.get_share(share_uuid).get("share_quota_used")
        # Share size is returned in MB so we convert it.
        share_size_bytes = SynoFormatHelper.megabytes_to_bytes(share_size_mb)
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(share_size_bytes)
        return share_size_bytes
