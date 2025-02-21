"""Synology DSM tests."""

import pytest
import pytest_asyncio

from synology_dsm.api.hyperbackup.const import (
    HEALTH_CRIT,
    HEALTH_GOOD,
    HEALTH_WARN,
    PROP_ONLINE,
    PROP_USED_SIZE,
    STATUS_DETECT,
    STATUS_NO_SCHEDULE,
    STATUS_OK,
    STATUS_RESTORE_ONLY,
    STATUS_RUNNING,
    STATUS_RUNNING_NO_SCHEDULE,
)

from .api_data.dsm_7.hyperbackup import (
    DSM_7_STATUSES,
    PERCENT_MIDDLE,
    TARGET_DATA_ONLINE,
)


# noinspection SpellCheckingInspection
class TestSynoHyperBackup:
    """Test Synology Backup."""

    @pytest_asyncio.fixture(scope="function")
    async def call_update(self, dsm_7):
        """Function for login and hyperbackup.update()."""
        await dsm_7.login()
        await dsm_7.hyperbackup.update(get_all_target_data=False)

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
        """Test dervied status logic."""
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
