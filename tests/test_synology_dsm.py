"""Synology DSM tests."""

# pylint: disable=protected-access
import logging
from types import SimpleNamespace

import pytest
from aiohttp import ClientTimeout

from synology_dsm import SynologyDSM
from synology_dsm.api.core.external_usb import SynoCoreExternalUSB
from synology_dsm.api.core.hardware import SynoCoreHardware
from synology_dsm.api.core.security import SynoCoreSecurity
from synology_dsm.api.core.share import SynoCoreShare
from synology_dsm.api.core.system import SynoCoreSystem
from synology_dsm.api.core.upgrade import SynoCoreUpgrade
from synology_dsm.api.core.utilization import SynoCoreUtilization
from synology_dsm.api.download_station import SynoDownloadStation
from synology_dsm.api.dsm.information import SynoDSMInformation
from synology_dsm.api.photos import SynoPhotos
from synology_dsm.api.storage.storage import SynoStorage
from synology_dsm.api.surveillance_station import SynoSurveillanceStation
from synology_dsm.const import API_AUTH, API_INFO, SENSITIV_PARAMS
from synology_dsm.exceptions import (
    SynologyDSMAPIErrorException,
    SynologyDSMAPIInsufficientPrivilegeException,
    SynologyDSMAPINoDataException,
    SynologyDSMAPINotExistsException,
    SynologyDSMLogin2SAFailedException,
    SynologyDSMLogin2SARequiredException,
    SynologyDSMLoginFailedException,
    SynologyDSMLoginInvalidException,
    SynologyDSMNotLoggedInException,
    SynologyDSMRequestException,
)

from . import (
    USER_MAX_TRY,
    VALID_HOST,
    VALID_HTTPS,
    VALID_OTP,
    VALID_PASSWORD,
    VALID_PORT,
    VALID_USER,
    VALID_USER_2SA,
    SynologyDSMMock,
)
from .api_data.dsm_7 import DSM_7_API_INFO, DSM_7_AUTH_LOGIN, DSM_7_DSM_INFORMATION
from .const import DEVICE_TOKEN, SESSION_ID, SYNO_TOKEN


class FakeResponse:
    """Fake aiohttp response returned by the FakeSession."""

    def __init__(self, url, payload):
        """Constructor method."""
        self.status = 200
        self.headers = {"Content-Type": "application/json"}
        self.url = url
        self.request_info = SimpleNamespace(headers={})
        self._payload = payload

    async def json(self, content_type=None):
        """Return the canned json payload."""
        return self._payload


class FakeSession:
    """Fake aiohttp session which records the requests it receives."""

    def __init__(self):
        """Constructor method."""
        self.requests = []

    def _handle(self, method, url, **kwargs):
        self.requests.append((method, url, kwargs))
        api = url.query.get("api")
        if api == API_INFO:
            payload = DSM_7_API_INFO
        elif api == API_AUTH:
            payload = DSM_7_AUTH_LOGIN
        elif api == SynoDSMInformation.API_KEY:
            payload = DSM_7_DSM_INFORMATION
        else:
            payload = {"data": {}, "success": True}
        return FakeResponse(url, payload)

    async def get(self, url, **kwargs):
        """Record a GET request and return a fake response."""
        return self._handle("GET", url, **kwargs)

    async def post(self, url, **kwargs):
        """Record a POST request and return a fake response."""
        return self._handle("POST", url, **kwargs)


