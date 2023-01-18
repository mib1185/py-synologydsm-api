========================================
Asynchronous Python API for Synology DSM
========================================

.. image:: https://github.com/mib1185/py-synologydsm-api/workflows/Tests/badge.svg
    :target: https://github.com/mib1185/py-synologydsm-api/actions?query=workflow%3ATests+branch%3Amaster

.. image:: https://img.shields.io/pypi/v/py-synologydsm-api.svg
    :alt: Library version
    :target: https://pypi.org/project/py-synologydsm-api

.. image:: https://img.shields.io/pypi/pyversions/py-synologydsm-api.svg
    :alt: Supported versions
    :target: https://pypi.org/project/py-synologydsm-api

.. image:: https://pepy.tech/badge/py-synologydsm-api
    :alt: Downloads
    :target: https://pypi.org/project/py-synologydsm-api

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Formated with Black
    :target: https://github.com/psf/black


Installation
============

.. code-block:: bash

    [sudo] pip install py-synologydsm-api


Usage
=====

You can import the module as ``synology_dsm``.


Constructor
-----------

.. code-block:: python

    SynologyDSM(
        session,
        dsm_ip,
        dsm_port,
        username,
        password,
        use_https=False,
        timeout=10,
        device_token=None,
        debugmode=False,
    )

For ``session`` a valid ``aiohttp.ClientSession`` needs to be provided. If ssl verification should be truned off, configure the session accordingly (eq. ``aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)``)

``device_token`` should be added when using a two-step authentication account, otherwise DSM will ask to login with a One Time Password (OTP) and requests will fail (see the login section for more details).

Default ``timeout`` is 10 seconds.


Login
------

The library automatically login at first request, but you better use the ``login()`` function separately to authenticate.

It will return a boolean if it successed or faild to authenticate to DSM.

If your account need a two-step authentication (2SA), ``login()`` will raise ``SynologyDSMLogin2SARequiredException``.
Call the function again with a One Time Password (OTP) as parameter, like ``login("123456")`` (better to be a string to handle first zero).
Store the ``device_token`` property so that you do not need to reconnect with password the next time you open a new ``SynologyDSM`` session.


Code exemple
------------

Every API has an ``update()`` function that is needed to get the first data, then the data is cached and updated at the next ``update()`` call.

The ``SynologyDSM`` class can also ``update()`` all APIs at once.

.. code-block:: python

    import asyncio
    import aiohttp
    from synology_dsm import SynologyDSM

    async def main():
        print("Creating Valid API")
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            await do(session)

    async def do(session: aiohttp.ClientSession):
        api = SynologyDSM(session, "<IP/DNS>", "<port>", "<username>", "<password>")
        print("=== Information ===")
        await api.information.update()
        print("Model:           " + str(api.information.model))
        print("RAM:             " + str(api.information.ram) + " MB")
        print("Serial number:   " + str(api.information.serial))
        print("Temperature:     " + str(api.information.temperature) + " °C")
        print("Temp. warning:   " + str(api.information.temperature_warn))
        print("Uptime:          " + str(api.information.uptime))
        print("Full DSM version:" + str(api.information.version_string))
        print("--")

        print("=== Utilisation ===")
        await api.utilisation.update()
        print("CPU Load:        " + str(api.utilisation.cpu_total_load) + " %")
        print("Memory Use:      " + str(api.utilisation.memory_real_usage) + " %")
        print("Net Up:          " + str(api.utilisation.network_up()))
        print("Net Down:        " + str(api.utilisation.network_down()))
        print("--")

        print("=== Storage ===")
        await api.storage.update()
        for volume_id in api.storage.volumes_ids:
            print("ID:          " + str(volume_id))
            print("Status:      " + str(api.storage.volume_status(volume_id)))
            print("% Used:      " + str(api.storage.volume_percentage_used(volume_id)) + " %")
            print("--")

        for disk_id in api.storage.disks_ids:
            print("ID:          " + str(disk_id))
            print("Name:        " + str(api.storage.disk_name(disk_id)))
            print("S-Status:    " + str(api.storage.disk_smart_status(disk_id)))
            print("Status:      " + str(api.storage.disk_status(disk_id)))
            print("Temp:        " + str(api.storage.disk_temp(disk_id)))
            print("--")

        print("=== Shared Folders ===")
        await api.share.update()
        for share_uuid in api.share.shares_uuids:
            print("Share name:        " + str(api.share.share_name(share_uuid)))
            print("Share path:        " + str(api.share.share_path(share_uuid)))
            print("Space used:        " + str(api.share.share_size(share_uuid, human_readable=True)))
            print("Recycle Bin Enabled: " + str(api.share.share_recycle_bin(share_uuid)))
            print("--")

    if __name__ == "__main__":
        asyncio.run(main())

Download Station usage
--------------------------

.. code-block:: python

    import asyncio
    import aiohttp
    from synology_dsm import SynologyDSM

    async def main():
        print("Creating Valid API")
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            await do(session)

    async def do(session: aiohttp.ClientSession):
        api = SynologyDSM(session, "<IP/DNS>", "<port>", "<username>", "<password>")

        if "SYNO.DownloadStation.Info" in api.apis:

            await api.download_station.get_info()
            await api.download_station.get_config()

            # The download list will be updated after each of the following functions:
            # You should have the right on the (default) directory that the download will be saved, or you will get a 403 or 406 error
            await api.download_station.create("http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4")
            await api.download_station.pause("dbid_1")
            # Like the other function, you can eather pass a str or a list
            await api.download_station.resume(["dbid_1", "dbid_2"])
            await api.download_station.delete("dbid_3")

            # Manual update
            await api.download_station.update()

    if __name__ == "__main__":
        asyncio.run(main())

Surveillance Station usage
--------------------------

