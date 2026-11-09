"""DSM 6 SYNO.Core.Package data."""

DSM_6_CORE_PACKAGE = {
    "data": {
        "packages": [
            {
                "additional": {"install_type": "system"},
                "id": "FileStation",
                "name": "File Station",
                "version": "1.2.8-0293",
            },
            {
                "additional": {"install_type": "system"},
                "id": "SynoFinder",
                "name": "Universal Search",
                "version": "1.5.1-0316",
            },
            {
                "additional": {"install_type": "system"},
                "id": "OAuthService",
                "name": "OAuth Service",
                "version": "1.0.4-0031",
            },
        ],
        "total": 3,
    },
    "success": True,
}

# DSM 6 doesn't know the "available_operation" additional data.
DSM_6_CORE_PACKAGE_ERROR_ADDITIONAL = {
    "error": {"code": 120, "errors": {"name": "additional", "reason": "condition"}},
    "success": False,
}

# SYNO.Core.Package.Server data, with only some of the packages and fields.
DSM_6_CORE_PACKAGE_SERVER = {
    "data": {
        "banners": [],
        "beta_packages": [],
        "blupgrade": True,
        "categories": [],
        "packages": [
            {
                "blupgrade": False,
                "changelog": '<p><strong>Fixed Issues</strong></p><ol style="list-style: decimal; padding-left: 30px;"><li>Fixed an issue where a public share link might not display correctly after opening.</li></ol>',
                "dname": "Audio Station",
                "id": "AudioStation",
                "is_security_version": False,
                "package": "AudioStation",
                "silent_upgrade": True,
                "source": "syno",
                "version": "6.5.7-3384",
            },
            {
                "blupgrade": False,
                "changelog": '<p><strong>Compatibility &amp; Installation</strong></p><ol style="list-style: decimal; padding-left: 30px;"><li>To preview newly added HEIC files in File Station, please install Advanced Media Extensions, available in DSM 6.2.4 and above, in Package Center.</li></ol><p><strong>Bug fixed</strong></p><ol style="list-style: decimal; padding-left: 30px;"><li>Fixed an issue where search could not be conducted on contents in sub-folders within shared folders.</li><li>Fixed an issue where users could not switch between images when browsing HEIC files.</li><li>Updating Audio Station to version 6.5.6 fixes the issue where editing music information in File Station might delete its embedded album cover.</li></ol>',
                "dname": "File Station",
                "id": "FileStation",
                "install_type": "system",
                "is_security_version": False,
                "package": "FileStation",
                "silent_upgrade": True,
                "source": "syno",
                "version": "1.2.8-0293",
            },
            {
                "blupgrade": False,
                "changelog": '<p><strong>Important Note</strong></p><p>This update is expected to be available in all regions within the next few days. The actual time of release may vary slightly depending on regions.</p><p><strong>Fixed Issues</strong></p><ol style="list-style: decimal; padding-left: 30px;"><li>Minor bug fixes.</li></ol>',
                "dname": "OAuth Service",
                "id": "OAuthService",
                "install_type": "system",
                "is_security_version": False,
                "package": "OAuthService",
                "silent_upgrade": True,
                "source": "syno",
                "version": "1.0.4-0031",
            },
            {
                "blupgrade": True,
                "changelog": '<p><strong>Important Notes</strong></p><ol style="list-style: decimal; padding-left: 30px;"><li>The update is expected to be available in all regions within the next few days. The actual time of release may vary slightly depending on the region.</li></ol><p><strong>Fixed Issues</strong></p><ol style="list-style: decimal; padding-left: 30px;"><li>Fixed an issue where indexing might be stuck after user renames or modifies a large amount of files.</li><li>Fixed an issue where pausing indexing might unexpectedly consume high CPU usage.</li><li>Fixed minor bugs.</li></ol>',
                "dname": "Universal Search",
                "id": "SynoFinder",
                "install_type": "system",
                "is_security_version": False,
                "package": "SynoFinder",
                "silent_upgrade": True,
                "source": "syno",
                "version": "1.5.2-0323",
            },
        ],
    },
    "success": True,
}
