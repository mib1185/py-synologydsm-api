"""HyperBackup task."""

from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict

from synology_dsm.api.hyperbackup.const import (
    HEALTH_CRIT,
    HEALTH_GOOD,
    HEALTH_WARN,
    PROP_STATUS_BACKUP,
    PROP_STATUS_DETECT,
    PROP_STATUS_DETECT_WAIT,
    PROP_STATUS_NONE,
    PROP_STATUS_PREP_VER_DEL,
    PROP_STATUS_VER_DEL,
    PROP_STATUS_WAITING,
    RESULT_DONE,
    RESULT_NONE,
    RESULT_RESUME,
    RESULT_SUSPEND,
    STATE_BACKUP,
    STATE_BROKEN,
    STATE_END_SERVICE,
    STATE_ERROR,
    STATE_RESTORE_ONLY,
    STATE_UNAUTH,
    STATUS_DETECT,
    STATUS_ERROR,
    STATUS_NEVER_RUN,
    STATUS_NO_SCHEDULE,
    STATUS_OK,
    STATUS_RESTORE_ONLY,
    STATUS_RESUMING,
    STATUS_RUNNING,
    STATUS_RUNNING_NO_SCHEDULE,
    STATUS_SUSPENDED,
    STATUS_UNKNOWN,
    STATUS_WAITING,
)
from synology_dsm.helpers import SynoFormatHelper

SynoHyperBackupTaskType = TypedDict(
    "SynoHyperBackupTaskType",
    {
        "name": str,
        "task_id": int,
        "data_type": str,
        "repo_id": int,
        "state": str,
        "status": str,
        "target_id": str,
        "target_type": str,
        "transfer_type": str,
        "type": str,
        "last_bkp_end_time": str,
        "last_bkp_error": str,
        "last_bkp_error_code": int,
        "last_bkp_progress": int,
        "last_bkp_result": str,
        "last_bkp_success_time": str,
        "last_bkp_time": str,
        "next_bkp_time": str,
        "is_online": bool,
        "used_size": int,
        "progress": int,
    },
    total=False,
)


