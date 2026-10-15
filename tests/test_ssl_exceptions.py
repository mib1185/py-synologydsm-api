"""Tests for SSL/TLS error handling."""

import ssl
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import (
    ClientConnectorCertificateError,
    ClientConnectorSSLError,
    ClientError,
)
from aiohttp.client_reqrep import ConnectionKey
from yarl import URL

from synology_dsm import SynologyDSM
from synology_dsm.exceptions import (
    SynologyDSMRequestException,
    SynologyDSMSSLException,
)

CONNECTION_KEY = ConnectionKey("nas.local", 5001, True, True, None, None, None)


def _dsm_raising(exc: Exception) -> SynologyDSM:
    session = MagicMock()
    session.get = AsyncMock(side_effect=exc)
    return SynologyDSM(session, "nas.local", 5001, "user", "pass", True)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("exc", "expected_details"),
    [
        (
            ClientConnectorCertificateError(
                CONNECTION_KEY,
                ssl.SSLCertVerificationError(
                    1,
                    "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: "
                    "certificate has expired (_ssl.c:1000)",
                ),
            ),
            "certificate has expired",
        ),
        (
            ClientConnectorSSLError(
                CONNECTION_KEY, ssl.SSLError(1, "[SSL: WRONG_VERSION_NUMBER]")
            ),
            "WRONG_VERSION_NUMBER",
        ),
        (ssl.SSLError(1, "[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE]"), "HANDSHAKE_FAILURE"),
    ],
    ids=["expired cert", "handshake (aiohttp)", "handshake (raw ssl)"],
)
async def test_ssl_errors_raise_ssl_exception(exc, expected_details):
    """SSL errors are raised as SynologyDSMSSLException with a useful message."""
    dsm = _dsm_raising(exc)
    with pytest.raises(SynologyDSMSSLException) as err:
        await dsm._execute_request("GET", URL("https://nas.local:5001/x"), {}, False)
    # backwards compatible: still a SynologyDSMRequestException
    assert isinstance(err.value, SynologyDSMRequestException)
    details = err.value.args[0]["details"]
    assert err.value.args[0]["code"] == -1
    assert expected_details in details
    assert err.value.__cause__ is exc


@pytest.mark.asyncio
async def test_plain_client_error_is_not_ssl_exception():
    """Non-SSL connection errors keep raising the plain request exception."""
    dsm = _dsm_raising(ClientError("boom"))
    with pytest.raises(SynologyDSMRequestException) as err:
        await dsm._execute_request("GET", URL("https://nas.local:5001/x"), {}, False)
    assert not isinstance(err.value, SynologyDSMSSLException)
