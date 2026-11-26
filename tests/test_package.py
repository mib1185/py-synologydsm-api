"""Synology DSM package tests."""

from typing import Any

import pytest

from synology_dsm.api.core.package import SynoPackage


@pytest.mark.parametrize(
    ("changelog", "expected"),
    [
        ("<p>Fixed issues.</p>", "<p>Fixed issues.</p>"),
        ({"en": "Fixed issues."}, None),
        (None, None),
    ],
)
def test_available_version_changelog(changelog: Any, expected: str | None) -> None:
    """Test only an HTML changelog is returned."""
    package = SynoPackage(
        {"id": "Node.js_v22", "name": "Node.js v22", "version": "22.22.3-1010"},
        {"id": "Node.js_v22", "version": "22.23.4-1011", "changelog": changelog},
    )

    assert package.available_version_changelog == expected