class SynoHyperBackupTask:
    """An representation of a Synology HyperBackup task."""

    def __init__(self, data: SynoHyperBackupTaskType) -> None:
        """Initialize a HyperBackup task."""
        self._data: SynoHyperBackupTaskType = data

    def update(self, data: SynoHyperBackupTaskType) -> None:
        """Update the task."""
        self._data = data

    @property
    def task_id(self) -> int | None:
        """Return id of the task."""
        return self._data.get("task_id")

    @property
    def name(self) -> str | None:
        """Return name of the task."""
        return self._data.get("name")

    @property
    def target_online(self) -> bool:
        """Return target online status."""
        return bool(self._data.get("is_online"))

    @property
    def status(self) -> str:
        """Return status.

        An 'OK' status requires state=backupable &&
        status=None && result=done && next_backup not null.
        """
        raw_status = self.raw_status
        state = self.state
        previous_result = self.previous_result

        # Check state value first
        if state != STATE_BACKUP:
            if state == STATE_RESTORE_ONLY:
                return STATUS_RESTORE_ONLY  # Not backup-able, but can restore
            if state == STATE_ERROR and raw_status == PROP_STATUS_DETECT_WAIT:
                return STATUS_DETECT
            if state in [STATE_ERROR, STATE_BROKEN, STATE_UNAUTH, STATE_END_SERVICE]:
                return STATUS_ERROR
            # TODO: Research relink/import/export backup tasks # pylint: disable=W0511
            return STATUS_UNKNOWN

        # Then check status value and previous result
        if raw_status == PROP_STATUS_NONE:
            if previous_result == RESULT_DONE:
                return STATUS_OK if self.has_schedule else STATUS_NO_SCHEDULE
            if previous_result == RESULT_NONE:
                return STATUS_NEVER_RUN
            if previous_result == RESULT_SUSPEND:
                return STATUS_SUSPENDED
            return STATUS_ERROR
        if raw_status in [
            PROP_STATUS_BACKUP,
            PROP_STATUS_DETECT,
            PROP_STATUS_VER_DEL,
            PROP_STATUS_PREP_VER_DEL,
        ]:
            if previous_result == RESULT_RESUME:
                return STATUS_RESUMING
            if not self.has_schedule:
                return STATUS_RUNNING_NO_SCHEDULE
            return STATUS_RUNNING
        if raw_status == PROP_STATUS_WAITING:
            return STATUS_WAITING

        return STATUS_ERROR

    @property
    def health(self) -> str:
        """Return health.

        Health mapping:
            * Good    => OK, RUNNING, RESUMING and WAITING
            * Warning => NEVER_RUN, SUSPENDED, NO_SCHEDULE
            * Critical => Error
        """
        ok_statuses = [STATUS_OK, STATUS_RESUMING, STATUS_WAITING, STATUS_RUNNING]
        if self.has_schedule and self.status in ok_statuses:
            return HEALTH_GOOD
        if self.status in [STATUS_RESTORE_ONLY, STATUS_ERROR]:
            return HEALTH_CRIT
        # STATUS_UNKNOWN, STATUS_SUSPENDED, STATUS_NEVER_RUN, STATUS_NO_SCHEDULE
        return HEALTH_WARN

    @property
    def is_backing_up(self) -> bool:
        """Is this backup task currently running?"""
        return bool(self.backup_progress is not None)

    @property
    def backup_progress(self) -> int | None:
        """What is backup percent? Returns None if not running."""
        try:
            return (
                self._data["progress"] if self._data["progress"] is not None else None
            )
        except KeyError:
            return None

    @property
    def state(self) -> str:
        """Return state."""
        return self._data["state"]

    @property
    def raw_status(self) -> str:
        """Return raw status."""
        return self._data["status"]

    def used_size(self, human_readable: bool = False) -> int | str | None:
        """Return bytes used for backup in destination."""
        try:
            return_data = self._data["used_size"]
        except KeyError:
            return None
        return_data = return_data * 1024
        if human_readable:
            return SynoFormatHelper.bytes_to_readable(return_data)
        return return_data

    @property
    def previous_result(self) -> str:
        """Return result from previous backup."""
        return self._data["last_bkp_result"]

    @property
    def has_schedule(self) -> bool:
        """Does this backup task have a future schedule?"""
        if self.next_backup_time is None:
            return False
        return bool(self.next_backup_time)

    @property
    def next_backup_time(self) -> datetime | None:
        """Return next scheduled backup date/time."""
        return self.to_datetime(self._data["next_bkp_time"])

    @property
    def target_id(self) -> str:
        """Return target id."""
        return self._data["target_id"]

    @property
    def transfer_type(self) -> str:
        """Return transfer type."""
        return self._data["transfer_type"]

    @property
    def previous_backup_end_time(self) -> datetime | None:
        """Return previous backup end date/time."""
        return self.to_datetime(self._data["last_bkp_end_time"])

    @property
    def previous_backup_time(self) -> datetime | None:
        """Return previous backup date/time."""
        return self.to_datetime(self._data["last_bkp_time"])

    @property
    def previous_error(self) -> str:
        """Return any error from previous backup."""
        return self._data["last_bkp_error"]

    @property
    def previous_success_time(self) -> datetime | None:
        """Return success previous backup date/time."""
        return self.to_datetime(self._data["last_bkp_success_time"])

    # Root
    @property
    def get_raw_data(self) -> dict[str, Any]:
        """Gets raw data of SynoHyperBackupTaskType."""
        return dict(self._data)

    def to_datetime(self, syn_datetime: str) -> datetime | None:
        """Takes a datetime string from YYYY/MM/DD HH:mm to a datetime."""
        if syn_datetime is None or "N/A" == syn_datetime:
            return None
        for fmt in ("%Y/%m/%d %H:%M", "%Y/%m/%d %H:%M:%S"):
            try:
                return datetime.strptime(syn_datetime, fmt)
            except ValueError:
                pass
        return None
