"""Synology DSM File Station upload tests."""

# pylint: disable=protected-access
from unittest.mock import AsyncMock, MagicMock

import pytest
from yarl import URL

from synology_dsm.api.file_station import SynoFileStation
from synology_dsm.synology_dsm import SynologyDSM

from . import VALID_HOST, VALID_PASSWORD, VALID_PORT, VALID_USER

CHUNKS = [b"x" * 1024] * 10 + [b"tail"]
CONTENT_SIZE = sum(len(chunk) for chunk in CHUNKS)


async def _content():
    for chunk in CHUNKS:
        yield chunk


class _BufferWriter:
    """Collects the bytes written by a payload."""

    def __init__(self):
        self.buffer = bytearray()

    async def write(self, data):
        self.buffer.extend(data)


async def _upload(size):
    session = MagicMock()
    response = MagicMock(status=200, headers={"Content-Type": "application/json"})
    response.json = AsyncMock(return_value={"success": True})
    session.post = AsyncMock(return_value=response)
    dsm = SynologyDSM(session, VALID_HOST, VALID_PORT, VALID_USER, VALID_PASSWORD)

    assert await dsm._execute_request(
        "POST",
        URL(f"http://{VALID_HOST}:{VALID_PORT}/webapi/entry.cgi"),
        {"api": SynoFileStation.UPLOAD_API_KEY, "method": "upload"},
        path="/share/backups",
        filename="backup.tar",
        content=_content(),
        create_parents=True,
        size=size,
    ) == {"success": True}
    return session.post.call_args.kwargs["data"]


@pytest.mark.asyncio
async def test_upload_async_iterator_with_size():
    """Test that a sized async iterator upload gets a known content length."""
    data = await _upload(CONTENT_SIZE)

    writer = _BufferWriter()
    await data.write(writer)
    assert data.size == len(writer.buffer)
    assert b"x" * 1024 * 10 + b"tail" in writer.buffer


@pytest.mark.asyncio
async def test_upload_async_iterator_without_size():
    """Test that an unsized async iterator upload falls back to chunked."""
    data = await _upload(None)

    assert data.size is None
