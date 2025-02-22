"""Synology DSM tests."""

# pylint: disable=protected-access
import pytest

from synology_dsm.const import API_AUTH
from synology_dsm.exceptions import SynologyDSMLogin2SARequiredException

from . import (
    VALID_HOST,
    VALID_HTTPS,
    VALID_OTP,
    VALID_PASSWORD,
    VALID_PORT,
    VALID_USER_2SA,
    SynologyDSMMock,
)
from .const import DEVICE_TOKEN, SESSION_ID


class TestSynologyDSM5:
    """SynologyDSM 5test cases."""

    @pytest.mark.asyncio
    async def test_login(self, dsm_5):
        """Test login."""
        assert await dsm_5.login()
        assert dsm_5.apis.get(API_AUTH)
        assert dsm_5._session_id == SESSION_ID
        assert dsm_5._syno_token is None

    @pytest.mark.asyncio
    async def test_login_2sa(self):
        """Test login with 2SA."""
        dsm_5 = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            VALID_USER_2SA,
            VALID_PASSWORD,
            VALID_HTTPS,
        )
        dsm_5.dsm_version = 5
        with pytest.raises(SynologyDSMLogin2SARequiredException):
            await dsm_5.login()
        await dsm_5.login(VALID_OTP)

        assert dsm_5._session_id == SESSION_ID
        assert dsm_5._syno_token is None
        assert dsm_5._device_token == DEVICE_TOKEN
        assert dsm_5.device_token == DEVICE_TOKEN

    @pytest.mark.asyncio
    async def test_login_2sa_new_session(self):
        """Test login with 2SA and a new session with granted device."""
        dsm_5 = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            VALID_USER_2SA,
            VALID_PASSWORD,
            VALID_HTTPS,
            device_token=DEVICE_TOKEN,
        )
        dsm_5.dsm_version = 5
        assert await dsm_5.login()

        assert dsm_5._session_id == SESSION_ID
        assert dsm_5._syno_token is None
        assert dsm_5._device_token == DEVICE_TOKEN
        assert dsm_5.device_token == DEVICE_TOKEN

    @pytest.mark.asyncio
    async def test_information(self, dsm_5):
        """Test information."""
        assert await dsm_5.login()
        assert dsm_5.information
        await dsm_5.information.update()
        assert dsm_5.information.model == "DS3615xs"
        assert dsm_5.information.ram == 6144
        assert dsm_5.information.serial == "B3J4N01003"
        assert dsm_5.information.temperature == 40
        assert not dsm_5.information.temperature_warn
        assert dsm_5.information.uptime == 3897
        assert dsm_5.information.version == "5967"
        assert dsm_5.information.version_string == "DSM 5.2-5967 Update 9"
        assert dsm_5.information.awesome_version == "5.2.0.9"

    @pytest.mark.asyncio
    async def test_network(self, dsm_5):
        """Test network."""
        assert await dsm_5.login()
        assert dsm_5.network
        await dsm_5.network.update()
        assert dsm_5.network.dns
        assert dsm_5.network.gateway
        assert dsm_5.network.hostname
        assert dsm_5.network.interfaces
        assert dsm_5.network.interface("eth0")
        assert dsm_5.network.interface("eth1") is None
        assert dsm_5.network.macs
        assert dsm_5.network.workgroup

    @pytest.mark.asyncio
    async def test_storage(self, dsm_5):
        """Test storage roots."""
        assert await dsm_5.login()
        assert dsm_5.storage
        await dsm_5.storage.update()
        assert dsm_5.storage.disks
        assert dsm_5.storage.env
        assert dsm_5.storage.storage_pools == []
        assert dsm_5.storage.volumes

    @pytest.mark.asyncio
    async def test_storage_volumes(self, dsm_5):
        """Test storage volumes."""
        assert await dsm_5.login()
        await dsm_5.storage.update()
        # Basics
        assert dsm_5.storage.volumes_ids
        for volume_id in dsm_5.storage.volumes_ids:
            if volume_id == "test_volume":
                continue
            assert dsm_5.storage.volume_status(volume_id)
            assert dsm_5.storage.volume_device_type(volume_id)
            assert dsm_5.storage.volume_size_total(volume_id)
            assert dsm_5.storage.volume_size_total(volume_id, True)
            assert dsm_5.storage.volume_size_used(volume_id)
            assert dsm_5.storage.volume_size_used(volume_id, True)
            assert dsm_5.storage.volume_percentage_used(volume_id)
            assert (
                dsm_5.storage.volume_disk_temp_avg(volume_id) is None
            )  # because of empty storagePools
            assert (
                dsm_5.storage.volume_disk_temp_max(volume_id) is None
            )  # because of empty storagePools

        # Existing volume
        assert dsm_5.storage.volume_status("volume_1") == "normal"
        assert dsm_5.storage.volume_device_type("volume_1") == "raid_5"
        assert dsm_5.storage.volume_size_total("volume_1") == 8846249701376
        assert dsm_5.storage.volume_size_total("volume_1", True) == "8.0Tb"
        assert dsm_5.storage.volume_size_used("volume_1") == 5719795761152
        assert dsm_5.storage.volume_size_used("volume_1", True) == "5.2Tb"
        assert dsm_5.storage.volume_percentage_used("volume_1") == 64.7
        assert (
            dsm_5.storage.volume_disk_temp_avg("volume_1") is None
        )  # because of empty storagePools
        assert (
            dsm_5.storage.volume_disk_temp_max("volume_1") is None
        )  # because of empty storagePools

        # Non existing volume
        assert not dsm_5.storage.volume_status("not_a_volume")
        assert not dsm_5.storage.volume_device_type("not_a_volume")
        assert not dsm_5.storage.volume_size_total("not_a_volume")
        assert not dsm_5.storage.volume_size_total("not_a_volume", True)
        assert not dsm_5.storage.volume_size_used("not_a_volume")
        assert not dsm_5.storage.volume_size_used("not_a_volume", True)
        assert not dsm_5.storage.volume_percentage_used("not_a_volume")
        assert not dsm_5.storage.volume_disk_temp_avg("not_a_volume")
        assert not dsm_5.storage.volume_disk_temp_max("not_a_volume")

        # Test volume
        assert dsm_5.storage.volume_status("test_volume") is None
        assert dsm_5.storage.volume_device_type("test_volume") is None
        assert dsm_5.storage.volume_size_total("test_volume") is None
        assert dsm_5.storage.volume_size_total("test_volume", True) is None
        assert dsm_5.storage.volume_size_used("test_volume") is None
        assert dsm_5.storage.volume_size_used("test_volume", True) is None
        assert dsm_5.storage.volume_percentage_used("test_volume") is None
        assert dsm_5.storage.volume_disk_temp_avg("test_volume") is None
        assert dsm_5.storage.volume_disk_temp_max("test_volume") is None

    @pytest.mark.asyncio
    async def test_storage_disks(self, dsm_5):
        """Test storage disks."""
        assert await dsm_5.login()
        await dsm_5.storage.update()
        # Basics
        assert dsm_5.storage.disks_ids
        for disk_id in dsm_5.storage.disks_ids:
            if disk_id == "test_disk":
                continue
            assert "Disk" in dsm_5.storage.disk_name(disk_id)
            assert "/dev/" in dsm_5.storage.disk_device(disk_id)
            if disk_id == "sda":
                assert dsm_5.storage.disk_smart_status(disk_id) == "90%"
            else:
                assert dsm_5.storage.disk_smart_status(disk_id) == "safe"
            assert dsm_5.storage.disk_status(disk_id) == "normal"
            assert not dsm_5.storage.disk_exceed_bad_sector_thr(disk_id)
            assert not dsm_5.storage.disk_below_remain_life_thr(disk_id)
            assert dsm_5.storage.disk_temp(disk_id)

        # Non existing disk
        assert not dsm_5.storage.disk_name("not_a_disk")
        assert not dsm_5.storage.disk_device("not_a_disk")
        assert not dsm_5.storage.disk_smart_status("not_a_disk")
        assert not dsm_5.storage.disk_status("not_a_disk")
        assert not dsm_5.storage.disk_exceed_bad_sector_thr("not_a_disk")
        assert not dsm_5.storage.disk_below_remain_life_thr("not_a_disk")
        assert not dsm_5.storage.disk_temp("not_a_disk")

        # Test disk
        assert dsm_5.storage.disk_name("test_disk") is None
        assert dsm_5.storage.disk_device("test_disk") is None
        assert dsm_5.storage.disk_smart_status("test_disk") is None
        assert dsm_5.storage.disk_status("test_disk") is None
        assert dsm_5.storage.disk_exceed_bad_sector_thr("test_disk") is None
        assert dsm_5.storage.disk_below_remain_life_thr("test_disk") is None
        assert dsm_5.storage.disk_temp("test_disk") is None
