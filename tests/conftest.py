"""Main conftest."""

import pytest

from synology_dsm.synology_dsm import SynologyDSM

from . import (
    VALID_HOST,
    VALID_HTTPS,
    VALID_PASSWORD,
    VALID_PORT,
    VALID_USER,
    SynologyDSMMock,
)


@pytest.fixture
def api() -> SynologyDSM:
    """Return a mock DSM 6 API."""
    return SynologyDSMMock(
        None,
        VALID_HOST,
        VALID_PORT,
        VALID_USER,
        VALID_PASSWORD,
        VALID_HTTPS,
    )


@pytest.fixture(
    params=[5, 6],
    ids=["DSM 5", "DSM 6"],
)
def dsm(request, api) -> SynologyDSM:
    """Return a mock DSM 6 API."""
    api.dsm_version = request.param
    return api


@pytest.fixture
def dsm_5(api) -> SynologyDSM:
    """Return a mock DSM 5 API."""
    api.dsm_version = 5
    return api


@pytest.fixture
def dsm_6(api) -> SynologyDSM:
    """Alias for api fixture."""
    return api


@pytest.fixture
def dsm_7(api) -> SynologyDSM:
    """Return a mock DSM 7 API."""
    api.dsm_version = 7
    return api
