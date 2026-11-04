"""Synology Hyper Backup tests."""

# pylint: disable=protected-access
from copy import deepcopy
from datetime import datetime

import pytest
import pytest_asyncio

from synology_dsm.api.hyperbackup import SynoHyperBackup
from synology_dsm.api.hyperbackup.const import (
    HEALTH_CRIT,
    HEALTH_GOOD,
    HEALTH_WARN,
    PROP_ONLINE,
    PROP_USED_SIZE,
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
from synology_dsm.api.hyperbackup.task import SynoHyperBackupTask
from synology_dsm.exceptions import (
    SynologyDSMAPIErrorException,
    SynologyDSMAPINoDataException,
)

from .api_data.dsm_7.hyperbackup import (
    DSM_7_HYPERBACKUP_LIST,
    DSM_7_STATUSES,
    PERCENT_MIDDLE,
    TARGET_DATA_OFFLINE,
    TARGET_DATA_ONLINE,
)

API_ERROR = {"error": {"code": 400}, "success": False}
NEXT_BACKUP = "2023/12/22 01:00"


class ApiRequestRecorder:
    """Record the API requests of a mocked DSM and optionally override responses."""

    def __init__(self, dsm):
        """Wrap the request execution of the given mocked DSM."""
        self.calls: list[tuple[str, str]] = []
        self.responses: dict[tuple[str, str], dict] = {}
        self._execute_request = dsm._execute_request
        dsm._execute_request = self._record

    async def _record(self, method, url, params, raw_response_content, **kwargs):
        call = (params["api"], params["method"])
        self.calls.append(call)
        if call in self.responses:
            return self.responses[call]
        return await self._execute_request(
            method, url, params, raw_response_content, **kwargs
        )

    def count(self, api: str) -> int:
        """Return the number of recorded requests to the given api."""
        return sum(1 for called_api, _ in self.calls if called_api == api)


# noinspection SpellCheckingInspection
class TestSynoHyperBackup:
    """Test Synology Backup."""

    @pytest_asyncio.fixture(scope="function")
    async def call_update(self, dsm_7):
        """Function for login and hyperbackup.update()."""
        await dsm_7.login()
        await dsm_7.hyperbackup.update(get_all_target_data=False)

    @pytest.fixture
    def api_requests(self, dsm_7):
        """Record the api requests of the mocked DSM 7."""
        return ApiRequestRecorder(dsm_7)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("call_update")
    async def test_get_data(self, dsm_7):
        """Test basic get data and combination of API calls."""
        assert len(dsm_7.hyperbackup.task_ids) > 0
        for task_id in DSM_7_STATUSES:
            processed_task = dsm_7.hyperbackup.get_task(task_id)
            api_task = DSM_7_STATUSES[task_id]["data"]
            target_data = TARGET_DATA_ONLINE["data"]
            assert (
                processed_task.get_raw_data["next_bkp_time"]
                == api_task["next_bkp_time"]
            )
            assert processed_task.state == api_task["state"]
            assert processed_task.raw_status == api_task["status"]
            assert processed_task.target_online == target_data[PROP_ONLINE]
            assert processed_task.used_size() == target_data[PROP_USED_SIZE] * 1024
            assert "source" not in processed_task.get_raw_data
            assert "schedule" not in processed_task.get_raw_data

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("call_update")
    @pytest.mark.parametrize(
        "task_id, expected_status",
        [
            (1, STATUS_RUNNING_NO_SCHEDULE),
            (2, STATUS_RUNNING_NO_SCHEDULE),
            (3, STATUS_RUNNING),
            (4, STATUS_RESTORE_ONLY),
            (5, STATUS_NO_SCHEDULE),
            (6, STATUS_OK),
            (7, STATUS_DETECT),
        ],
    )
    async def test_status(self, task_id, expected_status, dsm_7):
        """Test derived status logic."""
        assert dsm_7.hyperbackup.get_task(task_id).status == expected_status

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("call_update")
    @pytest.mark.parametrize(
        "task_id, expected_health",
        [
            (1, HEALTH_WARN),
            (2, HEALTH_WARN),
            (3, HEALTH_GOOD),
            (4, HEALTH_CRIT),
            (5, HEALTH_WARN),
            (6, HEALTH_GOOD),
            (7, HEALTH_WARN),
        ],
    )
    async def test_health(self, task_id, expected_health, dsm_7):
        """Test health calculation."""
        assert dsm_7.hyperbackup.get_task(task_id).health == expected_health

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("call_update")
    @pytest.mark.parametrize(
        "task_id, expected_percent",
        [
            (1, 0),
            (2, PERCENT_MIDDLE),
            (3, 0),
            (4, None),
            (5, None),
            (6, None),
            (7, None),
        ],
    )
    async def test_progress(self, task_id, expected_percent, dsm_7):
        """Test backup percentage."""
        assert dsm_7.hyperbackup.get_task(task_id).backup_progress == expected_percent

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("call_update")
    @pytest.mark.parametrize(
        "task_id, expected_bool",
        [
            (1, True),
            (2, True),
            (3, True),
            (4, False),
            (5, False),
            (6, False),
            (7, False),
        ],
    )
    async def test_is_backing_up(self, task_id, expected_bool, dsm_7):
        """Test backup is backing up."""
        assert dsm_7.hyperbackup.get_task(task_id).is_backing_up == expected_bool

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("call_update")
    async def test_no_target_api_call_on_second_update_with_same_backup_time(
        self, dsm_7, api_requests
    ):
        """Ensure target API is not called when last backup time is unchanged."""
        await dsm_7.hyperbackup.update(get_all_target_data=False)

        assert api_requests.count(SynoHyperBackup.API_KEY_TARGET) == 0

    @pytest.mark.asyncio
    async def test_get_all_tasks(self, dsm_7):
        """Test the task accessors."""
        assert await dsm_7.login()
        assert dsm_7.hyperbackup.get_all_tasks() == []

        await dsm_7.hyperbackup.update()
        tasks = dsm_7.hyperbackup.get_all_tasks()
        assert [task.task_id for task in tasks] == [1, 2, 3, 4, 5, 6, 7]
        assert all(isinstance(task, SynoHyperBackupTask) for task in tasks)
        assert dsm_7.hyperbackup.task_ids == [1, 2, 3, 4, 5, 6, 7]
        assert dsm_7.hyperbackup.get_raw_data == {task.task_id: task for task in tasks}
        assert dsm_7.hyperbackup.get_task(6) is tasks[5]
        assert dsm_7.hyperbackup.get_task(42) is None

    @pytest.mark.asyncio
    async def test_task_properties(self, dsm_7):
        """Test the properties of a task."""
        assert await dsm_7.login()
        await dsm_7.hyperbackup.update()

        task = dsm_7.hyperbackup.get_task(6)
        assert task.task_id == 6
        assert task.name == "Idle with schedule"
        assert task.target_id == "vault_2.hbk"
        assert task.transfer_type == "image_remote"
        assert task.previous_result == "done"
        assert task.previous_error == ""
        assert task.previous_backup_time == datetime(2023, 12, 21, 1, 13)
        assert task.previous_backup_end_time == datetime(2023, 12, 21, 1, 13)
        assert task.previous_success_time == datetime(2023, 12, 21, 1, 12)
        assert task.next_backup_time == datetime(2023, 12, 22, 1, 0)
        assert task.has_schedule is True
        assert task.target_online is True
        assert task.used_size() == 2048000000000
        assert task.used_size(human_readable=True) == "1.9Tb"

    @pytest.mark.asyncio
    async def test_update_no_data(self, dsm_7):
        """Test update raises when the task list returns no data."""
        dsm_7.no_data_responses.append(SynoHyperBackup.API_KEY)
        assert await dsm_7.login()
        with pytest.raises(SynologyDSMAPINoDataException):
            await dsm_7.hyperbackup.update()
        assert dsm_7.hyperbackup.get_all_tasks() == []

    @pytest.mark.asyncio
    async def test_update_keeps_task_objects(self, dsm_7, api_requests):
        """Test known tasks are updated in place and removed tasks are dropped."""
        assert await dsm_7.login()
        await dsm_7.hyperbackup.update()
        task = dsm_7.hyperbackup.get_task(6)

        await dsm_7.hyperbackup.update()
        assert dsm_7.hyperbackup.get_task(6) is task

        task_list = DSM_7_HYPERBACKUP_LIST["data"]["task_list"]
        api_requests.responses[(SynoHyperBackup.API_KEY, "list")] = {
            "success": True,
            "data": {"task_list": [task_list[5], task_list[6]], "total": 2},
        }
        await dsm_7.hyperbackup.update()
        assert dsm_7.hyperbackup.task_ids == [6, 7]
        assert dsm_7.hyperbackup.get_task(6) is task

    @pytest.mark.asyncio
    async def test_update_error_keeps_previous_tasks(self, dsm_7, api_requests):
        """Test a failing update does not discard the previous tasks."""
        assert await dsm_7.login()
        await dsm_7.hyperbackup.update()
        tasks = dsm_7.hyperbackup.get_all_tasks()

        api_requests.responses[(SynoHyperBackup.API_KEY, "status")] = API_ERROR
        with pytest.raises(SynologyDSMAPIErrorException):
            await dsm_7.hyperbackup.update()
        assert dsm_7.hyperbackup.get_all_tasks() == tasks

    @pytest.mark.asyncio
    async def test_update_without_status_data(self, dsm_7, api_requests):
        """Test tasks are still usable when their status returns no data."""
        assert await dsm_7.login()
        # the task list entries are modified in place without status data
        api_requests.responses[(SynoHyperBackup.API_KEY, "list")] = deepcopy(
            DSM_7_HYPERBACKUP_LIST
        )
        api_requests.responses[(SynoHyperBackup.API_KEY, "status")] = {"success": True}
        await dsm_7.hyperbackup.update()

        task = dsm_7.hyperbackup.get_task(6)
        assert task.state == "backupable"
        assert task.previous_result == "done"
        assert task.next_backup_time is None
        assert task.previous_error is None
        assert task.previous_success_time is None
        assert task.backup_progress is None
        assert task.status == STATUS_NO_SCHEDULE
        assert task.health == HEALTH_WARN

    @pytest.mark.asyncio
    @pytest.mark.parametrize("target_response", [API_ERROR, TARGET_DATA_OFFLINE])
    async def test_target_offline(self, dsm_7, api_requests, target_response):
        """Test tasks with an offline backup target."""
        assert await dsm_7.login()
        api_requests.responses[(SynoHyperBackup.API_KEY_TARGET, "get")] = (
            target_response
        )
        await dsm_7.hyperbackup.update()

        for task in dsm_7.hyperbackup.get_all_tasks():
            assert task.target_online is False
            assert task.used_size() is None
            assert task.used_size(human_readable=True) is None

    @pytest.mark.asyncio
    async def test_target_no_data(self, dsm_7, api_requests):
        """Test tasks when the target returns no data."""
        assert await dsm_7.login()
        api_requests.responses[(SynoHyperBackup.API_KEY_TARGET, "get")] = {
            "success": True
        }
        await dsm_7.hyperbackup.update()

        for task in dsm_7.hyperbackup.get_all_tasks():
            assert task.target_online is False
            assert task.used_size() is None

    @pytest.mark.asyncio
    async def test_target_data_refresh(self, dsm_7, api_requests):
        """Test when the target data is requested again."""
        assert await dsm_7.login()
        await dsm_7.hyperbackup.update()
        assert api_requests.count(SynoHyperBackup.API_KEY_TARGET) == 7

        # target data is requested for all tasks on demand
        api_requests.calls.clear()
        await dsm_7.hyperbackup.update(get_all_target_data=True)
        assert api_requests.count(SynoHyperBackup.API_KEY_TARGET) == 7

        # target data is requested only for tasks with a new backup
        api_requests.calls.clear()
        dsm_7.hyperbackup.get_task(6)._data["last_bkp_time"] = "2023/12/20 01:13"
        await dsm_7.hyperbackup.update()
        assert api_requests.count(SynoHyperBackup.API_KEY_TARGET) == 1
        assert dsm_7.hyperbackup.get_task(6).target_online is True

        # target data is always requested for tasks without a backup yet
        api_requests.calls.clear()
        api_requests.responses[(SynoHyperBackup.API_KEY, "status")] = {
            "success": True,
            "data": {"last_bkp_time": ""},
        }
        await dsm_7.hyperbackup.update()
        assert api_requests.count(SynoHyperBackup.API_KEY_TARGET) == 7

    @pytest.mark.parametrize(
        "state, raw_status, previous_result, next_backup, expected_status, "
        "expected_health",
        [
            ("restore_only", "none", "done", "", STATUS_RESTORE_ONLY, HEALTH_CRIT),
            ("error_detect", "detect_waiting", "done", "", STATUS_DETECT, HEALTH_WARN),
            ("error_detect", "none", "done", NEXT_BACKUP, STATUS_ERROR, HEALTH_CRIT),
            ("broken", "none", "done", NEXT_BACKUP, STATUS_ERROR, HEALTH_CRIT),
            ("unauth", "none", "done", NEXT_BACKUP, STATUS_ERROR, HEALTH_CRIT),
            ("endofservice", "none", "done", NEXT_BACKUP, STATUS_ERROR, HEALTH_CRIT),
            ("relinkable", "none", "done", NEXT_BACKUP, STATUS_UNKNOWN, HEALTH_WARN),
            ("backupable", "none", "done", NEXT_BACKUP, STATUS_OK, HEALTH_GOOD),
            ("backupable", "none", "done", "", STATUS_NO_SCHEDULE, HEALTH_WARN),
            ("backupable", "none", "none", NEXT_BACKUP, STATUS_NEVER_RUN, HEALTH_WARN),
            ("backupable", "none", "suspend", "", STATUS_SUSPENDED, HEALTH_WARN),
            ("backupable", "none", "failed", NEXT_BACKUP, STATUS_ERROR, HEALTH_CRIT),
            ("backupable", "backup", "resuming", "", STATUS_RESUMING, HEALTH_WARN),
            (
                "backupable",
                "backup",
                "resuming",
                NEXT_BACKUP,
                STATUS_RESUMING,
                HEALTH_GOOD,
            ),
            (
                "backupable",
                "version_deleting",
                "done",
                "",
                STATUS_RUNNING_NO_SCHEDULE,
                HEALTH_WARN,
            ),
            (
                "backupable",
                "preparing_version_delete",
                "done",
                NEXT_BACKUP,
                STATUS_RUNNING,
                HEALTH_GOOD,
            ),
            ("backupable", "detect", "done", NEXT_BACKUP, STATUS_RUNNING, HEALTH_GOOD),
            ("backupable", "waiting", "done", NEXT_BACKUP, STATUS_WAITING, HEALTH_GOOD),
            ("backupable", "waiting", "done", "", STATUS_WAITING, HEALTH_WARN),
            (
                "backupable",
                "unexpected",
                "done",
                NEXT_BACKUP,
                STATUS_ERROR,
                HEALTH_CRIT,
            ),
        ],
    )
    def test_status_and_health_mapping(
        self,
        state,
        raw_status,
        previous_result,
        next_backup,
        expected_status,
        expected_health,
    ):
        """Test the derived status and health of all known combinations."""
        task = SynoHyperBackupTask(
            {
                "task_id": 1,
                "state": state,
                "status": raw_status,
                "last_bkp_result": previous_result,
                "next_bkp_time": next_backup,
            }
        )
        assert task.status == expected_status
        assert task.health == expected_health

    def test_task_without_status_data(self):
        """Test a task containing only the task list data."""
        task = SynoHyperBackupTask(
            {"task_id": 1, "name": "Task", "state": "backupable", "status": "none"}
        )
        assert task.previous_result is None
        assert task.previous_error is None
        assert task.previous_backup_time is None
        assert task.previous_backup_end_time is None
        assert task.previous_success_time is None
        assert task.next_backup_time is None
        assert task.has_schedule is False
        assert task.backup_progress is None
        assert task.is_backing_up is False
        assert task.target_online is False
        assert task.used_size() is None
        assert task.status == STATUS_ERROR
        assert task.health == HEALTH_CRIT

    def test_task_update(self):
        """Test updating the data of a task."""
        task = SynoHyperBackupTask({"task_id": 1, "name": "Old name"})
        task.update({"task_id": 1, "name": "New name"})
        assert task.name == "New name"

    @pytest.mark.parametrize(
        "value, expected",
        [
            ("2023/12/22 01:00", datetime(2023, 12, 22, 1, 0)),
            ("2023/12/22 01:00:30", datetime(2023, 12, 22, 1, 0, 30)),
            ("N/A", None),
            ("", None),
            (None, None),
            ("invalid", None),
        ],
    )
    def test_to_datetime(self, value, expected):
        """Test parsing of the api date/time values."""
        assert SynoHyperBackupTask({}).to_datetime(value) == expected
