"""DSM 7 SYNO.AudioStation.* datas."""

DSM_7_AUDIO_STATION_INFOS = {
    "data": {
        "browse_personal_library": "all",
        "dsd_decode_capability": True,
        "enable_equalizer": False,
        "enable_personal_library": False,
        "enable_user_home": True,
        "has_music_share": True,
        "is_manager": True,
        "playing_queue_max": 8192,
        "privilege": {
            "playlist_edit": True,
            "remote_player": True,
            "sharing": True,
            "tag_edit": True,
            "upnp_browse": True
        },
        "remote_controller": False,
        "same_subnet": True,
        "serial_number": "mySerialNumber",
        "settings": {
            "audio_show_virtual_library": True,
            "disable_upnp": False,
            "enable_download": False,
            "prefer_using_html5": True,
            "transcode_to_mp3": True
        },
        "sid": "mySid",
        "support_bluetooth": False,
        "support_usb": False,
        "support_virtual_library": True,
        "transcode_capability": ["wav", "mp3"],
        "version": 5068,
        "version_string": "7.0.0-5068"
    },
    "success": True
}

DSM_7_AUDIO_STATION_PLAYER_LIST = {
    "data": {
        "players": [
            {
                "id": "uuid:a756f073-d134-4834-995b-6be38be4b190",
                "is_multiple": False,
                "name": "Denon AVR-X2700H (DLNA)",
                "password_protected": False,
                "support_seek": True,
                "support_set_volume": True,
                "type": "upnp"
            },
            {
                "id": "uuid:bf56262a-d0ae-4e86-b32a-e26d61f6de6e",
                "is_multiple": False,
                "name": "TV TV",
                "password_protected": False,
                "support_seek": True,
                "support_set_volume": True,
                "type": "upnp"
            },
            {
                "id": "0006785AC8AE",
                "is_multiple": False,
                "name": "Denon AVR-X2700H (AirPlay)",
                "password_protected": False,
                "support_seek": True,
                "support_set_volume": True,
                "type": "airplay"
            },
            {
                "id": "__SYNO_Multiple_AirPlay__",
                "is_multiple": True,
                "name": "Multiple AirPlay Devices",
                "password_protected": False,
                "support_seek": True,
                "support_set_volume": True,
                "type": "airplay",
                "additional": {"subplayer_list": []}
            }
        ]
    },
    "success": True
}

DSM_7_AUDIO_STATION_PLAYER_STATUS = {
    "data": {
        "index": 0,
        "play_mode": {
            "repeat": "none",
            "shuffle": False
        },
        "playlist_timestamp": 1650661485,
        "playlist_total": 20,
        "position": 0,
        "song": {
            "additional": {
                "song_audio": {
                    "bitrate": 320000,
                    "channel": 1,
                    "duration": 295,
                    "filesize": 1,
                    "frequency": 0
                },
                "song_tag": {
                    "album": "25",
                    "album_artist": "Adele",
                    "artist": "Adele",
                    "comment": "Some random comment",
                    "composer": "Adele Adkins & Greg Kurstin",
                    "disc": 1,
                    "genre": "Pop",
                    "track": 1,
                    "year": 2015
                }
            },
            "id": "music_20508",
            "path": "music/Adele/25 [2015]/CD1 - 01 - Hello.mp3",
            "title": "Hello",
            "type": "file"
        },
        "state": "transitioning",
        "stop_index": 0,
        "subplayer_volume": None,
        "volume": 42
    },
    "success": True
}