.. code-block:: python

    import asyncio
    import aiohttp
    from synology_dsm import SynologyDSM

    async def main():
        print("Creating Valid API")
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            await do(session)

    async def do(session: aiohttp.ClientSession):
        api = SynologyDSM(session, "<IP/DNS>", "<port>", "<username>", "<password>")

        surveillance = api.surveillance_station
        await surveillance.update() # First update is required

        # Returns a list of cached cameras available
        cameras = surveillance.get_all_cameras()

        # Assuming there's at least one camera, get the first camera_id
        camera_id = cameras[0].camera_id

        # Returns cached camera object by camera_id
        camera = surveillance.get_camera(camera_id)

        # Returns cached motion detection enabled
        motion_setting = camera.is_motion_detection_enabled

        # Return bytes of camera image
        await surveillance.get_camera_image(camera_id)

        # Updates all cameras/motion settings and cahce them
        await surveillance.update()

        # Gets Home Mode status
        home_mode_status = await surveillance.get_home_mode_status()

        # Sets home mode - true is on, false is off
        await surveillance.set_home_mode(True)

    if __name__ == "__main__":
        asyncio.run(main())

System usage
--------------------------

.. code-block:: python

    import asyncio
    import aiohttp
    from synology_dsm import SynologyDSM

    async def main():
        print("Creating Valid API")
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            await do(session)

    async def do(session: aiohttp.ClientSession):
        api = SynologyDSM(session, "<IP/DNS>", "<port>", "<username>", "<password>")

        system = api.system

        # Reboot NAS
        await system.reboot()

        # Shutdown NAS
        await system.shutdown()

        # Manual update system information
        await system.update()

        # Get CPU information
        system.cpu_clock_speed
        system.cpu_cores
        system.cpu_family
        system.cpu_series

        # Get NTP settings
        system.enabled_ntp
        system.ntp_server

        # Get system information
        system.firmware_ver
        system.model
        system.ram_size
        system.serial
        system.sys_temp
        system.time
        system.time_zone
        system.time_zone_desc
        system.up_time

        # Get list of all connected USB devices
        system.usb_dev

    if __name__ == "__main__":
        asyncio.run(main())

Hyperbackup usage (with SSL)
--------------------------

.. code-block:: python
    import asyncio
    import aiohttp
    from synology_dsm import SynologyDSM

    async def main():
        print("Creating Valid API")
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=True)
        ) as session:
            await do(session)

    async def do(session: aiohttp.ClientSession):
        api = SynologyDSM(session, "<ip_or_domain>", "443", "<username>", "<password>", use_https=True)

        await api.hyperbackup.update()
        for task_id in api.hyperbackup.task_ids:
            print("ID:               " + str(task_id))
            print("Name:             " + api.hyperbackup.name(task_id))
            print("Status:           " + api.hyperbackup.status(task_id))
            print("Next Backup time: " + str(api.hyperbackup.next_backup_time(task_id)))
            print("Size:             " + human_size(api.hyperbackup.used_size(task_id)))
            print("--")

    def human_size(bytes, units=['KB','MB','GB','TB', 'PB', 'EB']):
        """ Returns a human readable string representation of bytes """
        if bytes is None:
            return "N/A"
        return str(bytes) + units[0] if bytes < 1024 else human_size(bytes>>10, units[1:])

    if __name__ == "__main__":
        asyncio.run(main())


Upgrade usage
--------------------------

.. code-block:: python

    import asyncio
    import aiohttp
    from synology_dsm import SynologyDSM

    async def main():
        print("Creating Valid API")
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            await do(session)

    async def do(session: aiohttp.ClientSession):
        api = SynologyDSM(session, "<IP/DNS>", "<port>", "<username>", "<password>")
        upgrade = api.upgrade

        # Manual update upgrade information
        await upgrade.update()

        # check if DSM update is available
        if upgrade.update_available:
            do something ...

        # get available version string (return None if no update available)
        upgrade.available_version

        # get need of reboot (return None if no update available)
        upgrade.reboot_needed

        # get need of service restarts (return None if no update available)
        upgrade.service_restarts

    if __name__ == "__main__":
        asyncio.run(main())

Credits / Special Thanks
========================
- https://github.com/florianeinfalt
- https://github.com/tchellomello
- https://github.com/Quentame   (Multiple API addition & tests)
- https://github.com/aaska      (DSM 5 tests)
- https://github.com/chemelli74 (2SA tests)
- https://github.com/snjoetw    (Surveillance Station library)
- https://github.com/shenxn     (Surveillance Station tests)
- https://github.com/Gestas     (Shared Folders)

Found Synology API "documentation" on this repo : https://github.com/kwent/syno/tree/master/definitions


Official references
===================

- `Calendar API documentation (2015-2019) <https://global.download.synology.com/download/Document/Software/DeveloperGuide/Package/Calendar/2.4/enu/Synology_Calendar_API_Guide_enu.pdf>`_

- `Download Station API documentation (2012-2014) <https://global.download.synology.com/download/Document/Software/DeveloperGuide/Package/DownloadStation/All/enu/Synology_Download_Station_Web_API.pdf>`_

- `File Station API documentation (2013-2019) <https://global.download.synology.com/download/Document/Software/DeveloperGuide/Package/FileStation/All/enu/Synology_File_Station_API_Guide.pdf>`_

- `Surveillance Station API documentation (2012-2020) <https://global.download.synology.com/download/Document/Software/DeveloperGuide/Package/SurveillanceStation/All/enu/Surveillance_Station_Web_API.pdf>`_

- `Virtual Machine Manager API documentation (2015-2019) <https://global.download.synology.com/download/Document/Software/DeveloperGuide/Package/Virtualization/All/enu/Synology_Virtual_Machine_Manager_API_Guide.pdf>`_
