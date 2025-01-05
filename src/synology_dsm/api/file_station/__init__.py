"""Synology FileStation API wrapper."""

from __future__ import annotations

from collections.abc import AsyncIterator
from io import BufferedReader

from synology_dsm.api import SynoBaseApi

from .models import (
    SynoFileAdditionalOwner,
    SynoFileAdditionalPermission,
    SynoFileAdditionalTime,
    SynoFileAdditionalVolumeStatus,
    SynoFileFile,
    SynoFileFileAdditional,
    SynoFileSharedFolder,
    SynoFileSharedFolderAdditional,
)


class SynoFileStation(SynoBaseApi):
    """An implementation of a Synology FileStation."""

    API_KEY = "SYNO.FileStation.*"
    LIST_API_KEY = "SYNO.FileStation.List"
    DOWNLOAD_API_KEY = "SYNO.FileStation.Download"
    UPLOAD_API_KEY = "SYNO.FileStation.Upload"

    async def get_shared_folders(
        self, offset: int = 0, limit: int = 100, only_writable: bool = False
    ) -> list[SynoFileSharedFolder] | None:
        """Get a list of all shared folders."""
        raw_data = await self._dsm.get(
            self.LIST_API_KEY,
            "list_share",
            {
                "offset": offset,
                "limit": limit,
                "onlywritable": only_writable,
                "additional": (
                    '["real_path","owner","time","perm",'
                    '"mount_point_type","sync_share","volume_status"]'
                ),
            },
        )
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return None

        shared_folders: list[SynoFileSharedFolder] = []
        for folder in data["shares"]:
            additional = folder["additional"]
            shared_folders.append(
                SynoFileSharedFolder(
                    SynoFileSharedFolderAdditional(
                        additional["mount_point_type"],
                        SynoFileAdditionalOwner(**additional["owner"]),
                        SynoFileAdditionalPermission(**additional["perm"]),
                        SynoFileAdditionalVolumeStatus(
                            **additional["volume_status"],
                        ),
                    ),
                    folder["isdir"],
                    folder["name"],
                    folder["path"],
                )
            )

        return shared_folders

    async def get_files(
        self, path: str, offset: int = 0, limit: int = 100
    ) -> list[SynoFileFile] | None:
        """Get a list of all files in a folder."""
        raw_data = await self._dsm.get(
            self.LIST_API_KEY,
            "list",
            {
                "offset": offset,
                "limit": limit,
                "folder_path": path,
                "additional": (
                    '["real_path","owner","time","perm",'
                    '"mount_point_type","type","size"]'
                ),
            },
        )
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return None

        files: list[SynoFileFile] = []
        for file in data["files"]:
            additional = file["additional"]
            files.append(
                SynoFileFile(
                    SynoFileFileAdditional(
                        additional["mount_point_type"],
                        SynoFileAdditionalOwner(**additional["owner"]),
                        SynoFileAdditionalPermission(**additional["perm"]),
                        additional["real_path"],
                        additional["size"],
                        SynoFileAdditionalTime(**additional["time"]),
                        additional["type"],
                    ),
                    file["isdir"],
                    file["name"],
                    file["path"],
                )
            )

        return files

    async def upload_files(
        self,
        path: str,
        filename: str,
        content: bytes | BufferedReader | AsyncIterator[bytes],
    ) -> bool | None:
        """Upload a file to a folder."""
        raw_data = await self._dsm.post(
            self.UPLOAD_API_KEY, "upload", path=path, filename=filename, content=content
        )
        if not isinstance(raw_data, dict):
            return None
        return raw_data.get("success")
