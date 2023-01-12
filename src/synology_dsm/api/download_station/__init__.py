"""Synology DownloadStation API wrapper."""
from synology_dsm.api import SynoBaseApi

from .task import SynoDownloadTask


class SynoDownloadStation(SynoBaseApi):
    """An implementation of a Synology DownloadStation."""

    API_KEY = "SYNO.DownloadStation.*"
    INFO_API_KEY = "SYNO.DownloadStation.Info"
    STAT_API_KEY = "SYNO.DownloadStation.Statistic"
    TASK_API_KEY = "SYNO.DownloadStation.Task"
    REQUEST_DATA = {
        "additional": "detail,file"
    }  # Can contain: detail, transfer, file, tracker, peer

    async def update(self):
        """Update tasks from API."""
        self._data = {}
        raw_data = await self._dsm.get(self.TASK_API_KEY, "List", self.REQUEST_DATA)
        list_data = raw_data["data"]
        for task_data in list_data["tasks"]:
            if task_data["id"] in self._data:
                self._data[task_data["id"]].update(task_data)
            else:
                self._data[task_data["id"]] = SynoDownloadTask(task_data)

    # Global
    async def get_info(self):
        """Return general informations about the Download Station instance."""
        return await self._dsm.get(self.INFO_API_KEY, "GetInfo")

    async def get_config(self):
        """Return configuration about the Download Station instance."""
        return await self._dsm.get(self.INFO_API_KEY, "GetConfig")

    async def get_stat(self):
        """Return statistic about the Download Station instance."""
        return await self._dsm.get(self.STAT_API_KEY, "GetInfo")

    # Downloads
    def get_all_tasks(self):
        """Return a list of tasks."""
        return self._data.values()

    def get_task(self, task_id):
        """Return task matching task_id."""
        return self._data[task_id]

    def create(self, uri, unzip_password=None, destination=None):
        """Create a new task (uri accepts HTTP/FTP/magnet/ED2K links)."""
        res = self._dsm.post(
            self.TASK_API_KEY,
            "Create",
            {
                "uri": ",".join(uri) if isinstance(uri, list) else uri,
                "unzip_password": unzip_password,
                "destination": destination,
            },
        )
        self.update()
        return res

    async def pause(self, task_id):
        """Pause a download task."""
        res = await self._dsm.get(
            self.TASK_API_KEY,
            "Pause",
            {"id": ",".join(task_id) if isinstance(task_id, list) else task_id},
        )
        await self.update()
        return res

    async def resume(self, task_id):
        """Resume a paused download task."""
        res = await self._dsm.get(
            self.TASK_API_KEY,
            "Resume",
            {"id": ",".join(task_id) if isinstance(task_id, list) else task_id},
        )
        await self.update()
        return res

    async def delete(self, task_id, force_complete=False):
        """Delete a download task."""
        res = await self._dsm.get(
            self.TASK_API_KEY,
            "Delete",
            {
                "id": ",".join(task_id) if isinstance(task_id, list) else task_id,
                "force_complete": force_complete,
            },
        )
        await self.update()
        return res
