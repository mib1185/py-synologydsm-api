"""DSM 7 SYNO.Core.System network data."""

DSM_7_CORE_SYSTEM_NETWORK = {
    "data": {
        "dns": "192.168.1.5",
        "enabled_domain": False,
        "enabled_samba": True,
        "gateway": "192.168.1.1",
        "hostname": "DiskStation",
        "nif": [
            {
                "addr": "192.168.1.10",
                "duplex": True,
                "id": "eth0",
                "mac": "00-11-32-00-00-01",
                "mask": "255.255.255.0",
                "mtu": 1500,
                "speed": 1000,
                "status": "connected",
                "type": "lan",
                "use_dhcp": True,
            },
            {
                "addr": "169.254.216.44",
                "duplex": True,
                "id": "eth1",
                "mac": "00-11-32-00-00-02",
                "mask": "255.255.0.0",
                "mtu": 1500,
                "speed": -1,
                "status": "disconnected",
                "type": "lan",
                "use_dhcp": True,
            },
        ],
        "wins": "",
        "workgroup": "WORKGROUP",
    },
    "success": True,
}
