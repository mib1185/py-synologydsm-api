"""Synology DSM tests."""
import pytest
import pytest_asyncio

from synology_dsm.api.hyperbackup.hyperbackup import (
    SynoHyperBackup, PROP_ONLINE, PROP_USED_SIZE, HEALTH_GOOD, HEALTH_WARN, HEALTH_CRIT,
    STATUS_OK, STATUS_RUNNING, STATUS_WAITING, STATUS_RESUMING, STATUS_SUSPENDED, STATUS_NEVER_RUN, STATUS_NO_SCHEDULE,
    STATUS_RESTORE_ONLY, STATUS_UNKNOWN, STATUS_ERROR, STATUS_RUNNING_NO_SCHEDULE
)
from synology_dsm.const import API_AUTH, API_INFO
from synology_dsm.exceptions import (
    SynologyDSMAPIErrorException,
    SynologyDSMAPINotExistsException,
    SynologyDSMLogin2SAFailedException,
    SynologyDSMLogin2SARequiredException,
    SynologyDSMLoginFailedException,
    SynologyDSMLoginInvalidException,
    SynologyDSMRequestException,
)

from synology_dsm.synology_dsm import SynologyDSM
from .api_data.dsm_7.hyperbackup import (
    DSM_7_HYPERBACKUP_LIST, DSM_7_STATUSES, TARGET_DATA_ONLINE, TARGET_DATA_OFFLINE, PERCENT_MIDDLE
)
from . import SynologyDSMMock


# noinspection SpellCheckingInspection
class TestSynoHyperBackup:
    """Test Synology Backup."""
    hyperbackup: SynoHyperBackup

    @pytest.fixture(autouse=True)
    def run_around_tests(self):
        dsm = SynologyDSMMock()
        dsm.dsm_version = 7
        dsm.hyper_backup_list = DSM_7_HYPERBACKUP_LIST
        dsm.hyper_task_status = DSM_7_STATUSES
        dsm.hyper_target_data = TARGET_DATA_ONLINE
        self.hyperbackup = SynoHyperBackup(dsm)
        yield

    @pytest_asyncio.fixture(scope='function')
    async def call_update(self):
        await self.hyperbackup.update(get_all_target_data=False)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('call_update')
    async def test_get_data(self):
        """Test basic get data and combination of API calls."""
        assert len(self.hyperbackup.task_ids) > 0
        for task_id in DSM_7_STATUSES:
            processed_task = self.hyperbackup.get_task(task_id)
            api_task = DSM_7_STATUSES[task_id]['data']
            target_data = TARGET_DATA_ONLINE['data']
            assert processed_task['next_bkp_time'] == api_task['next_bkp_time']
            assert processed_task['state'] == api_task['state']
            assert processed_task['status'] == api_task['status']
            assert processed_task[PROP_ONLINE] == target_data[PROP_ONLINE]
            assert processed_task[PROP_USED_SIZE] == target_data[PROP_USED_SIZE]
            assert 'source' not in processed_task
            assert 'schedule' not in processed_task

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('call_update')
    @pytest.mark.parametrize("task_id, expected_status", [
        (1, STATUS_RUNNING_NO_SCHEDULE), (2, STATUS_RUNNING_NO_SCHEDULE), (3, STATUS_RUNNING),
        (4, STATUS_RESTORE_ONLY), (5, STATUS_NO_SCHEDULE), (6, STATUS_OK)
    ])
    async def test_status(self, task_id, expected_status):
        """Test dervied status logic"""
        assert self.hyperbackup.status(task_id) == expected_status

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('call_update')
    @pytest.mark.parametrize("task_id, expected_health", [
        (1, HEALTH_WARN), (2, HEALTH_WARN), (3, HEALTH_GOOD), (4, HEALTH_CRIT), (5, HEALTH_WARN), (6, HEALTH_GOOD)
    ])
    async def test_health(self, task_id, expected_health):
        """Test health calculation"""
        assert self.hyperbackup.health(task_id) == expected_health

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('call_update')
    @pytest.mark.parametrize("task_id, expected_percent", [
        (1, 0), (2, PERCENT_MIDDLE), (3, 0), (4, None), (5, None), (6, None)
    ])
    async def test_progress(self, task_id, expected_percent):
        """Test backup percentage"""
        assert self.hyperbackup.backup_progress(task_id) == expected_percent
