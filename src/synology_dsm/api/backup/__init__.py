"""Synology Backup API models."""
from typing import Any
from typing import Dict

from .const import PROP_TASKID
from .task import SynoBackupTask


class SynoBackup:
    """An implementaion of Synology HyperBackup."""

    API_KEY = "SYNO.Backup.*"
    API_KEY_TASK = "SYNO.Backup.Task"

    def __init__(self, dsm):
        """Initialize HyperBackup."""
        self._dsm = dsm
        self._data = {}

    def update(self):
        """Update backup tasks settings and information from API."""
        self._data = {}
        task_list = self._dsm.get(self.API_KEY_TASK, "list", max_version=1)["data"].get(
            "task_list", []
        )
        for task in task_list:
            backup_task_data = self._dsm.get(
                self.API_KEY_TASK,
                "get",
                {PROP_TASKID: task[PROP_TASKID]},
                max_version=1,
            )["data"]
            self._data[task[PROP_TASKID]] = SynoBackupTask(backup_task_data)

    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Return a list of all tasks."""
        return self._data.values()

    def get_task(self, task_id: int) -> Dict[str, Any]:
        """Return task matching task_id."""
        return self._data[task_id]
