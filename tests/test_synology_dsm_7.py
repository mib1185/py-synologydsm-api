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


class TestSynologyDSM7:
    """SynologyDSM 7 test cases."""

    @pytest.mark.asyncio
    async def test_login(self, dsm_7):
        """Test login."""
        assert await dsm_7.login()
        assert dsm_7.apis.get(API_AUTH)
        assert dsm_7._session_id == SESSION_ID
        assert dsm_7._syno_token == SYNO_TOKEN

    @pytest.mark.asyncio
    async def test_login_2sa(self):
        """Test login with 2SA."""
        dsm_7 = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            VALID_USER_2SA,
            VALID_PASSWORD,
            VALID_HTTPS,
        )
        dsm_7.dsm_version = 7
        with pytest.raises(SynologyDSMLogin2SARequiredException) as error:
            await dsm_7.login()
        error_value = error.value.args[0]
        assert error_value["api"] == "SYNO.API.Auth"
        assert error_value["code"] == 403
        assert error_value["reason"] == "One time password not specified"
        assert (
            error_value["details"]
            == "Two-step authentication required for account: valid_user_2sa"
        )

        assert await dsm_7.login(VALID_OTP)

        assert dsm_7._session_id == SESSION_ID
        assert dsm_7._syno_token == SYNO_TOKEN
        assert dsm_7._device_token == DEVICE_TOKEN
        assert dsm_7.device_token == DEVICE_TOKEN

    @pytest.mark.asyncio
    async def test_external_usb(self, dsm_7):
        """Test external USB storage devices."""
        assert await dsm_7.login()
        assert dsm_7.external_usb
        await dsm_7.external_usb.update()
        assert dsm_7.external_usb.get_devices
        for device in dsm_7.external_usb.get_devices:
            assert dsm_7.external_usb.get_device(device).device_name
            assert dsm_7.external_usb.get_device(device).device_type
            assert dsm_7.external_usb.get_device(device).device_status
            assert dsm_7.external_usb.get_device(device).device_size_total(
                human_readable=True
            )
            assert dsm_7.external_usb.get_device(device).device_manufacturer
            assert dsm_7.external_usb.get_device(device).device_product_name
            assert dsm_7.external_usb.get_device(device).device_formatable
            assert not dsm_7.external_usb.get_device(device).device_progress
            for partition in dsm_7.external_usb.get_device(device).device_partitions:
                if partition.is_formatted():
                    assert partition.name_id
                    assert partition.partition_title
                    assert partition.share_name
                    assert partition.filesystem
                    assert partition.fstype
                    assert partition.status
                    assert partition.partition_size_total(human_readable=True)
                    assert partition.partition_size_used(human_readable=True)

        assert dsm_7.external_usb.get_device("usb1").device_manufacturer == "PNY"
        assert (
            dsm_7.external_usb.get_device("usb1").device_product_name == "Flash Drive"
        )
        assert (
            dsm_7.external_usb.get_device("usb1").device_size_total(
                human_readable=False
            )
            == 127999672320.0
        )
        assert (
            dsm_7.external_usb.get_device("usb1").device_size_total(human_readable=True)
            == "119.2Gb"
        )

        assert dsm_7.external_usb.get_device("usb1").device_name == "USB Disk 1"
        assert dsm_7.external_usb.get_device("usb1").device_type == "usbDisk"
        assert (
            dsm_7.external_usb.get_device("usb1")
            .get_device_partition("usb1p1")
            .share_name
            == "usbshare1-1"
        )
        assert (
            dsm_7.external_usb.get_device("usb1")
            .get_device_partition("usb1p1")
            .filesystem
            == "ntfs"
        )
        assert (
            dsm_7.external_usb.get_device("usb1")
            .get_device_partition("usb1p2")
            .share_name
            == "usbshare1-2"
        )
        assert (
            dsm_7.external_usb.get_device("usb1")
            .get_device_partition("usb1p2")
            .filesystem
            == "FAT32"
        )
        assert (
            dsm_7.external_usb.get_device("usb1")
            .get_device_partition("usb1p2")
            .partition_size_total(False)
            == 1073741824.0
        )

        # Unformatted device partition
        assert (
            dsm_7.external_usb.get_device("usb8")
            .get_device_partition("usb8")
            .is_formatted()
            is False
        )
        assert (
            dsm_7.external_usb.get_device("usb8")
            .get_device_partition("usb8")
            .partition_size_total(False)
            is None
        )
        assert (
            dsm_7.external_usb.get_device("usb8")
            .get_device_partition("usb8")
            .partition_size_used(False)
            is None
        )
        assert (
            dsm_7.external_usb.get_device("usb8")
            .get_device_partition("usb8")
            .partition_percentage_used
            is None
        )

    @pytest.mark.asyncio
    async def test_login_2sa_new_session(self):
        """Test login with 2SA and a new session with granted device."""
        dsm_7 = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            VALID_USER_2SA,
            VALID_PASSWORD,
            VALID_HTTPS,
            device_token=DEVICE_TOKEN,
        )
        dsm_7.dsm_version = 7
        assert await dsm_7.login()

        assert dsm_7._session_id == SESSION_ID
        assert dsm_7._syno_token == SYNO_TOKEN
        assert dsm_7._device_token == DEVICE_TOKEN
        assert dsm_7.device_token == DEVICE_TOKEN

    @pytest.mark.asyncio
    async def test_upgrade(self, dsm_7):
        """Test upgrade."""
        assert await dsm_7.login()
        assert dsm_7.upgrade
        await dsm_7.upgrade.update()
        assert dsm_7.upgrade.update_available
        assert dsm_7.upgrade.available_version == "7.0.1-42218 Update 3"
        assert dsm_7.upgrade.reboot_needed == "now"
        assert dsm_7.upgrade.service_restarts == "some"
        assert dsm_7.upgrade.available_version_details == {
            "buildnumber": 42218,
            "major": 7,
            "micro": 1,
            "minor": 0,
            "nano": 3,
            "os_name": "DSM",
        }

    @pytest.mark.asyncio
    async def test_photos(self, dsm_7):
        """Test photos."""
        assert await dsm_7.login()
        assert dsm_7.photos
        albums = await dsm_7.photos.get_albums()

        assert albums
        assert len(albums) == 2
        assert albums[0].album_id == 4
        assert albums[0].name == "Album1"
        assert albums[0].item_count == 3
        assert albums[1].album_id == 1
        assert albums[1].name == "Album2"
        assert albums[1].item_count == 1

        items = await dsm_7.photos.get_items_from_album(albums[0])
        assert items
        assert len(items) == 3
        assert items[0].file_name == "20221115_185642.jpg"
        assert items[0].thumbnail_cache_key == "29807_1668560967"
        assert items[0].thumbnail_size == "xl"
        assert items[1].file_name == "20221115_185643.jpg"
        assert items[1].thumbnail_cache_key == "29808_1668560967"
        assert items[1].thumbnail_size == "m"
        assert items[2].file_name == "20221115_185644.jpg"
        assert items[2].thumbnail_cache_key == "29809_1668560967"
        assert items[2].thumbnail_size == "sm"

        thumb_url = await dsm_7.photos.get_item_thumbnail_url(items[0])
        assert thumb_url
        assert thumb_url == (
            "https://nas.mywebsite.me:443/webapi/entry.cgi?"
            "id=29807&cache_key=29807_1668560967&size=xl&type=unit"
            "&api=SYNO.Foto.Thumbnail&version=2&method=get"
            "&_sid=session_id&SynoToken=Sy%C3%B10_T0k%E2%82%AC%C3%B1"
        )

        items = await dsm_7.photos.get_items_from_search(albums[0])
        assert items
        assert len(items) == 2
        assert items[0].file_name == "search_1.jpg"
        assert items[0].thumbnail_cache_key == "12340_1668560967"
        assert items[1].file_name == "search_2.jpg"
        assert items[1].thumbnail_cache_key == "12341_1668560967"
