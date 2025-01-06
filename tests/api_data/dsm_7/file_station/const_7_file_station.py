"""DSM 7 SYNO.FileStation.List data."""

DSM_7_FILE_STATION_FOLDERS = {
    "data": {
        "offset": 0,
        "shares": [
            {
                "additional": {
                    "mount_point_type": "",
                    "owner": {"gid": 0, "group": "root", "uid": 0, "user": "root"},
                    "perm": {
                        "acl": {
                            "append": True,
                            "del": True,
                            "exec": True,
                            "read": True,
                            "write": True,
                        },
                        "acl_enable": True,
                        "adv_right": {
                            "disable_download": False,
                            "disable_list": False,
                            "disable_modify": False,
                        },
                        "is_acl_mode": True,
                        "is_share_readonly": False,
                        "posix": 777,
                        "share_right": "RW",
                    },
                    "real_path": "/volume1/backup",
                    "sync_share": False,
                    "time": {
                        "atime": 1736098543,
                        "crtime": 1669466095,
                        "ctime": 1736083030,
                        "mtime": 1733848814,
                    },
                    "volume_status": {
                        "freespace": 1553335107584,
                        "readonly": False,
                        "totalspace": 3821146505216,
                    },
                },
                "isdir": True,
                "name": "backup",
                "path": "/backup",
            },
            {
                "additional": {
                    "mount_point_type": "",
                    "owner": {
                        "gid": 100,
                        "group": "users",
                        "uid": 1046,
                        "user": "hass",
                    },
                    "perm": {
                        "acl": {
                            "append": True,
                            "del": True,
                            "exec": True,
                            "read": True,
                            "write": True,
                        },
                        "acl_enable": True,
                        "adv_right": {
                            "disable_download": False,
                            "disable_list": False,
                            "disable_modify": False,
                        },
                        "is_acl_mode": True,
                        "is_share_readonly": False,
                        "posix": 777,
                        "share_right": "RW",
                    },
                    "real_path": "/volume1/homes/hass",
                    "sync_share": False,
                    "time": {
                        "atime": 1736109199,
                        "crtime": 1643818781,
                        "ctime": 1736109071,
                        "mtime": 1736109071,
                    },
                    "volume_status": {
                        "freespace": 1553335107584,
                        "readonly": False,
                        "totalspace": 3821146505216,
                    },
                },
                "isdir": True,
                "name": "home",
                "path": "/home",
            },
        ],
        "total": 2,
    },
    "success": True,
}
DSM_7_FILE_STATION_FILES = {
    "data": {
        "files": [
            {
                "additional": {
                    "mount_point_type": "",
                    "owner": {
                        "gid": 105733,
                        "group": "SynologyPhotos",
                        "uid": 1046,
                        "user": "hass",
                    },
                    "perm": {
                        "acl": {
                            "append": True,
                            "del": True,
                            "exec": True,
                            "read": True,
                            "write": True,
                        },
                        "is_acl_mode": True,
                        "posix": 711,
                    },
                    "real_path": "/volume1/homes/hass/Photos",
                    "size": 50,
                    "time": {
                        "atime": 1735700476,
                        "crtime": 1723653032,
                        "ctime": 1723653464,
                        "mtime": 1723653464,
                    },
                    "type": "",
                },
                "isdir": True,
                "name": "Photos",
                "path": "/home/Photos",
            },
            {
                "additional": {
                    "mount_point_type": "",
                    "owner": {
                        "gid": 100,
                        "group": "users",
                        "uid": 1046,
                        "user": "hass",
                    },
                    "perm": {
                        "acl": {
                            "append": True,
                            "del": True,
                            "exec": True,
                            "read": True,
                            "write": True,
                        },
                        "is_acl_mode": True,
                        "posix": 711,
                    },
                    "real_path": "/volume1/homes/hass/3e57d06c.tar",
                    "size": 1660753920,
                    "time": {
                        "atime": 1736105132,
                        "crtime": 1736105128,
                        "ctime": 1736105132,
                        "mtime": 1736105132,
                    },
                    "type": "TAR",
                },
                "isdir": False,
                "name": "3e57d06c.tar",
                "path": "/home/3e57d06c.tar",
            },
        ],
        "offset": 0,
        "total": 2,
    },
    "success": True,
}
