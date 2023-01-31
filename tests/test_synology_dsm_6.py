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
from .const import DEVICE_TOKEN, SESSION_ID, SYNO_TOKEN


class TestSynologyDSM6:
    """SynologyDSM 6 test cases."""

    @pytest.mark.asyncio
    async def test_login(self, dsm_6):
        """Test login."""
        assert await dsm_6.login()
        assert dsm_6.apis.get(API_AUTH)
        assert dsm_6._session_id == SESSION_ID
        assert dsm_6._syno_token == SYNO_TOKEN

    @pytest.mark.asyncio
    async def test_login_2sa(self):
        """Test login with 2SA."""
        dsm = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            VALID_USER_2SA,
            VALID_PASSWORD,
            VALID_HTTPS,
        )

        with pytest.raises(SynologyDSMLogin2SARequiredException) as error:
            await dsm.login()
        error_value = error.value.args[0]
        assert error_value["api"] == "SYNO.API.Auth"
        assert error_value["code"] == 403
        assert error_value["reason"] == "One time password not specified"
        assert (
            error_value["details"]
            == "Two-step authentication required for account: valid_user_2sa"
        )

        assert await dsm.login(VALID_OTP)

        assert dsm._session_id == SESSION_ID
        assert dsm._syno_token == SYNO_TOKEN
        assert dsm._device_token == DEVICE_TOKEN
        assert dsm.device_token == DEVICE_TOKEN

    @pytest.mark.asyncio
    async def test_login_2sa_new_session(self):
        """Test login with 2SA and a new session with granted device."""
        dsm = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            VALID_USER_2SA,
            VALID_PASSWORD,
            VALID_HTTPS,
            device_token=DEVICE_TOKEN,
        )
        assert await dsm.login()

        assert dsm._session_id == SESSION_ID
        assert dsm._syno_token == SYNO_TOKEN
        assert dsm._device_token == DEVICE_TOKEN
        assert dsm.device_token == DEVICE_TOKEN

    @pytest.mark.asyncio
    async def test_information(self, dsm_6):
        """Test information."""
        assert await dsm_6.login()
        assert dsm_6.information
        await dsm_6.information.update()
        assert dsm_6.information.model == "DS918+"
        assert dsm_6.information.ram == 4096
        assert dsm_6.information.serial == "1920PDN001501"
        assert dsm_6.information.temperature == 40
        assert not dsm_6.information.temperature_warn
        assert dsm_6.information.uptime == 155084
        assert dsm_6.information.version == "24922"
        assert dsm_6.information.version_string == "DSM 6.2.2-24922 Update 4"

    @pytest.mark.asyncio
    async def test_network(self, dsm_6):
        """Test network."""
        assert await dsm_6.login()
        assert dsm_6.network
        await dsm_6.network.update()
        assert dsm_6.network.dns
        assert dsm_6.network.gateway
        assert dsm_6.network.hostname
        assert dsm_6.network.interfaces
        assert dsm_6.network.interface("eth0")
        assert dsm_6.network.interface("eth1")
        assert dsm_6.network.macs
        assert dsm_6.network.workgroup

    @pytest.mark.asyncio
    async def test_security(self, dsm_6):
        """Test security, safe status."""
        assert await dsm_6.login()
        assert dsm_6.security
        await dsm_6.security.update()
        assert dsm_6.security.checks
        assert dsm_6.security.last_scan_time
        assert not dsm_6.security.start_time  # Finished scan
        assert dsm_6.security.success
        assert dsm_6.security.progress
        assert dsm_6.security.status == "safe"
        assert dsm_6.security.status_by_check
        assert dsm_6.security.status_by_check["malware"] == "safe"
        assert dsm_6.security.status_by_check["network"] == "safe"
        assert dsm_6.security.status_by_check["securitySetting"] == "safe"
        assert dsm_6.security.status_by_check["systemCheck"] == "safe"
        assert dsm_6.security.status_by_check["update"] == "safe"
        assert dsm_6.security.status_by_check["userInfo"] == "safe"

    @pytest.mark.asyncio
    async def test_security_error(self, dsm_6):
        """Test security, outOfDate status."""
        assert await dsm_6.login()
        dsm_6.error = True
        assert dsm_6.security
        await dsm_6.security.update()
        assert dsm_6.security.checks
        assert dsm_6.security.last_scan_time
        assert not dsm_6.security.start_time  # Finished scan
        assert dsm_6.security.success
        assert dsm_6.security.progress
        assert dsm_6.security.status == "outOfDate"
        assert dsm_6.security.status_by_check
        assert dsm_6.security.status_by_check["malware"] == "safe"
        assert dsm_6.security.status_by_check["network"] == "safe"
        assert dsm_6.security.status_by_check["securitySetting"] == "safe"
        assert dsm_6.security.status_by_check["systemCheck"] == "safe"
        assert dsm_6.security.status_by_check["update"] == "outOfDate"
        assert dsm_6.security.status_by_check["userInfo"] == "safe"

    @pytest.mark.asyncio
    async def test_shares(self, dsm_6):
        """Test shares."""
        assert await dsm_6.login()
        assert dsm_6.share
        await dsm_6.share.update()
        assert dsm_6.share.shares
        for share_uuid in dsm_6.share.shares_uuids:
            assert dsm_6.share.share_name(share_uuid)
            assert dsm_6.share.share_path(share_uuid)
            assert dsm_6.share.share_recycle_bin(share_uuid) is not None
            assert dsm_6.share.share_size(share_uuid) is not None
            assert dsm_6.share.share_size(share_uuid, human_readable=True)

        assert (
            dsm_6.share.share_name("2ee6c06a-8766-48b5-013d-63b18652a393")
            == "test_share"
        )
        assert (
            dsm_6.share.share_path("2ee6c06a-8766-48b5-013d-63b18652a393") == "/volume1"
        )
        assert (
            dsm_6.share.share_recycle_bin("2ee6c06a-8766-48b5-013d-63b18652a393")
            is True
        )
        assert (
            dsm_6.share.share_size("2ee6c06a-8766-48b5-013d-63b18652a393")
            == 3.790251876432216e19
        )
        assert (
            dsm_6.share.share_size("2ee6c06a-8766-48b5-013d-63b18652a393", True)
            == "32.9Eb"
        )

    @pytest.mark.asyncio
    async def test_system(self, dsm_6):
        """Test system."""
        assert await dsm_6.login()
        assert dsm_6.system
        await dsm_6.system.update()
        assert dsm_6.system.cpu_clock_speed
        assert dsm_6.system.cpu_cores
        assert dsm_6.system.cpu_family
        assert dsm_6.system.cpu_series
        assert dsm_6.system.firmware_ver
        assert dsm_6.system.model
        assert dsm_6.system.ram_size
        assert dsm_6.system.serial
        assert dsm_6.system.sys_temp
        assert dsm_6.system.time
        assert dsm_6.system.time_zone
        assert dsm_6.system.time_zone_desc
        assert dsm_6.system.up_time
        for usb_dev in dsm_6.system.usb_dev:
            assert usb_dev.get("cls")
            assert usb_dev.get("pid")
            assert usb_dev.get("producer")
            assert usb_dev.get("product")
            assert usb_dev.get("rev")
            assert usb_dev.get("vid")

    @pytest.mark.asyncio
    async def test_upgrade(self, dsm_6):
        """Test upgrade."""
        assert await dsm_6.login()
        assert dsm_6.upgrade
        await dsm_6.upgrade.update()
        assert dsm_6.upgrade.update_available
        assert dsm_6.upgrade.available_version == "DSM 6.2.3-25426 Update 2"
        assert dsm_6.upgrade.reboot_needed == "now"
        assert dsm_6.upgrade.service_restarts == "some"
        assert dsm_6.upgrade.available_version_details == {
            "buildnumber": 25426,
            "major": 6,
            "micro": 3,
            "minor": 2,
            "nano": 2,
            "os_name": "DSM",
        }

    @pytest.mark.asyncio
    async def test_storage(self, dsm_6):
        """Test storage roots."""
        assert await dsm_6.login()
        assert dsm_6.storage
        await dsm_6.storage.update()
        assert dsm_6.storage.disks
        assert dsm_6.storage.env
        assert dsm_6.storage.storage_pools
        assert dsm_6.storage.volumes

    @pytest.mark.asyncio
    async def test_storage_raid_volumes(self, dsm_6):
        """Test RAID storage volumes."""
        assert await dsm_6.login()
        await dsm_6.storage.update()
        # Basics
        assert dsm_6.storage.volumes_ids
        for volume_id in dsm_6.storage.volumes_ids:
            if volume_id == "test_volume":
                continue
            assert dsm_6.storage.volume_status(volume_id)
            assert dsm_6.storage.volume_device_type(volume_id)
            assert dsm_6.storage.volume_size_total(volume_id)
            assert dsm_6.storage.volume_size_total(volume_id, True)
            assert dsm_6.storage.volume_size_used(volume_id)
            assert dsm_6.storage.volume_size_used(volume_id, True)
            assert dsm_6.storage.volume_percentage_used(volume_id)
            assert dsm_6.storage.volume_disk_temp_avg(volume_id)
            assert dsm_6.storage.volume_disk_temp_max(volume_id)

        # Existing volume
        assert dsm_6.storage.volume_status("volume_1") == "normal"
        assert dsm_6.storage.volume_device_type("volume_1") == "raid_5"
        assert dsm_6.storage.volume_size_total("volume_1") == 7672030584832
        assert dsm_6.storage.volume_size_total("volume_1", True) == "7.0Tb"
        assert dsm_6.storage.volume_size_used("volume_1") == 4377452806144
        assert dsm_6.storage.volume_size_used("volume_1", True) == "4.0Tb"
        assert dsm_6.storage.volume_percentage_used("volume_1") == 57.1
        assert dsm_6.storage.volume_disk_temp_avg("volume_1") == 24.0
        assert dsm_6.storage.volume_disk_temp_max("volume_1") == 24

        # Non existing volume
        assert not dsm_6.storage.volume_status("not_a_volume")
        assert not dsm_6.storage.volume_device_type("not_a_volume")
        assert not dsm_6.storage.volume_size_total("not_a_volume")
        assert not dsm_6.storage.volume_size_total("not_a_volume", True)
        assert not dsm_6.storage.volume_size_used("not_a_volume")
        assert not dsm_6.storage.volume_size_used("not_a_volume", True)
        assert not dsm_6.storage.volume_percentage_used("not_a_volume")
        assert not dsm_6.storage.volume_disk_temp_avg("not_a_volume")
        assert not dsm_6.storage.volume_disk_temp_max("not_a_volume")

        # Test volume
        assert dsm_6.storage.volume_status("test_volume") is None
        assert dsm_6.storage.volume_device_type("test_volume") is None
        assert dsm_6.storage.volume_size_total("test_volume") is None
        assert dsm_6.storage.volume_size_total("test_volume", True) is None
        assert dsm_6.storage.volume_size_used("test_volume") is None
        assert dsm_6.storage.volume_size_used("test_volume", True) is None
        assert dsm_6.storage.volume_percentage_used("test_volume") is None
        assert dsm_6.storage.volume_disk_temp_avg("test_volume") is None
        assert dsm_6.storage.volume_disk_temp_max("test_volume") is None

    @pytest.mark.asyncio
    async def test_storage_shr_volumes(self, dsm_6):
        """Test SHR storage volumes."""
        assert await dsm_6.login()
        dsm_6.disks_redundancy = "SHR1"
        await dsm_6.storage.update()

        # Basics
        assert dsm_6.storage.volumes_ids
        for volume_id in dsm_6.storage.volumes_ids:
            if volume_id == "test_volume":
                continue
            assert dsm_6.storage.volume_status(volume_id)
            assert dsm_6.storage.volume_device_type(volume_id)
            assert dsm_6.storage.volume_size_total(volume_id)
            assert dsm_6.storage.volume_size_total(volume_id, True)
            assert dsm_6.storage.volume_size_used(volume_id)
            assert dsm_6.storage.volume_size_used(volume_id, True)
            assert dsm_6.storage.volume_percentage_used(volume_id)
            assert dsm_6.storage.volume_disk_temp_avg(volume_id)
            assert dsm_6.storage.volume_disk_temp_max(volume_id)

        # Existing volume
        assert dsm_6.storage.volume_status("volume_1") == "normal"
        assert (
            dsm_6.storage.volume_device_type("volume_1") == "shr_without_disk_protect"
        )
        assert dsm_6.storage.volume_size_total("volume_1") == 2948623499264
        assert dsm_6.storage.volume_size_total("volume_1", True) == "2.7Tb"
        assert dsm_6.storage.volume_size_used("volume_1") == 2710796488704
        assert dsm_6.storage.volume_size_used("volume_1", True) == "2.5Tb"
        assert dsm_6.storage.volume_percentage_used("volume_1") == 91.9
        assert dsm_6.storage.volume_disk_temp_avg("volume_1") == 29.0
        assert dsm_6.storage.volume_disk_temp_max("volume_1") == 29

        assert dsm_6.storage.volume_status("volume_2") == "normal"
        assert (
            dsm_6.storage.volume_device_type("volume_2") == "shr_without_disk_protect"
        )
        assert dsm_6.storage.volume_size_total("volume_2") == 1964124495872
        assert dsm_6.storage.volume_size_total("volume_2", True) == "1.8Tb"
        assert dsm_6.storage.volume_size_used("volume_2") == 1684179374080
        assert dsm_6.storage.volume_size_used("volume_2", True) == "1.5Tb"
        assert dsm_6.storage.volume_percentage_used("volume_2") == 85.7
        assert dsm_6.storage.volume_disk_temp_avg("volume_2") == 30.0
        assert dsm_6.storage.volume_disk_temp_max("volume_2") == 30

        # Non existing volume
        assert not dsm_6.storage.volume_status("not_a_volume")
        assert not dsm_6.storage.volume_device_type("not_a_volume")
        assert not dsm_6.storage.volume_size_total("not_a_volume")
        assert not dsm_6.storage.volume_size_total("not_a_volume", True)
        assert not dsm_6.storage.volume_size_used("not_a_volume")
        assert not dsm_6.storage.volume_size_used("not_a_volume", True)
        assert not dsm_6.storage.volume_percentage_used("not_a_volume")
        assert not dsm_6.storage.volume_disk_temp_avg("not_a_volume")
        assert not dsm_6.storage.volume_disk_temp_max("not_a_volume")

        # Test volume
        assert dsm_6.storage.volume_status("test_volume") is None
        assert dsm_6.storage.volume_device_type("test_volume") is None
        assert dsm_6.storage.volume_size_total("test_volume") is None
        assert dsm_6.storage.volume_size_total("test_volume", True) is None
        assert dsm_6.storage.volume_size_used("test_volume") is None
        assert dsm_6.storage.volume_size_used("test_volume", True) is None
        assert dsm_6.storage.volume_percentage_used("test_volume") is None
        assert dsm_6.storage.volume_disk_temp_avg("test_volume") is None
        assert dsm_6.storage.volume_disk_temp_max("test_volume") is None

    @pytest.mark.asyncio
    async def test_storage_shr2_volumes(self, dsm_6):
        """Test SHR2 storage volumes."""
        assert await dsm_6.login()
        dsm_6.disks_redundancy = "SHR2"
        await dsm_6.storage.update()

        # Basics
        assert dsm_6.storage.volumes_ids
        for volume_id in dsm_6.storage.volumes_ids:
            assert dsm_6.storage.volume_status(volume_id)
            assert dsm_6.storage.volume_device_type(volume_id)
            assert dsm_6.storage.volume_size_total(volume_id)
            assert dsm_6.storage.volume_size_total(volume_id, True)
            assert dsm_6.storage.volume_size_used(volume_id)
            assert dsm_6.storage.volume_size_used(volume_id, True)
            assert dsm_6.storage.volume_percentage_used(volume_id)
            assert dsm_6.storage.volume_disk_temp_avg(volume_id)
            assert dsm_6.storage.volume_disk_temp_max(volume_id)

        # Existing volume
        assert dsm_6.storage.volume_status("volume_1") == "normal"
        assert dsm_6.storage.volume_device_type("volume_1") == "shr_with_2_disk_protect"
        assert dsm_6.storage.volume_size_total("volume_1") == 38378964738048
        assert dsm_6.storage.volume_size_total("volume_1", True) == "34.9Tb"
        assert dsm_6.storage.volume_size_used("volume_1") == 26724878606336
        assert dsm_6.storage.volume_size_used("volume_1", True) == "24.3Tb"
        assert dsm_6.storage.volume_percentage_used("volume_1") == 69.6
        assert dsm_6.storage.volume_disk_temp_avg("volume_1") == 37.0
        assert dsm_6.storage.volume_disk_temp_max("volume_1") == 41

    @pytest.mark.asyncio
    async def test_storage_shr2_expansion_volumes(self, dsm_6):
        """Test SHR2 storage with expansion unit volumes."""
        assert await dsm_6.login()
        dsm_6.disks_redundancy = "SHR2_EXPANSION"
        await dsm_6.storage.update()

        # Basics
        assert dsm_6.storage.volumes_ids
        for volume_id in dsm_6.storage.volumes_ids:
            assert dsm_6.storage.volume_status(volume_id)
            assert dsm_6.storage.volume_device_type(volume_id)
            assert dsm_6.storage.volume_size_total(volume_id)
            assert dsm_6.storage.volume_size_total(volume_id, True)
            assert dsm_6.storage.volume_size_used(volume_id)
            assert dsm_6.storage.volume_size_used(volume_id, True)
            assert dsm_6.storage.volume_percentage_used(volume_id)
            assert dsm_6.storage.volume_disk_temp_avg(volume_id)
            assert dsm_6.storage.volume_disk_temp_max(volume_id)

        # Existing volume
        assert dsm_6.storage.volume_status("volume_1") == "normal"
        assert dsm_6.storage.volume_device_type("volume_1") == "shr_with_2_disk_protect"
        assert dsm_6.storage.volume_size_total("volume_1") == 31714659872768
        assert dsm_6.storage.volume_size_total("volume_1", True) == "28.8Tb"
        assert dsm_6.storage.volume_size_used("volume_1") == 25419707531264
        assert dsm_6.storage.volume_size_used("volume_1", True) == "23.1Tb"
        assert dsm_6.storage.volume_percentage_used("volume_1") == 80.2
        assert dsm_6.storage.volume_disk_temp_avg("volume_1") == 33.0
        assert dsm_6.storage.volume_disk_temp_max("volume_1") == 35

    @pytest.mark.asyncio
    async def test_storage_disks(self, dsm_6):
        """Test storage disks."""
        assert await dsm_6.login()
        await dsm_6.storage.update()
        # Basics
        assert dsm_6.storage.disks_ids
        for disk_id in dsm_6.storage.disks_ids:
            if disk_id == "test_disk":
                continue
            assert "Drive" in dsm_6.storage.disk_name(disk_id)
            assert "/dev/" in dsm_6.storage.disk_device(disk_id)
            assert dsm_6.storage.disk_smart_status(disk_id) == "normal"
            assert dsm_6.storage.disk_status(disk_id) == "normal"
            assert not dsm_6.storage.disk_exceed_bad_sector_thr(disk_id)
            assert not dsm_6.storage.disk_below_remain_life_thr(disk_id)
            assert dsm_6.storage.disk_temp(disk_id)

        # Non existing disk
        assert not dsm_6.storage.disk_name("not_a_disk")
        assert not dsm_6.storage.disk_device("not_a_disk")
        assert not dsm_6.storage.disk_smart_status("not_a_disk")
        assert not dsm_6.storage.disk_status("not_a_disk")
        assert not dsm_6.storage.disk_exceed_bad_sector_thr("not_a_disk")
        assert not dsm_6.storage.disk_below_remain_life_thr("not_a_disk")
        assert not dsm_6.storage.disk_temp("not_a_disk")

        # Test disk
        assert dsm_6.storage.disk_name("test_disk") is None
        assert dsm_6.storage.disk_device("test_disk") is None
        assert dsm_6.storage.disk_smart_status("test_disk") is None
        assert dsm_6.storage.disk_status("test_disk") is None
        assert dsm_6.storage.disk_exceed_bad_sector_thr("test_disk") is None
        assert dsm_6.storage.disk_below_remain_life_thr("test_disk") is None
        assert dsm_6.storage.disk_temp("test_disk") is None

    @pytest.mark.asyncio
    async def test_external_usb(self, dsm_6):
        """Test external USB storage devices."""
        assert await dsm_6.login()
        assert dsm_6.external_usb
        await dsm_6.external_usb.update()
        assert dsm_6.external_usb.devices
        for device_id in dsm_6.external_usb.device_ids:
            assert dsm_6.external_usb.device_name(device_id)
            assert dsm_6.external_usb.device_type(device_id)
            assert dsm_6.external_usb.device_status(device_id)
            assert dsm_6.external_usb.device_size_total(device_id, human_readable=True)
            assert dsm_6.external_usb.producer(device_id)
            assert dsm_6.external_usb.product_name(device_id)
            assert dsm_6.external_usb.device_formatable(device_id)
            assert not dsm_6.external_usb.device_progress(device_id)
            for partition in dsm_6.external_usb.device_partitions(device_id):
                assert partition.name_id
                assert partition.partition_title
                assert partition.share_name
                assert partition.filesystem
                assert partition.fstype
                assert partition.status
                assert partition.partition_size_total(human_readable=True)
                assert partition.partition_size_used(human_readable=True)

        assert dsm_6.external_usb.producer("usb1") == "PNY"
        assert dsm_6.external_usb.product_name("usb1") == "Flash Drive"
        assert dsm_6.external_usb.device_size_total("usb1") == 127999672320.0
        assert dsm_6.external_usb.device_size_total("usb1", True) == "119.2Gb"

        assert dsm_6.external_usb.device_name("usb1") == "USB Disk 1"
        assert dsm_6.external_usb.device_type("usb1") == "usbDisk"
        assert (
            dsm_6.external_usb.device_partition("usb1", "usb1p1").share_name
            == "usbshare1-1"
        )
        assert (
            dsm_6.external_usb.device_partition("usb1", "usb1p1").filesystem == "ntfs"
        )
        assert (
            dsm_6.external_usb.device_partition("usb1", "usb1p2").share_name
            == "usbshare1-2"
        )
        assert (
            dsm_6.external_usb.device_partition("usb1", "usb1p2").filesystem == "FAT32"
        )

    @pytest.mark.asyncio
    async def test_download_station(self, dsm_6):
        """Test DownloadStation."""
        assert await dsm_6.login()
        assert dsm_6.download_station
        assert not dsm_6.download_station.get_all_tasks()

        assert (await dsm_6.download_station.get_info())["data"]["version"]
        assert (await dsm_6.download_station.get_config())["data"][
            "default_destination"
        ]
        assert (await dsm_6.download_station.get_stat())["data"]["speed_download"]
        await dsm_6.download_station.update()
        assert dsm_6.download_station.get_all_tasks()
        assert len(dsm_6.download_station.get_all_tasks()) == 8

        # BT DL
        assert dsm_6.download_station.get_task("dbid_86").status == "downloading"
        assert not dsm_6.download_station.get_task("dbid_86").status_extra
        assert dsm_6.download_station.get_task("dbid_86").type == "bt"
        assert dsm_6.download_station.get_task("dbid_86").additional.get("file")
        assert (
            len(dsm_6.download_station.get_task("dbid_86").additional.get("file")) == 9
        )

        # HTTPS error
        assert dsm_6.download_station.get_task("dbid_549").status == "error"
        assert (
            dsm_6.download_station.get_task("dbid_549").status_extra["error_detail"]
            == "broken_link"
        )
        assert dsm_6.download_station.get_task("dbid_549").type == "https"

    @pytest.mark.asyncio
    async def test_surveillance_station(self, dsm_6):
        """Test SurveillanceStation."""
        dsm_6.with_surveillance = True
        assert await dsm_6.login()
        assert dsm_6.surveillance_station
        assert not dsm_6.surveillance_station.get_all_cameras()

        await dsm_6.surveillance_station.update()
        assert dsm_6.surveillance_station.get_all_cameras()
        assert dsm_6.surveillance_station.get_camera(1)
        assert dsm_6.surveillance_station.get_camera_live_view_path(1)
        assert dsm_6.surveillance_station.get_camera_live_view_path(1, "rtsp")

        # Motion detection
        assert (await dsm_6.surveillance_station.enable_motion_detection(1)).get(
            "success"
        )
        assert (await dsm_6.surveillance_station.disable_motion_detection(1)).get(
            "success"
        )

        # Home mode
        assert await dsm_6.surveillance_station.get_home_mode_status()
        assert await dsm_6.surveillance_station.set_home_mode(False)
        assert await dsm_6.surveillance_station.set_home_mode(True)
