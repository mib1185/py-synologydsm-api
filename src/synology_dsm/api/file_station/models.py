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


# -------------------------------------
# shared folder
# -------------------------------------


@dataclass
class SynoFileSharedFolderAdditionalPermission:
    """Representation of an Synology FileStation additionl permission data."""

    acl: dict
    acl_enable: bool
    adv_right: dict
    is_acl_mode: bool
    is_share_readonly: bool
    posix: int
    share_right: str


@dataclass
class SynoFileSharedFolderAdditionalVolumeStatus:
    """Representation of an Synology FileStation additionl permission data."""

    freespace: int
    totalspace: int
    readonly: bool


@dataclass
class SynoFileSharedFolderAdditional:
    """Representation of an Synology FileStation Shared Folder additionl data."""

    mount_point_type: str
    owner: SynoFileAdditionalOwner
    perm: SynoFileSharedFolderAdditionalPermission
    volume_status: SynoFileSharedFolderAdditionalVolumeStatus


@dataclass
class SynoFileSharedFolder:
    """Representation of an Synology FileStation Shared Folder."""

    additional: SynoFileSharedFolderAdditional | None
    is_dir: bool
    name: str
    path: str


# -------------------------------------
# file
# -------------------------------------


@dataclass
class SynoFileFileAdditionalPermission:
    """Representation of an Synology FileStation additionl permission data."""

    acl: dict
    is_acl_mode: bool
    posix: int


@dataclass
class SynoFileFileAdditionalTime:
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
    perm: SynoFileFileAdditionalPermission
    real_path: str
    size: int
    time: SynoFileFileAdditionalTime
    type: str


@dataclass
class SynoFileFile:
    """Representation of an Synology FileStation File."""

    additional: SynoFileFileAdditional | None
    is_dir: bool
    name: str
    path: str
