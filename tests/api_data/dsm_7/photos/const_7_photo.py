"""DSM 7 SYNO.Foto.Browse.Album data."""

DSM_7_FOTO_ALBUMS = {
    "data": {
        "list": [
            {
                "condition": {"folder_filter": [597], "user_id": 1},
                "create_time": 1674514932,
                "end_time": 1640958550,
                "id": 4,
                "item_count": 3,
                "name": "Album1",
                "owner_user_id": 1,
                "passphrase": "",
                "shared": False,
                "sort_by": "default",
                "sort_direction": "default",
                "start_time": 1601653233,
                "type": "condition",
                "version": 197920,
            },
            {
                "cant_migrate_condition": {},
                "condition": {},
                "create_time": 1668690757,
                "end_time": 1668538602,
                "freeze_album": False,
                "id": 1,
                "item_count": 1,
                "name": "Album2",
                "owner_user_id": 1,
                "passphrase": "",
                "shared": False,
                "sort_by": "default",
                "sort_direction": "default",
                "start_time": 1668538602,
                "temporary_shared": False,
                "type": "normal",
                "version": 195694,
            },
        ]
    },
    "success": True,
}

DSM_7_FOTO_ITEMS = {
    "success": True,
    "data": {
        "list": [
            {
                "id": 29807,
                "filename": "20221115_185642.jpg",
                "filesize": 2644859,
                "time": 1668538602,
                "indexed_time": 1668564550862,
                "owner_user_id": 1,
                "folder_id": 597,
                "type": "photo",
                "additional": {
                    "thumbnail": {
                        "m": "ready",
                        "xl": "ready",
                        "preview": "broken",
                        "sm": "ready",
                        "cache_key": "29807_1668560967",
                        "unit_id": 29807,
                    }
                },
            },
            {
                "id": 29808,
                "filename": "20221115_185643.jpg",
                "filesize": 2644859,
                "time": 1668538602,
                "indexed_time": 1668564550862,
                "owner_user_id": 1,
                "folder_id": 597,
                "type": "photo",
                "additional": {
                    "thumbnail": {
                        "m": "ready",
                        "xl": "notready",
                        "preview": "broken",
                        "sm": "ready",
                        "cache_key": "29808_1668560967",
                        "unit_id": 29808,
                    }
                },
            },
            {
                "id": 29809,
                "filename": "20221115_185644.jpg",
                "filesize": 2644859,
                "time": 1668538602,
                "indexed_time": 1668564550862,
                "owner_user_id": 1,
                "folder_id": 597,
                "type": "photo",
                "additional": {
                    "thumbnail": {
                        "m": "notready",
                        "xl": "notready",
                        "preview": "broken",
                        "sm": "ready",
                        "cache_key": "29809_1668560967",
                        "unit_id": 29809,
                    }
                },
            },
        ]
    },
}
