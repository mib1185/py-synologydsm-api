"""Synology FileStation API wrapper."""

from __future__ import annotations

from collections.abc import AsyncIterator
from io import BufferedReader

import aiofiles
from aiohttp import StreamReader

from synology_dsm.api import SynoBaseApi

from .models import (
    SynoFileAdditionalOwner,
    SynoFileFile,
    SynoFileFileAdditional,
    SynoFileFileAdditionalPermission,
    SynoFileFileAdditionalTime,
    SynoFileSharedFolder,
    SynoFileSharedFolderAdditional,
    SynoFileSharedFolderAdditionalPermission,
    SynoFileSharedFolderAdditionalVolumeStatus,
)


class SynoFileStation(SynoBaseApi):
    """An implementation of a Synology FileStation."""

    API_KEY = "SYNO.FileStation.*"
    LIST_API_KEY = "SYNO.FileStation.List"
    DOWNLOAD_API_KEY = "SYNO.FileStation.Download"
    UPLOAD_API_KEY = "SYNO.FileStation.Upload"
    DELETE_API_KEY = "SYNO.FileStation.Delete"

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
            if (additional := folder.get("additional")) is not None:
                shared_folders.append(
                    SynoFileSharedFolder(
                        SynoFileSharedFolderAdditional(
                            additional["mount_point_type"],
                            SynoFileAdditionalOwner(**additional["owner"]),
                            SynoFileSharedFolderAdditionalPermission(
                                **additional["perm"]
                            ),
                            SynoFileSharedFolderAdditionalVolumeStatus(
                                **additional["volume_status"],
                            ),
                        ),
                        folder["isdir"],
                        folder["name"],
                        folder["path"],
                    )
                )
            else:
                shared_folders.append(
                    SynoFileSharedFolder(
                        None, folder["isdir"], folder["name"], folder["path"]
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
            if (additional := file.get("additional")) is not None:
                files.append(
                    SynoFileFile(
                        SynoFileFileAdditional(
                            additional["mount_point_type"],
                            SynoFileAdditionalOwner(**additional["owner"]),
                            SynoFileFileAdditionalPermission(**additional["perm"]),
                            additional["real_path"],
                            additional["size"],
                            SynoFileFileAdditionalTime(**additional["time"]),
                            additional["type"],
                        ),
                        file["isdir"],
                        file["name"],
                        file["path"],
                    )
                )
            else:
                files.append(
                    SynoFileFile(None, file["isdir"], file["name"], file["path"])
                )

        return files

    async def upload_file(
        self,
        path: str,
        filename: str,
        source: bytes | BufferedReader | AsyncIterator[bytes] | str,
        create_parents: bool = False,
    ) -> bool | None:
        """Upload a file to a folder from eather a local source_file or content."""
        if isinstance(source, str):
            source = open(source, "rb")

        raw_data = await self._dsm.post(
            self.UPLOAD_API_KEY,
            "upload",
            path=path,
            filename=filename,
            content=source,
            create_parents=create_parents,
        )
        if not isinstance(raw_data, dict):
            return None
        return raw_data.get("success")

    async def download_file(
        self, path: str, filename: str, target_file: str | None = None
    ) -> StreamReader | bool | None:
        """Download a file to local target_file or returns an async StreamReader."""
        response_content = await self._dsm.get(
            self.DOWNLOAD_API_KEY,
            "download",
            {"path": f"{path}/{filename}", "mode": "download"},
            raw_response_content=True,
        )
        if not isinstance(response_content, StreamReader):
            return None

        if target_file:
            async with aiofiles.open(target_file, "wb") as fh:
                async for data, _ in response_content.iter_chunks():
                    await fh.write(data)
            return True

        return response_content

    async def delete_file(self, path: str, filename: str) -> bool | None:
        """Delete a file."""
        raw_data = await self._dsm.get(
            self.DELETE_API_KEY,
            "delete",
            {"path": f"{path}/{filename}", "recursive": False},
        )
        if not isinstance(raw_data, dict):
            return None
        return raw_data.get("success")
