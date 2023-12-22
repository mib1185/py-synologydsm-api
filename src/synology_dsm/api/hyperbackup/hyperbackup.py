"""HyperBackup task data."""
from typing import Any
from typing import Dict
import json
from datetime import datetime

from synology_dsm.exceptions import SynologyDSMAPIErrorException

from .const import *

import logging
LOGGER = logging.getLogger(__name__)


class SynoHyperBackup:
    """An implementation of Synology HyperBackup."""

    API_KEY = "SYNO.Backup.Task"
    API_KEY_TARGET = "SYNO.Backup.Target"
    STATUS_FIELDS = [PROP_LAST_BACKUP_TIME, PROP_NEXT_BACKUP_TIME, PROP_LAST_RESULT, PROP_LAST_PROGRESS]
    TARGET_FIELDS = [PROP_ONLINE, PROP_USED_SIZE]
    SYN_DATE_FORMAT = '%Y/%m/%d %H:%M'

    def __init__(self, dsm):
        """Initialize HyperBackup."""
        self._dsm = dsm
        self._data: Dict[int, Dict[str, Any]] = {}
        self._last_backup_times: Dict[int, str] = {}

    async def update(self, get_all_target_data=False):
        """Update backup tasks settings and information from API."""
        prev_data = self._data
        self._data = {}

        LOGGER.debug("Executing %s API call for task list", self.API_KEY)
        task_list = (await self._dsm.get(self.API_KEY, "list", max_version=1))["data"].get("task_list", [])
        for task in task_list:
            task_id = task[PROP_TASKID]

            LOGGER.debug("Executing %s API call for task status details: %d", self.API_KEY, task_id)
            backup_status = (await self._dsm.get(
                self.API_KEY, "status",
                {PROP_TASKID: task_id, "additional": json.dumps(self.STATUS_FIELDS)},
                max_version=1
            ))["data"]
            task = task | backup_status
            task.pop("schedule", None)  # Keep response cleaner (schedule is a large array)
            task.pop("source", None)  # Keep response cleaner (source can be a large array)

            target_data = await self._get_target_data(task_id, task, prev_data, get_all_target_data)
            task = task | target_data

            self._last_backup_times[task_id] = task[PROP_LAST_BACKUP_TIME]
            self._data[task_id] = task

    async def _get_target_data(self, task_id: int, task: Dict, prev_data: Dict, get_all_target_data=False) -> Dict:
        backup_since_last_update = (task_id not in self._last_backup_times) or \
                                   (task[PROP_LAST_BACKUP_TIME] != self._last_backup_times[task_id]) or \
                                   not task[PROP_LAST_BACKUP_TIME]

        # Target API calls can be expensive (1 - 3+ seconds each), so only get them if there has been a backup.
        if backup_since_last_update or get_all_target_data:
            try:
                LOGGER.debug("Making %s API call for task %d", self.API_KEY_TARGET, task_id)
                target_data = (await self._dsm.get(
                    self.API_KEY_TARGET,
                    "get",
                    {PROP_TASKID: task_id, 'additional': json.dumps(self.TARGET_FIELDS)},
                    max_version=1
                ))["data"]
            except SynologyDSMAPIErrorException:  # Occurs when target is "offline"
                LOGGER.debug("target call failed for task %d, assuming target is offline", task_id)
                target_data = {'is_online': False}
        else:
            target_data = prev_data[task_id]  # Use previous values for size and target

        return {k: target_data.get(k, None) for k in tuple(self.TARGET_FIELDS)}

    @property
    def task_ids(self):
        """Returns (internal) hyper backup task ids."""
        return self._data.keys()

    @property
    def tasks(self) -> Dict[int, Dict[str, Any]]:
        """Return a list of all tasks."""
        return self._data

    def get_task(self, task_id: int) -> Dict[str, Any]:
        """Return task matching task_id."""
        return self._data[task_id]

    def health(self, task_id: int) -> str:
        """
        Health mapping:
            * Good    => OK, RUNNING, RESUMING and WAITING
            * Warning => NEVER_RUN, SUSPENDED, NO_SCHEDULE
            * Critical => Error
        """
        if self.has_schedule(task_id) and self.status(task_id) in [STATUS_OK, STATUS_RESUMING, STATUS_WAITING, STATUS_RUNNING]:
            return HEALTH_GOOD
        elif self.status(task_id) in [STATUS_RESTORE_ONLY, STATUS_ERROR]:
            return HEALTH_CRIT
        else:  # STATUS_UNKNOWN, STATUS_SUSPENDED, STATUS_NEVER_RUN, STATUS_NO_SCHEDULE
            return HEALTH_WARN

    def status(self, task_id: int) -> str:
        """
        An 'OK' status requires state=backupable && status=None && result=done && next_backup not null.
        """
        raw_status = self.raw_status(task_id)
        state = self.state(task_id)
        previous_result = self.raw_previous_result(task_id)

        # Check state value first
        if state != STATE_BACKUP:
            if state == STATE_RESTORE_ONLY:
                return STATUS_RESTORE_ONLY
            elif state in [STATE_ERROR, STATE_BROKEN, STATE_UNAUTH, STATE_END_SERVICE]:
                return STATUS_ERROR
            else:
                return STATUS_UNKNOWN  # TODO: Research relink/import/export backup tasks

        # Then check status value and previous result
        if raw_status == PROP_STATUS_NONE:
            if previous_result == RESULT_DONE:
                return STATUS_OK if self.has_schedule(task_id) else STATUS_NO_SCHEDULE
            elif previous_result == RESULT_NONE:
                return STATUS_NEVER_RUN
            elif previous_result == RESULT_SUSPEND:
                return STATUS_SUSPENDED
            else:
                return STATUS_ERROR
        elif raw_status in [PROP_STATUS_BACKUP, PROP_STATUS_DETECT, PROP_STATUS_VER_DEL, PROP_STATUS_PREP_VER_DEL]:
            if previous_result == RESULT_RESUME:
                return STATUS_RESUMING
            if not self.has_schedule(task_id):
                return STATUS_RUNNING_NO_SCHEDULE
            return STATUS_RUNNING
        elif raw_status == PROP_STATUS_WAITING:
            return STATUS_WAITING
        else:
            return STATUS_ERROR

    def name(self, task_id: int) -> str:
        """Return name."""
        return self._data.get(task_id).get(PROP_NAME)

    def has_schedule(self, task_id: int) -> str:
        """Does this backup task have a future schedule?"""
        return bool(self.next_backup_time(task_id))

    def backup_progress(self, task_id: int) -> str:
        """What is backup percent? Returns None if not running."""
        try:
            return self._data.get(task_id).get(PROP_PROGRESS).get(PROP_PROGRESS)
        except AttributeError:
            return None

    def state(self, task_id: int) -> str:
        """Return state."""
        return self._data.get(task_id).get(PROP_STATE)

    def raw_status(self, task_id: int) -> str:
        """Return status."""
        return self._data.get(task_id).get(PROP_STATUS)

    def target_id(self, task_id: int) -> str:
        """Return target id."""
        return self._data.get(task_id).get(PROP_TARGET_ID)

    def task_id(self, task_id: int) -> int:
        """Return task id."""
        return self._data.get(task_id).get(PROP_TASKID)

    def transfer_type(self, task_id: int) -> str:
        """Return transfer type."""
        return self._data.get(task_id).get(PROP_TRANSFER_TYPE)

    def previous_result(self, task_id: int) -> str:
        """Return result from previous backup."""
        return self._data.get(task_id).get(PROP_LAST_RESULT).capitalize()

    def raw_previous_result(self, task_id: int) -> str:
        """Return result from previous backup."""
        return self._data.get(task_id).get(PROP_LAST_RESULT)

    def previous_backup_time(self, task_id: int) -> datetime:
        """Return previous backup date/time."""
        return self.to_datetime(self._data.get(task_id).get(PROP_LAST_BACKUP_END_TIME))

    def next_backup_time(self, task_id: int) -> datetime:
        """Return next scheduled backup date/time."""
        return self.to_datetime(self._data.get(task_id).get(PROP_NEXT_BACKUP_TIME))

    def previous_error(self, task_id: int) -> str:
        """Return any error from previous backup."""
        return self._data.get(task_id).get(PROP_LAST_BACKUP_ERROR)

    def target_online(self, task_id: int) -> str:
        """Return target online status."""
        return self._data.get(task_id).get(PROP_ONLINE)

    def used_size(self, task_id: int) -> str:
        """Return bytes used for backup in destination."""
        return self._data.get(task_id).get(PROP_USED_SIZE)

    @classmethod
    def to_datetime(cls, syn_datetime):
        """ Takes a datetime string from YYYY/MM/DD HH:mm to a datetime"""
        if not syn_datetime:
            return None
        return datetime.strptime(syn_datetime, cls.SYN_DATE_FORMAT)
