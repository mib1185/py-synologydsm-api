"""Synology Core API models."""
from __future__ import annotations

from typing import TypedDict


class SynoCoreShareType(TypedDict):
    """TypedDict for SynoCoreShareType."""

    uuid: str
    name: str
    vol_path: str
    enable_recycle_bin: bool
    share_quota_used: float | int
