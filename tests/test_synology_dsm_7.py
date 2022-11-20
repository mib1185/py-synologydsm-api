"""Synology DSM tests."""
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
    VALID_VERIFY_SSL,
    SynologyDSMMock,
)
from .const import DEVICE_TOKEN, SESSION_ID, SYNO_TOKEN


class TestSynologyDSM7:
    """SynologyDSM 7 test cases."""

    def test_login(self, dsm_7):
        """Test login."""
        assert dsm_7.login()
        assert dsm_7.apis.get(API_AUTH)
        assert dsm_7._session_id == SESSION_ID
        assert dsm_7._syno_token == SYNO_TOKEN

    def test_login_2sa(self):
        """Test login with 2SA."""
        dsm_7 = SynologyDSMMock(
            VALID_HOST,
            VALID_PORT,
            VALID_USER_2SA,
            VALID_PASSWORD,
            VALID_HTTPS,
            VALID_VERIFY_SSL,
        )
        dsm_7.dsm_version = 7
        with pytest.raises(SynologyDSMLogin2SARequiredException) as error:
            dsm_7.login()
        error_value = error.value.args[0]
        assert error_value["api"] == "SYNO.API.Auth"
        assert error_value["code"] == 403
        assert error_value["reason"] == "One time password not specified"
        assert (
            error_value["details"]
            == "Two-step authentication required for account: valid_user_2sa"
        )

        assert dsm_7.login(VALID_OTP)

        assert dsm_7._session_id == SESSION_ID
        assert dsm_7._syno_token == SYNO_TOKEN
        assert dsm_7._device_token == DEVICE_TOKEN
        assert dsm_7.device_token == DEVICE_TOKEN

    def test_login_2sa_new_session(self):
        """Test login with 2SA and a new session with granted device."""
        dsm_7 = SynologyDSMMock(
            VALID_HOST,
            VALID_PORT,
            VALID_USER_2SA,
            VALID_PASSWORD,
            VALID_HTTPS,
            VALID_VERIFY_SSL,
            device_token=DEVICE_TOKEN,
        )
        dsm_7.dsm_version = 7
        assert dsm_7.login()

        assert dsm_7._session_id == SESSION_ID
        assert dsm_7._syno_token == SYNO_TOKEN
        assert dsm_7._device_token == DEVICE_TOKEN
        assert dsm_7.device_token == DEVICE_TOKEN

    def test_upgrade(self, dsm_7):
        """Test upgrade."""
        assert dsm_7.upgrade
        dsm_7.upgrade.update()
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
