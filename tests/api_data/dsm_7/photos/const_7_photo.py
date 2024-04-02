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
                "owner_user_id": 0,
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

DSM_7_FOTO_SHARED_ITEMS = {
    "success": True,
    "data": {
        "list": [
            {
                "id": 77,
                "filename": "shared_1.jpg",
                "filesize": 1404758,
                "time": 1627062628,
                "indexed_time": 1628329471168,
                "owner_user_id": 0,
                "folder_id": 17,
                "type": "photo",
                "additional": {
                    "thumbnail": {
                        "m": "ready",
                        "xl": "ready",
                        "preview": "broken",
                        "sm": "ready",
                        "cache_key": "77_1628323785",
                        "unit_id": 77,
                    }
                },
            },
            {
                "id": 490,
                "filename": "shared_2.jpg",
                "filesize": 888192,
                "time": 1627062618,
                "indexed_time": 1628329516646,
                "owner_user_id": 0,
                "folder_id": 37,
                "type": "photo",
                "additional": {
                    "thumbnail": {
                        "m": "ready",
                        "xl": "ready",
                        "preview": "broken",
                        "sm": "ready",
                        "cache_key": "490_1628323817",
                        "unit_id": 490,
                    }
                },
            },
            {
                "id": 96,
                "filename": "shared_3.jpg",
                "filesize": 4903571,
                "time": 1626987559,
                "indexed_time": 1628329472531,
                "owner_user_id": 0,
                "folder_id": 18,
                "type": "photo",
                "additional": {
                    "thumbnail": {
                        "m": "ready",
                        "xl": "ready",
                        "preview": "broken",
                        "sm": "ready",
                        "cache_key": "96_1628323786",
                        "unit_id": 96,
                    }
                },
            },
        ]
    },
}

DSM_7_FOTO_ITEMS_SEARCHED = {
    "success": True,
    "data": {
        "list": [
            {
                "id": 12340,
                "filename": "search_1.jpg",
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
                        "cache_key": "12340_1668560967",
                        "unit_id": 12340,
                    }
                },
            },
            {
                "id": 12341,
                "filename": "search_2.jpg",
                "filesize": 2644859,
                "time": 1668538602,
                "indexed_time": 1668564550862,
                "owner_user_id": 1,
                "folder_id": 597,
                "type": "photo",
                "additional": {
                    "thumbnail": {
                        "m": "ready",
                        "xl": "broken",
                        "preview": "broken",
                        "sm": "ready",
                        "cache_key": "12341_1668560967",
                        "unit_id": 12341,
                    }
                },
            },
        ]
    },
}

DSM_7_FOTO_SHARED_ALBUMS = {
    "data": {
        "list": [
            {
                "additional": {
                    "access_permission": {
                        "download": False,
                        "manage": False,
                        "own": False,
                        "upload": False,
                        "view": True,
                    },
                    "sharing_info": {
                        "enable_password": False,
                        "expiration": 0,
                        "is_expired": False,
                        "mtime": 1706014133,
                        "owner": {"id": 1, "name": "owner_user"},
                        "passphrase": "BA234A2m3",
                        "permission": [
                            {
                                "db_id": 7,
                                "id": 1002,
                                "name": "me",
                                "role": "view",
                                "type": "user",
                            },
                            {
                                "db_id": 2,
                                "id": 1001,
                                "name": "other_user",
                                "role": "upload",
                                "type": "user",
                            },
                        ],
                        "privacy_type": "public-view",
                        "sharing_link": "https://nas.mywebsite.me/photo/mo/sharing/BA234A2m3",
                        "type": "album",
                    },
                    "thumbnail": {
                        "cache_key": "4028_1650287094",
                        "m": "ready",
                        "preview": "broken",
                        "sm": "ready",
                        "unit_id": 4028,
                        "xl": "ready",
                    },
                },
                "cant_migrate_condition": {},
                "condition": {},
                "create_time": 1629657841,
                "end_time": 1627843267,
                "freeze_album": False,
                "id": 8,
                "item_count": 2,
                "name": "SharedAlbum",
                "owner_user_id": 1,
                "passphrase": "BA234A2m3",
                "shared": True,
                "sort_by": "default",
                "sort_direction": "default",
                "start_time": 1541754484,
                "temporary_shared": False,
                "type": "normal",
                "version": 477650,
            }
        ]
    },
    "success": True,
}

DSM_7_FOTO_SHARED_ALBUM_ITEMS = {
    "success": True,
    "data": {
        "list": [
            {
                "id": 1986,
                "filename": "album_share_1.jpg",
                "filesize": 2354278,
                "time": 1541754484,
                "indexed_time": 1628459795018,
                "owner_user_id": 0,
                "folder_id": 80,
                "type": "photo",
                "additional": {
                    "resolution": {"width": 2976, "height": 3968},
                    "orientation": 1,
                    "orientation_original": 1,
                    "thumbnail": {
                        "m": "ready",
                        "xl": "ready",
                        "preview": "broken",
                        "sm": "ready",
                        "cache_key": "1986_1650286954",
                        "unit_id": 1986,
                    },
                    "provider_user_id": 1,
                },
            },
            {
                "id": 18924,
                "filename": "album_share_2.jpg",
                "filesize": 4876975,
                "time": 1542449788,
                "indexed_time": 1628461102087,
                "owner_user_id": 0,
                "folder_id": 94,
                "type": "photo",
                "additional": {
                    "resolution": {"width": 2976, "height": 3968},
                    "orientation": 1,
                    "orientation_original": 1,
                    "thumbnail": {
                        "m": "ready",
                        "xl": "notready",
                        "preview": "broken",
                        "sm": "ready",
                        "cache_key": "18924_1650288297",
                        "unit_id": 18924,
                    },
                    "provider_user_id": 1,
                },
            },
        ]
    },
}
