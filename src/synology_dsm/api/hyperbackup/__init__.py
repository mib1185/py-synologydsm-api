"""Synology HyperBackup API wrapper."""

from __future__ import annotations

from typing import Any, Dict

from synology_dsm.api import SynoBaseApi
from synology_dsm.api.hyperbackup.const import (
    PROP_LAST_BACKUP_ERROR,
    PROP_LAST_BACKUP_PROGRESS,
    PROP_LAST_BACKUP_SUCCESS_TIME,
    PROP_LAST_BACKUP_TIME,
    PROP_LAST_RESULT,
    PROP_NEXT_BACKUP_TIME,
    PROP_ONLINE,
    PROP_PROGRESS,
    PROP_TASKID,
    PROP_USED_SIZE,
)
from synology_dsm.exceptions import SynologyDSMAPIErrorException

from .task import SynoHyperBackupTask


class SynoHyperBackup(SynoBaseApi["dict[int, SynoHyperBackupTask]"]):
    """An implementation of Synology HyperBackup."""

    API_KEY = "SYNO.Backup.Task"
    API_KEY_TARGET = "SYNO.Backup.Target"

    REQUEST_DATA = (
        '["'
        + PROP_LAST_BACKUP_TIME
        + '", "'
        + PROP_LAST_RESULT
        + '", "'
        + PROP_NEXT_BACKUP_TIME
        + '", "'
        + PROP_LAST_BACKUP_PROGRESS
        + '", "'
        + PROP_LAST_BACKUP_ERROR
        + '", "'
        + PROP_LAST_BACKUP_SUCCESS_TIME
        + '"]'
    )
    TARGET_FIELDS = [PROP_ONLINE, PROP_USED_SIZE]
    TARGET_DATA = '["' + PROP_ONLINE + '", "' + PROP_USED_SIZE + '"]'

    async def update(self, get_all_target_data: bool = False) -> None:
        """Update backup tasks settings and information from API."""
        prev_data = self._data
        self._data: dict[int, SynoHyperBackupTask] = {}

        raw_data = await self._dsm.get(self.API_KEY, "list", max_version=1)
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            return

        for task in data.get("task_list", []):
            task_id = task[PROP_TASKID]

            raw_backup_status = await self._dsm.get(
                self.API_KEY,
                "status",
                {PROP_TASKID: task_id, "additional": self.REQUEST_DATA},
                max_version=1,
            )
            if (
                isinstance(raw_backup_status, dict)
                and (backup_status := raw_backup_status.get("data")) is not None
            ):
                task = task | backup_status

            # Keep response cleaner (schedule is a large array)
            task.pop("schedule", None)
            # Keep response cleaner (source can be a large array)
            task.pop("source", None)

            if (progress_raw := task.get(PROP_PROGRESS)) is not None and (
                progress := progress_raw.get(PROP_PROGRESS)
            ) is not None:
                task[PROP_PROGRESS] = progress
            else:
                task[PROP_PROGRESS] = None

            target_data = await self._get_target_data(
                task_id, task, prev_data, get_all_target_data
            )
            task = task | target_data

            if task_id in self._data:
                self._data[task_id].update(task)
            else:
                self._data[task_id] = SynoHyperBackupTask(task)

    async def _get_target_data(
        self,
        task_id: int,
        task: Dict,
        prev_data: dict[int, SynoHyperBackupTask],
        get_all_target_data: bool = False,
    ) -> Dict:
        backup_since_last_update = (
            (task_id not in prev_data)
            or (
                task[PROP_LAST_BACKUP_TIME]
                != prev_data[task_id].get_raw_data.get(PROP_LAST_BACKUP_TIME)
            )
            or not task[PROP_LAST_BACKUP_TIME]
        )
        target_data: dict[str, Any] = {"is_online": False}
        # Target API calls can be expensive (1 - 3+ seconds each),
        # so only get them if there has been a backup.
        if backup_since_last_update or get_all_target_data:
            try:
                target_data_raw = await self._dsm.get(
                    self.API_KEY_TARGET,
                    "get",
                    {PROP_TASKID: task_id, "additional": self.TARGET_DATA},
                    max_version=1,
                )
                if (
                    isinstance(target_data_raw, dict)
                    and (td := target_data_raw.get("data")) is not None
                ):
                    target_data = td
                else:
                    return target_data
            except SynologyDSMAPIErrorException:  # Occurs when target is "offline"
                return target_data
        else:
            # Use previous values for size and target
            target_data = prev_data[task_id].get_raw_data

        return {k: target_data.get(k, None) for k in tuple(self.TARGET_FIELDS)}

    # Tasks

    def get_all_tasks(self) -> list[SynoHyperBackupTask]:
        """Return a list of tasks."""
        return list(self._data.values())

    def get_task(self, task_id: int) -> SynoHyperBackupTask | None:
        """Return task by id."""
        return self._data[task_id]

    @property
    def task_ids(self) -> list[int]:
        """Returns (internal) hyper backup task ids."""
        return list(self._data.keys())

    # Root
    @property
    def get_raw_data(self) -> dict[int, SynoHyperBackupTask]:
        """Gets all external USB storage devices."""
        return self._data
