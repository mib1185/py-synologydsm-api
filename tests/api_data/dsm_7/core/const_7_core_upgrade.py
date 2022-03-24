"""DSM 7 SYNO.Core.Upgrade data."""

DSM_7_CORE_UPGRADE_FALSE = {"data": {"update": {"available": False}}, "success": True}
DSM_7_CORE_UPGRADE_TRUE = {
    "data": {
        "update": {
            "available": True,
            "reboot": "now",
            "restart": "some",
            "type": "nano",
            "version": "7.0.1-42218 Update 3",
            "version_details": {
                "buildnumber": 42218,
                "major": 7,
                "micro": 1,
                "minor": 0,
                "nano": 3,
                "os_name": "DSM",
            },
        }
    },
    "success": True,
}