class TestSynologyDSM:
    """Common SynologyDSM 5 and 6 test cases."""

    def test_init(self, dsm):
        """Test init."""
        assert dsm.username == VALID_USER
        assert str(dsm._base_url) == f"https://{VALID_HOST}:{VALID_PORT}"
        assert dsm._aiohttp_timeout.total == 10
        assert not dsm.apis.get(API_AUTH)
        assert not dsm._session_id

    def test_sensitive_params(self):
        """Test secret request parameters are masked in debug logs."""
        for param in (
            "account",
            "passwd",
            "_sid",
            "SynoToken",
            "device_id",
            "otp_code",
            "unzip_password",
            "passphrase",
        ):
            assert param in SENSITIV_PARAMS

    @pytest.mark.parametrize("version", [5, 6, 7])
    @pytest.mark.asyncio
    async def test_login_neccessary(self, version):
        """Test login is neccessary."""
        dsm = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            USER_MAX_TRY,
            VALID_PASSWORD,
            VALID_HTTPS,
        )
        dsm.dsm_version = version

        with pytest.raises(SynologyDSMNotLoggedInException) as error:
            await dsm.utilisation.update()
        error_value = error.value.args[0]
        assert error_value["api"] is None
        assert error_value["code"] == -1
        assert error_value["reason"] == "Unknown"
        assert error_value["details"] == "Not logged in. You have to do login() first."

    @pytest.mark.parametrize("version", [5, 6, 7])
    @pytest.mark.asyncio
    async def test_logout(self, version):
        """Test logout clears the session credential."""
        dsm = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            VALID_USER,
            VALID_PASSWORD,
            VALID_HTTPS,
        )
        dsm.dsm_version = version
        assert await dsm.login()
        assert dsm._session_id

        assert await dsm.logout()
        assert dsm._session_id is None
        assert dsm._syno_token is None

        # the forgotten credential can neither be sent nor embedded in urls
        with pytest.raises(SynologyDSMNotLoggedInException):
            await dsm.utilisation.update()
        with pytest.raises(SynologyDSMNotLoggedInException):
            await dsm.generate_url("SYNO.DownloadStation2.Task", "list")

        # without a session there is nothing left to log out from
        assert not await dsm.logout()

    @pytest.mark.parametrize("version", [5, 6, 7])
    @pytest.mark.asyncio
    async def test_logout_request_failed(self, version, monkeypatch):
        """Test logout clears the session credential even if the request fails."""
        dsm = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            VALID_USER,
            VALID_PASSWORD,
            VALID_HTTPS,
        )
        dsm.dsm_version = version
        assert await dsm.login()
        assert dsm._session_id

        async def _failing_request(*args, **kwargs):
            raise SynologyDSMRequestException(TimeoutError())

        monkeypatch.setattr(dsm, "_execute_request", _failing_request)

        with pytest.raises(SynologyDSMRequestException):
            await dsm.logout()
        assert dsm._session_id is None
        assert dsm._syno_token is None

    @pytest.mark.parametrize("version", [5, 6, 7])
    @pytest.mark.asyncio
    async def test_login_basic_failed(self, version):
        """Test basic failed login."""
        dsm = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            USER_MAX_TRY,
            VALID_PASSWORD,
            VALID_HTTPS,
        )
        dsm.dsm_version = version

        with pytest.raises(SynologyDSMLoginFailedException) as error:
            await dsm.login()
        error_value = error.value.args[0]
        assert error_value["api"] == "SYNO.API.Auth"
        assert error_value["code"] == 407
        assert error_value["reason"] == "Max Tries (if auto blocking is set to true)"
        assert error_value["details"] == USER_MAX_TRY

    @pytest.mark.parametrize("version", [5, 6, 7])
    @pytest.mark.asyncio
    async def test_login_2sa_failed(self, version):
        """Test failed login with 2SA."""
        dsm = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            VALID_USER_2SA,
            VALID_PASSWORD,
            VALID_HTTPS,
        )
        dsm.dsm_version = version

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

        with pytest.raises(SynologyDSMLogin2SAFailedException) as error:
            await dsm.login(888888)
        error_value = error.value.args[0]
        assert error_value["api"] == "SYNO.API.Auth"
        assert error_value["code"] == 404
        assert error_value["reason"] == "One time password authenticate failed"
        assert (
            error_value["details"]
            == "Two-step authentication failed, retry with a new pass code"
        )

        assert dsm._session_id is None
        assert dsm._syno_token is None
        assert dsm._device_token is None

    @pytest.mark.parametrize("version", [5, 6, 7])
    @pytest.mark.asyncio
    async def test_login_debug_log_masks_credentials(self, version, caplog):
        """Test the auth response and session id are not written to the log."""
        dsm = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            VALID_USER_2SA,
            VALID_PASSWORD,
            VALID_HTTPS,
        )
        dsm.dsm_version = version

        with caplog.at_level(logging.DEBUG):
            assert await dsm.login(VALID_OTP)

        assert dsm._session_id == SESSION_ID
        assert dsm.device_token == DEVICE_TOKEN
        assert "Authentication successful" in caplog.text
        assert "RESPONSE: <masked SYNO.API.Auth response>" in caplog.text
        assert SESSION_ID not in caplog.text
        assert SYNO_TOKEN not in caplog.text
        assert DEVICE_TOKEN not in caplog.text

    @pytest.mark.parametrize("version", [5, 6, 7])
    @pytest.mark.asyncio
    async def test_connection_failed(self, version):
        """Test failed connection."""
        # No internet
        dsm = SynologyDSMMock(
            None,
            "no_internet",
            VALID_PORT,
            VALID_USER,
            VALID_PASSWORD,
            VALID_HTTPS,
        )
        dsm.dsm_version = version
        with pytest.raises(SynologyDSMRequestException) as error:
            await dsm.login()
        error_value = error.value.args[0]
        assert not error_value["api"]
        assert error_value["code"] == -1
        assert error_value["reason"] == "Unknown"
        assert (
            "ClientError = <urllib3.connection.VerifiedHTTPSConnection "
            in error_value["details"]
        )

        assert not dsm.apis.get(API_AUTH)
        assert not dsm._session_id

        # Wrong host
        dsm = SynologyDSMMock(
            None,
            "host",
            VALID_PORT,
            VALID_USER,
            VALID_PASSWORD,
            VALID_HTTPS,
        )
        dsm.dsm_version = version
        with pytest.raises(SynologyDSMRequestException) as error:
            await dsm.login()
        error_value = error.value.args[0]
        assert not error_value["api"]
        assert error_value["code"] == -1
        assert error_value["reason"] == "Unknown"
        assert (
            "ClientError = <urllib3.connection.HTTPConnection "
            in error_value["details"]
        )

        assert not dsm.apis.get(API_AUTH)
        assert not dsm._session_id

        # Wrong port
        dsm = SynologyDSMMock(
            None,
            VALID_HOST,
            0,
            VALID_USER,
            VALID_PASSWORD,
            VALID_HTTPS,
        )
        dsm.dsm_version = version
        with pytest.raises(SynologyDSMRequestException) as error:
            await dsm.login()
        error_value = error.value.args[0]
        assert not error_value["api"]
        assert error_value["code"] == -1
        assert error_value["reason"] == "Unknown"
        assert error_value["details"] == (
            "ClientError = [SSL: WRONG_VERSION_NUMBER] "
            "wrong version number (_ssl.c:1076)"
        )

        assert not dsm.apis.get(API_AUTH)
        assert not dsm._session_id

        # Wrong HTTPS
        dsm = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            VALID_USER,
            VALID_PASSWORD,
            False,
        )
        dsm.dsm_version = version
        with pytest.raises(SynologyDSMRequestException) as error:
            await dsm.login()
        error_value = error.value.args[0]
        assert not error_value["api"]
        assert error_value["code"] == -1
        assert error_value["reason"] == "Unknown"
        assert error_value["details"] == "ClientError = Bad request"

        assert not dsm.apis.get(API_AUTH)
        assert not dsm._session_id

    @pytest.mark.parametrize("version", [5, 6, 7])
    @pytest.mark.asyncio
    async def test_login_failed(self, version):
        """Test failed login."""
        dsm = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            "user",
            VALID_PASSWORD,
            VALID_HTTPS,
        )
        dsm.dsm_version = version
        with pytest.raises(SynologyDSMLoginInvalidException) as error:
            await dsm.login()
        error_value = error.value.args[0]
        assert error_value["api"] == "SYNO.API.Auth"
        assert error_value["code"] == 400
        assert error_value["reason"] == "Invalid credentials"
        assert error_value["details"] == "Invalid password or not admin account: user"

        assert dsm.apis.get(API_AUTH)
        assert not dsm._session_id

        dsm = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            VALID_USER,
            "pass",
            VALID_HTTPS,
        )
        dsm.dsm_version = version
        with pytest.raises(SynologyDSMLoginInvalidException) as error:
            await dsm.login()
        error_value = error.value.args[0]
        assert error_value["api"] == "SYNO.API.Auth"
        assert error_value["code"] == 400
        assert error_value["reason"] == "Invalid credentials"
        assert (
            error_value["details"]
            == "Invalid password or not admin account: valid_user"
        )

        assert dsm.apis.get(API_AUTH)
        assert not dsm._session_id

    @pytest.mark.parametrize("version", [5, 6, 7])
    @pytest.mark.parametrize(
        "timeout,expected_result",
        [
            (2, (2, None)),
            (15, (15, None)),
            (ClientTimeout(total=5), (5, None)),
            (ClientTimeout(total=60, connect=15), (60, 15)),
        ],
    )
    def test_request_timeout(self, version, timeout, expected_result):
        """Test request timeout."""
        dsm = SynologyDSMMock(
            None,
            VALID_HOST,
            VALID_PORT,
            VALID_USER,
            VALID_PASSWORD,
            VALID_HTTPS,
            timeout=timeout,
        )
        dsm.dsm_version = version
        assert dsm._aiohttp_timeout.total == expected_result[0]
        assert dsm._aiohttp_timeout.connect == expected_result[1]

    @pytest.mark.asyncio
    async def test_request_get(self, dsm):
        """Test get request."""
        await dsm.login()
        assert await dsm.get(API_INFO, "query")
        assert await dsm.get(API_AUTH, "login")
        assert await dsm.get("SYNO.DownloadStation2.Task", "list")
        assert await dsm.get(API_AUTH, "logout")

    @pytest.mark.asyncio
    async def test_request_get_failed(self, dsm):
        """Test failed get request."""
        await dsm.login()
        with pytest.raises(SynologyDSMAPINotExistsException) as error:
            await dsm.get("SYNO.Virtualization.API.Task.Info", "list")
        error_value = error.value.args[0]
        assert error_value["api"] == "SYNO.Virtualization.API.Task.Info"
        assert error_value["code"] == -2
        assert error_value["reason"] == "Unknown"
        assert (
            error_value["details"]
            == "API SYNO.Virtualization.API.Task.Info does not exists"
        )

    @pytest.mark.asyncio
    async def test_request_post(self, dsm):
        """Test post request."""
        await dsm.login()
        assert await dsm.post(
            "SYNO.FileStation.Upload",
            "upload",
            params={"dest_folder_path": "/upload/test", "create_parents": True},
            files={"file": "open('file.txt','rb')"},
        )

        assert await dsm.post(
            "SYNO.DownloadStation2.Task",
            "create",
            params={
                "uri": "ftps://192.0.0.1:21/test/test.zip",
                "username": "admin",
                "password": "1234",
            },
        )

    @pytest.mark.asyncio
    async def test_request_post_failed(self, dsm):
        """Test failed post request."""
        await dsm.login()
        with pytest.raises(SynologyDSMAPIErrorException) as error:
            await dsm.post(
                "SYNO.FileStation.Upload",
                "upload",
                params={"dest_folder_path": "/upload/test", "create_parents": True},
                files={"file": "open('file_already_exists.txt','rb')"},
            )
        error_value = error.value.args[0]
        assert error_value["api"] == "SYNO.FileStation.Upload"
        assert error_value["code"] == 1805
        assert error_value["reason"] == (
            "Can’t overwrite or skip the existed file, if no overwrite"
            " parameter is given"
        )
        assert not error_value["details"]

        with pytest.raises(SynologyDSMAPIErrorException) as error:
            await dsm.post(
                "SYNO.DownloadStation2.Task",
                "create",
                params={
                    "uri": "ftps://192.0.0.1:21/test/test_not_exists.zip",
                    "username": "admin",
                    "password": "1234",
                },
            )
        error_value = error.value.args[0]
        assert error_value["api"] == "SYNO.DownloadStation2.Task"
        assert error_value["code"] == 408
        assert error_value["reason"] == "File does not exist"
        assert not error_value["details"]

    @staticmethod
    def _real_dsm(session, **kwargs):
        """Return a real SynologyDSM using the given fake session."""
        return SynologyDSM(
            session,
            VALID_HOST,
            VALID_PORT,
            VALID_USER,
            VALID_PASSWORD,
            VALID_HTTPS,
            **kwargs,
        )

    def test_mask_sensitive_params(self, dsm):
        """Test sensitive params are masked in a copy, the input is untouched."""
        params = {param: f"secret_{param}" for param in SENSITIV_PARAMS}
        params.update({"api": API_AUTH, "version": 7, "method": "login"})
        original = dict(params)

        masked = dsm._mask_sensitive_params(params)
        assert masked is not params
        assert set(masked) == set(params)
        for param in SENSITIV_PARAMS:
            assert masked[param] == "*********"
            assert f"secret_{param}" not in str(masked)
        assert masked["api"] == API_AUTH
        assert masked["version"] == 7
        assert masked["method"] == "login"
        assert params == original

    @pytest.mark.asyncio
    async def test_login_credentials_in_post_body(self, caplog):
        """Test login is a POST with the credentials only in the body."""
        caplog.set_level(logging.DEBUG)
        session = FakeSession()
        dsm = self._real_dsm(session, device_token=DEVICE_TOKEN)
        assert await dsm.login()
        assert dsm._session_id == SESSION_ID
        assert dsm._syno_token == SYNO_TOKEN

        login_requests = [
            request
            for request in session.requests
            if request[1].query.get("api") == API_AUTH
        ]
        assert len(login_requests) == 1
        method, url, kwargs = login_requests[0]
        assert method == "POST"
        assert set(url.query) == {"api", "version", "method"}
        assert url.query["method"] == "login"
        data = kwargs["data"]
        assert data["account"] == VALID_USER
        assert data["passwd"] == VALID_PASSWORD
        assert data["device_id"] == DEVICE_TOKEN
        assert data["enable_device_token"] == "yes"
        assert data["device_name"]
        assert data["mimeType"] == "application/json"

        # neither the password nor the device token reach any log message
        # (the session id is logged by the login response itself only)
        for message in caplog.messages:
            assert VALID_PASSWORD not in message
            assert DEVICE_TOKEN not in message
            if message.startswith(("Request url: ", "POST data: ")):
                assert SESSION_ID not in message
        # the logged copy of the POST body is masked, the sent body is not
        data_logs = [msg for msg in caplog.messages if msg.startswith("POST data: ")]
        assert len(data_logs) == 1
        assert VALID_USER not in data_logs[0]
        assert "'account': '*********'" in data_logs[0]
        assert "'passwd': '*********'" in data_logs[0]
        assert "'device_id': '*********'" in data_logs[0]
        assert "'enable_device_token': 'yes'" in data_logs[0]
        assert data["account"] == VALID_USER
        assert data["passwd"] == VALID_PASSWORD

    @pytest.mark.asyncio
    async def test_request_post_session_in_body(self, caplog):
        """Test POST sends session id, token and params only in the body."""
        caplog.set_level(logging.DEBUG)
        session = FakeSession()
        dsm = self._real_dsm(session, debugmode=True)
        assert await dsm.login()
        session.requests.clear()
        caplog.clear()

        assert await dsm.post(
            SynoCoreShare.API_KEY,
            "list",
            {"caller": "param", "overridden": "param"},
            data={"overridden": "data"},
        )
        method, url, kwargs = session.requests[0]
        assert method == "POST"
        assert set(url.query) == {"api", "version", "method"}
        assert url.query["api"] == SynoCoreShare.API_KEY
        assert url.query["method"] == "list"
        data = kwargs["data"]
        assert data["_sid"] == SESSION_ID
        assert data["SynoToken"] == SYNO_TOKEN
        assert data["caller"] == "param"
        assert data["overridden"] == "data"
        assert data["mimeType"] == "application/json"

        # the logged url neither contains the secrets nor a mask placeholder
        url_logs = [msg for msg in caplog.messages if msg.startswith("Request url: ")]
        assert len(url_logs) == 1
        assert SESSION_ID not in url_logs[0]
        assert "_sid" not in url_logs[0]
        assert "SynoToken" not in url_logs[0]
        assert "*********" not in url_logs[0]
        # the logged POST body masks the session id and token
        data_logs = [msg for msg in caplog.messages if msg.startswith("POST data: ")]
        assert len(data_logs) == 1
        assert SESSION_ID not in data_logs[0]
        assert SYNO_TOKEN not in data_logs[0]
        assert "'_sid': '*********'" in data_logs[0]
        assert "'SynoToken': '*********'" in data_logs[0]
        assert "'caller': 'param'" in data_logs[0]

    @pytest.mark.asyncio
    async def test_request_get_params_in_query(self, caplog):
        """Test GET still sends its parameters in the URL query."""
        caplog.set_level(logging.DEBUG)
        session = FakeSession()
        dsm = self._real_dsm(session)
        assert await dsm.login()
        session.requests.clear()
        caplog.clear()

        assert await dsm.get(SynoCoreShare.API_KEY, "list", {"caller": "param"})
        method, url, kwargs = session.requests[0]
        assert method == "GET"
        assert url.query["api"] == SynoCoreShare.API_KEY
        assert url.query["method"] == "list"
        assert url.query["caller"] == "param"
        assert url.query["_sid"] == SESSION_ID
        assert url.query["SynoToken"] == SYNO_TOKEN
        assert "data" not in kwargs

        # the logged url shows a mask placeholder instead of the secrets
        url_logs = [msg for msg in caplog.messages if msg.startswith("Request url: ")]
        assert len(url_logs) == 1
        assert SESSION_ID not in url_logs[0]
        assert "_sid=*********" in url_logs[0]
        assert "SynoToken=*********" in url_logs[0]

    def test_reset_str_attr(self, dsm):
        """Test reset with string attr."""
        assert not dsm._external_usb
        assert dsm.external_usb
        assert dsm._external_usb
        assert dsm.reset("external_usb")
        assert not dsm._external_usb

        assert not dsm._hardware
        assert dsm.hardware
        assert dsm._hardware
        assert dsm.reset("hardware")
        assert not dsm._hardware

        assert not dsm._security
        assert dsm.security
        assert dsm._security
        assert dsm.reset("security")
        assert not dsm._security

        assert not dsm._share
        assert dsm.share
        assert dsm._share
        assert dsm.reset("share")
        assert not dsm._share

        assert not dsm._system
        assert dsm.system
        assert dsm._system
        assert dsm.reset("system")
        assert not dsm._system

        assert not dsm._upgrade
        assert dsm.upgrade
        assert dsm._upgrade
        assert dsm.reset("upgrade")
        assert not dsm._upgrade

        assert not dsm._utilisation
        assert dsm.utilisation
        assert dsm._utilisation
        assert dsm.reset("utilisation")
        assert not dsm._utilisation

        assert not dsm._download
        assert dsm.download_station
        assert dsm._download
        assert dsm.reset("download")
        assert not dsm._download

        assert not dsm._photos
        assert dsm.photos
        assert dsm._photos
        assert dsm.reset("photos")
        assert not dsm._photos

        assert not dsm._storage
        assert dsm.storage
        assert dsm._storage
        assert dsm.reset("storage")
        assert not dsm._storage

        assert not dsm._surveillance
        assert dsm.surveillance_station
        assert dsm._surveillance
        assert dsm.reset("surveillance")
        assert not dsm._surveillance

    def test_reset_str_key(self, dsm):
        """Test reset with string API key."""
        assert not dsm._external_usb
        assert dsm.external_usb
        assert dsm._external_usb
        assert dsm.reset(SynoCoreExternalUSB.API_KEY)
        assert not dsm._external_usb

        assert not dsm._hardware
        assert dsm.hardware
        assert dsm._hardware
        assert dsm.reset(SynoCoreHardware.API_KEY)
        assert not dsm._hardware

        assert not dsm._security
        assert dsm.security
        assert dsm._security
        assert dsm.reset(SynoCoreSecurity.API_KEY)
        assert not dsm._security

        assert not dsm._share
        assert dsm.share
        assert dsm._share
        assert dsm.reset(SynoCoreShare.API_KEY)
        assert not dsm._share

        assert not dsm._system
        assert dsm.system
        assert dsm._system
        assert dsm.reset(SynoCoreSystem.API_KEY)
        assert not dsm._system

        assert not dsm._upgrade
        assert dsm.upgrade
        assert dsm._upgrade
        assert dsm.reset(SynoCoreUpgrade.API_KEY)
        assert not dsm._upgrade

        assert not dsm._utilisation
        assert dsm.utilisation
        assert dsm._utilisation
        assert dsm.reset(SynoCoreUtilization.API_KEY)
        assert not dsm._utilisation

        assert not dsm._download
        assert dsm.download_station
        assert dsm._download
        assert dsm.reset(SynoDownloadStation.API_KEY)
        assert not dsm._download

        assert not dsm._photos
        assert dsm.photos
        assert dsm._photos
        assert dsm.reset(SynoPhotos.API_KEY)
        assert not dsm._photos

        assert not dsm._storage
        assert dsm.storage
        assert dsm._storage
        assert dsm.reset(SynoStorage.API_KEY)
        assert not dsm._storage

        assert not dsm._surveillance
        assert dsm.surveillance_station
        assert dsm._surveillance
        assert dsm.reset(SynoSurveillanceStation.API_KEY)
        assert not dsm._surveillance

    def test_reset_object(self, dsm):
        """Test reset with object."""
        assert not dsm._external_usb
        assert dsm.external_usb
        assert dsm._external_usb
        assert dsm.reset(dsm.external_usb)
        assert not dsm._external_usb

        assert not dsm._hardware
        assert dsm.hardware
        assert dsm._hardware
        assert dsm.reset(dsm.hardware)
        assert not dsm._hardware

        assert not dsm._security
        assert dsm.security
        assert dsm._security
        assert dsm.reset(dsm.security)
        assert not dsm._security

        assert not dsm._share
        assert dsm.share
        assert dsm._share
        assert dsm.reset(dsm.share)
        assert not dsm._share

        assert not dsm._system
        assert dsm.system
        assert dsm._system
        assert dsm.reset(dsm.system)
        assert not dsm._system

        assert not dsm._upgrade
        assert dsm.upgrade
        assert dsm._upgrade
        assert dsm.reset(dsm.upgrade)
        assert not dsm._upgrade

        assert not dsm._utilisation
        assert dsm.utilisation
        assert dsm._utilisation
        assert dsm.reset(dsm.utilisation)
        assert not dsm._utilisation

        assert not dsm._download
        assert dsm.download_station
        assert dsm._download
        assert dsm.reset(dsm.download_station)
        assert not dsm._download

        assert not dsm._photos
        assert dsm.photos
        assert dsm._photos
        assert dsm.reset(dsm.photos)
        assert not dsm._photos

        assert not dsm._storage
        assert dsm.storage
        assert dsm._storage
        assert dsm.reset(dsm.storage)
        assert not dsm._storage

        assert not dsm._surveillance
        assert dsm.surveillance_station
        assert dsm._surveillance
        assert dsm.reset(dsm.surveillance_station)
        assert not dsm._surveillance

    def test_reset_str_attr_information(self, dsm):
        """Test reset with string information attr (should not be reset)."""
        assert not dsm._information
        assert dsm.information
        assert dsm._information
        assert not dsm.reset("information")
        assert dsm._information

    def test_reset_str_key_information(self, dsm):
        """Test reset with string information API key (should not be reset)."""
        assert not dsm._information
        assert dsm.information
        assert dsm._information
        assert not dsm.reset(SynoDSMInformation.API_KEY)
        assert dsm._information

    def test_reset_object_information(self, dsm):
        """Test reset with information object (should not be reset)."""
        assert not dsm._information
        assert dsm.information
        assert dsm._information
        assert not dsm.reset(dsm.information)
        assert dsm._information

    @pytest.mark.asyncio
    async def test_utilisation(self, dsm):
        """Test utilisation."""
        await dsm.login()
        assert dsm.utilisation
        await dsm.utilisation.update()

    @pytest.mark.asyncio
    async def test_utilisation_no_data_error(self, dsm):
        """Test utilisation no data error."""
        dsm.no_data_responses.append(SynoCoreUtilization.API_KEY)
        assert await dsm.login()
        assert dsm.utilisation
        with pytest.raises(SynologyDSMAPINoDataException):
            await dsm.utilisation.update()

    @pytest.mark.asyncio
    async def test_utilisation_cpu(self, dsm):
        """Test utilisation CPU."""
        await dsm.login()
        await dsm.utilisation.update()
        assert dsm.utilisation.cpu
        assert dsm.utilisation.cpu_other_load
        assert dsm.utilisation.cpu_user_load
        assert dsm.utilisation.cpu_system_load
        assert dsm.utilisation.cpu_total_load
        assert dsm.utilisation.cpu_1min_load
        assert dsm.utilisation.cpu_5min_load
        assert dsm.utilisation.cpu_15min_load

    @pytest.mark.asyncio
    async def test_utilisation_insufficient_privilege(self, dsm):
        """Test utilisation insufficient user privilege error."""
        dsm.insufficient_privilege_responses.append(SynoCoreUtilization.API_KEY)
        await dsm.login()
        with pytest.raises(SynologyDSMAPIInsufficientPrivilegeException) as error:
            await dsm.utilisation.update()
        assert isinstance(error.value, SynologyDSMAPIErrorException)
        error_value = error.value.args[0]
        assert error_value["api"] == "SYNO.Core.System.Utilization"
        assert error_value["code"] == 105
        assert error_value["reason"] == "Insufficient user privilege"

    @pytest.mark.asyncio
    async def test_utilisation_error(self, dsm):
        """Test utilisation error."""
        dsm.error = True
        await dsm.login()
        with pytest.raises(SynologyDSMAPIErrorException) as error:
            await dsm.utilisation.update()
        error_value = error.value.args[0]
        assert error_value["api"] == "SYNO.Core.System.Utilization"
        assert error_value["code"] == 1055
        assert error_value["reason"] == "Unknown"
        assert error_value["details"] == {
            "err_key": "",
            "err_line": 883,
            "err_msg": "Transmition failed.",
            "err_session": "",
        }

    @pytest.mark.asyncio
    async def test_utilisation_memory(self, dsm):
        """Test utilisation memory."""
        await dsm.login()
        await dsm.utilisation.update()
        assert dsm.utilisation.memory
        assert dsm.utilisation.memory_real_usage
        assert dsm.utilisation.memory_size()
        assert dsm.utilisation.memory_size(True)
        assert dsm.utilisation.memory_available_swap()
        assert dsm.utilisation.memory_available_swap(True)
        assert dsm.utilisation.memory_cached()
        assert dsm.utilisation.memory_cached(True)
        assert dsm.utilisation.memory_available_real()
        assert dsm.utilisation.memory_available_real(True)
        assert dsm.utilisation.memory_total_real()
        assert dsm.utilisation.memory_total_real(True)
        assert dsm.utilisation.memory_total_swap()
        assert dsm.utilisation.memory_total_swap(True)

    @pytest.mark.asyncio
    async def test_utilisation_network(self, dsm):
        """Test utilisation network."""
        await dsm.login()
        await dsm.utilisation.update()
        assert dsm.utilisation.network
        assert dsm.utilisation.network_up()
        assert dsm.utilisation.network_up(True)
        assert dsm.utilisation.network_down()
        assert dsm.utilisation.network_down(True)
