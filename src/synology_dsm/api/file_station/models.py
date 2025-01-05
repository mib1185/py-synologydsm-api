"""Data models for Synology FileStation Module."""

from __future__ import annotations

from dataclasses import dataclass

# -------------------------------------
# generic additional data
# -------------------------------------


@dataclass
class SynoFileAdditionalOwner:
    """Representation of an Synology FileStation additionl owner data."""

    gid: int
    group: str
    uid: int
    user: str


@dataclass
class SynoFileAdditionalPermission:
    """Representation of an Synology FileStation additionl permission data."""

    acl: dict
    is_acl_mode: bool
    posix: int


# -------------------------------------
# shared folder
# -------------------------------------


@dataclass
class SynoFileAdditionalVolumeStatus:
    """Representation of an Synology FileStation additionl permission data."""

    freespace: int
    totalspace: int
    readonly: bool


@dataclass
class SynoFileSharedFolderAdditional:
    """Representation of an Synology FileStation Shared Folder additionl data."""

    mount_point_type: str
    owner: SynoFileAdditionalOwner
    perm: SynoFileAdditionalPermission
    volume_status: SynoFileAdditionalVolumeStatus


@dataclass
class SynoFileSharedFolder:
    """Representation of an Synology FileStation Shared Folder."""

    addidtionan: SynoFileSharedFolderAdditional
    is_dir: bool
    name: str
    path: str


# -------------------------------------
# file
# -------------------------------------


@dataclass
class SynoFileAdditionalTime:
    """Representation of an Synology FileStation additionl permission data."""

    atime: int
    ctime: int
    crtime: int
    mtime: int


@dataclass
class SynoFileFileAdditional:
    """Representation of an Synology FileStation File additionl data."""

    mount_point_type: str
    owner: SynoFileAdditionalOwner
    perm: SynoFileAdditionalPermission
    real_path: str
    size: int
    time: SynoFileAdditionalTime
    type: str


@dataclass
class SynoFileFile:
    """Representation of an Synology FileStation File."""

    addidtionan: SynoFileFileAdditional
    is_dir: bool
    name: str
    path: str
