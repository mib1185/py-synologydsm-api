"""DSM 7 SYNO.Core.Package data."""

# Captured from DSM 7.2.2, with only some of the installed packages.
DSM_7_CORE_PACKAGE = {
    "data": {
        "packages": [
            {
                "additional": {"install_type": "system"},
                "id": "ActiveInsight",
                "name": "Active Insight",
                "timestamp": 1794160354851,
                "version": "3.0.5-24122",
            },
            {
                "additional": {"install_type": "system"},
                "id": "FileStation",
                "name": "File Station",
                "timestamp": 1794160354853,
                "version": "1.4.2-1575",
            },
            {
                "additional": {"install_type": "system"},
                "id": "QuickConnect",
                "name": "QuickConnect",
                "timestamp": 1794160354854,
                "version": "1.0.9-0171",
            },
            {
                "additional": {"install_type": "system_hidden"},
                "id": "SupportService",
                "name": "SupportService",
                "timestamp": 1794160354856,
                "version": "2.0.5-21076",
            },
        ],
        "total": 4,
    },
    "success": True,
}

# SYNO.Core.Package.Server data, with only some of the packages and fields.
DSM_7_CORE_PACKAGE_SERVER = {
    "data": {
        "banners": [],
        "beta_packages": [],
        "categories": [],
        "packages": [
            {
                "beta": False,
                "changelog": '<p><strong>Fixed Issues</strong></p><ol style="list-style: decimal; padding-left: 30px;"><li>Minor bug fixes.</li></ol>',
                "dname": "Active Insight",
                "id": "ActiveInsight",
                "install_type": "system",
                "is_security_version": False,
                "package": "ActiveInsight",
                "silent_upgrade": True,
                "source": "syno",
                "version": "3.0.6-24124",
            },
            {
                "beta": False,
                "changelog": '<p><strong>Important Notes</strong></p><ol style="list-style: decimal; padding-left: 30px;"><li>File Station will discontinue support for generating HEIC/HEIF thumbnails and previews on Synology NAS through Advanced Media Extensions (AME), as most end devices now support the HEVC (H.265) codec. This change also helps reduce server-side load and unnecessary resource usage. Please refer to <a target="_new" href="https://kb.synology.com/DSM/tutorial/Convert_HEIC_to_JPG" target="_blank">this article</a> for a workaround.</li></ol><p><strong>Compatibility and Installation</strong></p><ol style="list-style: decimal; padding-left: 30px;"><li>File Station 1.4.2 requires DSM 7.2.2 and above.</li></ol><p><strong>Fixed Issues</strong></p><ol style="list-style: decimal; padding-left: 30px;"><li>Fixed security vulnerabilities regarding XSS.</li></ol>',
                "dname": "File Station",
                "id": "FileStation",
                "install_type": "system",
                "is_security_version": False,
                "package": "FileStation",
                "silent_upgrade": True,
                "source": "syno",
                "version": "1.4.2-1575",
            },
            {
                "beta": False,
                "changelog": '<p><strong>Fixed Issue</strong></p><ol style="list-style: decimal; padding-left: 30px;"><li>Minor bug fixes.</li></ol>',
                "dname": "QuickConnect",
                "id": "QuickConnect",
                "install_type": "system",
                "is_security_version": False,
                "package": "QuickConnect",
                "silent_upgrade": True,
                "source": "syno",
                "version": "1.0.10-0187",
            },
            {
                "beta": False,
                "changelog": '<p><strong>Compatibility &amp; Installation</strong></p><ol style="list-style: decimal; padding-left: 30px;"><li>Text Editor 1.2.5-0254 requires DSM 7.2 and above.</li></ol>',
                "dname": "Text Editor",
                "id": "TextEditor",
                "is_security_version": False,
                "package": "TextEditor",
                "silent_upgrade": True,
                "source": "syno",
                "version": "1.2.5-0254",
            },
        ],
    },
    "success": True,
}

# SYNO.Core.Package.Server error while DSM has no internet access
DSM_7_CORE_PACKAGE_SERVER_ERROR_NO_INTERNET = {"error": {"code": 117}, "success": False}
