"""DSM 7 SYNO.Core.Upgrade data."""

# Common definitions parts for backup tasks
# =============================================
DUMMY_SOURCE_DATA = {  # NB: mis-spellings match actual API in DSM 7 (e.g. "dataEncryped")
    "app_config": [], "app_list": ["HyperBackup"], "app_name_list": ["Hyper Backup"],
    "backup_filter": {"exclude_list": [], "whitelist": []}, "backup_volumes": [], "file_list": [
        {"dataEncryped": False, "encryptedShare": False, "fileSystem": "BTRFS", "fileSystemType": "internal",
         "folderPath": "/myfolder1", "fullPath": "/volume1/myfolder1", "isValidSource": True, "missing": False},
        {"dataEncryped": False, "encryptedShare": False, "fileSystem": "BTRFS", "fileSystemType": "internal",
         "folderPath": "/myfolder2", "fullPath": "/volume1/myfolder2", "isValidSource": True, "missing": False}
    ]
    , "share_list": {
        "myfolder1": {"dataEncryped": False, "encryptedShare": False, "fileSystem": "BTRFS",
                      "fileSystemType": "internal", "fullPath": "/volume1/myfolder1", "isValidSource": True},
        "myfolder2": {"dataEncryped": False, "encryptedShare": False, "fileSystem": "BTRFS",
                      "fileSystemType": "internal", "fullPath": "/volume1/myfolder2", "isValidSource": True}
    }
}

SCHEDULE_VALID = {
    "schedule_enable": True, "schedule": {
        "date": "2023/12/19", "date_type": 0, "hour": 13, "last_work_hour": 13, "min": 0,
        "next_trigger_time": "2023-12-20 13:00", "repeat": 0, "repeat_hour": 0,
        "repeat_hour_store_config": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
        "repeat_min": 0, "repeat_min_store_config": [], "week_name": "0,1,2,3,4,5,6"
    }
}
SCHEDULE_DISABLED = SCHEDULE_VALID.copy()
SCHEDULE_DISABLED["schedule_enable"] = False
# =============================================

# Backup task defintions with various states
# =============================================
# Running backup, no schedule, backup_prepare step (0% progress)
DSM_7_TASK_1_LIST_RUN_NO_SCHD_0_PCT = {
    'name': 'Run, no schd, 0%', 'task_id': 1, 'state': 'backupable', 'status': 'backup',
    'last_bkp_result': 'backingup', 'data_enc': False, 'data_type': 'data', 'ext3ShareList': [],
    'last_bkp_end_time': '2023/12/18 14:51', 'last_bkp_time': '2023/12/18 14:51', 'next_bkp_time': '',
    'repo_id': 1, 'schedule': SCHEDULE_DISABLED, 'target_id': 'vault_5.hbk', 'target_type': 'image',
    'transfer_type': 'image_remote', 'type': 'image:image_remote'
}
DSM_7_TASK_1_STATUS_RUN_NO_SCHD_0_PCT = {'success': True, 'data': {
    'task_id': 1, 'state': 'backupable', 'status': 'backup', 'last_bkp_result': 'backingup', 'last_bkp_error': '',
    'last_bkp_end_time': '2023/12/18 14:51', 'last_bkp_error_code': 4401, 'last_bkp_progress': 73,
    'last_bkp_success_time': '2023/12/18 14:50', 'last_bkp_time': '2023/12/18 14:51', 'next_bkp_time': '',
    'schedule': SCHEDULE_DISABLED, 'progress': {
        'step': 'backup_prepare', 'progress': 0, 'app_done_list': [], 'app_list': [], 'avg_speed': 0, 'can_cancel': True, 'can_suspend': False,
        'current_app': '', 'current_app_action_percent': '0', 'current_app_percent': '0',
        'current_app_stage': '', 'processed_size': '0', 'scan_file_count': '0',
        'title_type': 'backingup', 'total_size': '0',
        'transmitted_size': '0'
}}}

# Running backup, no schedule, data backup step (84% progress)
PERCENT_MIDDLE = 84
DSM_7_TASK_2_LIST_RUN_NO_SCHD_84_PCT = {
    'name': 'Run, no schd, 84%', 'task_id': 2, 'state': 'backupable', 'status': 'backup',
    'last_bkp_result': 'backingup','data_enc': False, 'data_type': 'data', 'ext3ShareList': [],
    'last_bkp_end_time': '2023/12/18 14:51', 'last_bkp_time': '2023/12/18 14:51', 'next_bkp_time': '', 'repo_id': 2,
    'schedule': SCHEDULE_DISABLED,  'target_id': 'vault_2.hbk', 'target_type': 'image', 'transfer_type': 'image_remote',
    'type': 'image:image_remote'
}
DSM_7_TASK_2_STATUS_RUN_NO_SCHD_84_PCT = {'success': True, 'data': {
    'task_id': 2, 'state': 'backupable', 'status': 'backup', 'last_bkp_result': 'backingup', 'last_bkp_error': '',
    'last_bkp_end_time': '2023/12/18 14:51', 'last_bkp_error_code': 4401, 'last_bkp_progress': 73,
    'last_bkp_success_time': '2023/12/18 14:50', 'last_bkp_time': '2023/12/18 14:51', 'next_bkp_time': '',
    'schedule': SCHEDULE_DISABLED, 'progress': {
        'step': 'data_backup', 'progress': PERCENT_MIDDLE, 'app_done_list': [], 'app_list': [], 'avg_speed': 0, 'can_cancel': True,
        'can_suspend': True, 'current_app': '', 'current_app_action_percent': '0', 'current_app_percent': '0',
        'current_app_stage': '', 'processed_size': '1009875720', 'scan_file_count': '16699',
        'title_type': 'backingup', 'total_size': '1202233000', 'transmitted_size': '9789834655'
}}}

# Running backup, with schedule
DSM_7_TASK_3_LIST_RUN_WITH_SCHD_SIZE_CNT = {
    "name": "Checking src file size", "task_id": 3, "status": "backup", "state": "backupable",
    "last_bkp_result": "backingup", "data_enc": False, "data_type": "data", "ext3ShareList": [],
    "is_modified": False, "last_bkp_end_time": "2023/12/19 13:12", "last_bkp_time": "2023/12/19 13:12",
    "repo_id": 3, "source": DUMMY_SOURCE_DATA, "target_id": "vault_4.hbk", "target_type": "image",
    "transfer_type": "image_local", "type": "image:image_local", "progress_title_type": "backingup"
}
DSM_7_TASK_3_STATUS_RUN_WITH_SCHD_SIZE_CNT = {'success': True, 'data': {
    'task_id': 3, 'state': 'backupable', 'status': 'backup', 'last_bkp_result': 'backingup', 'last_bkp_end_time': '2023/12/21 01:13',
    'last_bkp_error': '', 'last_bkp_error_code': 4401, 'last_bkp_success_time': '2023/12/21 01:12', 'last_bkp_time': '2023/12/21 01:13',
    'next_bkp_time': '2023/12/22 01:00', 'schedule': SCHEDULE_VALID, 'progress': {
        'step': 'total_size_count', 'progress': 0, 'app_done_list': [], 'app_list': [], 'avg_speed': 0, 'can_cancel': True,
        'can_suspend': False, 'current_app': '', 'current_app_action_percent': '0', 'current_app_percent': '0',
        'current_app_stage': '', 'processed_size': '0', 'scan_file_count': '0', 'title_type': 'backingup',
        'total_size': '1202233000', 'transmitted_size': '0'
}}}

# Backup state is broken, destination corrupted
DSM_7_TASK_4_LIST_BROKEN = {
    "name": "Bad: Dest Corrupt", "task_id": 4, "status": "none", "state": "restore_only",
    "last_bkp_result": "done", "data_enc": True, "data_type": "data", "ext3ShareList": [],
    "is_modified": False, "last_bkp_end_time": "2022/10/19 13:40", "last_bkp_time": "2022/10/19 13:40",
    "repo_id": 4, "source": DUMMY_SOURCE_DATA, "target_id": "vault_1.hbk", "target_type": "cloud_image",
    "transfer_type": "google_drive", "type": "cloud_image:google_drive"
}
DSM_7_TASK_4_STATUS_BROKEN = {'success': True, 'data': {
    'task_id': 4, 'status': 'none', 'state': 'restore_only', 'last_bkp_result': 'done',
    'last_bkp_error': 'SYNO.SDS.Backup.Application:error:status_target_broken', 'last_bkp_end_time': '2022/10/19 13:40',
    'last_bkp_error_code': 4467, 'last_bkp_success_time': '2022/10/19 13:21',
    'last_bkp_time': '2022/10/19 13:40', 'next_bkp_time': '', 'schedule': SCHEDULE_DISABLED
}}

# Backup idle, no schedule, otherwise OK.
DSM_7_TASK_5_LIST_IDLE_NO_SCHEDULE = {
    "name": "Idle, no schedule", "task_id": 5, "status": "none", "state": "backupable",
    "last_bkp_result": "done", "data_enc": False, "data_type": "data", "ext3ShareList": [],
    "is_modified": False, "last_bkp_end_time": "2023/12/18 14:51", "last_bkp_time": "2023/12/18 14:51",
    "repo_id": 5, "source": DUMMY_SOURCE_DATA, "target_id": "vault_3.hbk", "target_type": "image",
    "transfer_type": "image_remote", "type": "image:image_remote"
}
DSM_7_TASK_5_STATUS_IDLE_NO_SCHEDULE = {'success': True, 'data': {
    'task_id': 5, 'status': 'none', 'state': 'backupable', 'last_bkp_result': 'done', 'last_bkp_error': '',
    'last_bkp_end_time': '2023/12/18 14:51', 'last_bkp_error_code': 4401, 'last_bkp_progress': 73,
    'last_bkp_success_time': '2023/12/18 14:50', 'last_bkp_time': '2023/12/18 14:51', 'next_bkp_time': '',
    'schedule': SCHEDULE_DISABLED
}}

# Backup idle, with schedule, 100% good.
DSM_7_TASK_6_LIST_IDLE_WITH_SCHEDULE = {
    "name": "Idle with schedule", "task_id": 6, "status": "none", "state": "backupable",
    "last_bkp_result": "done", "data_enc": True, "data_type": "data", "ext3ShareList": [],
    "is_modified": False, "last_bkp_end_time": "2023/12/19 01:16", "last_bkp_time": "2023/12/19 01:16",
    "repo_id": 6, "source": DUMMY_SOURCE_DATA, "target_id": "vault_2.hbk", "target_type": "image",
    "transfer_type": "image_remote", "type": "image:image_remote"
}
DSM_7_TASK_6_STATUS_IDLE_WITH_SCHEDULE = {'success': True, 'data': {
    'task_id': 6, 'status': 'none', 'state': 'backupable', 'last_bkp_result': 'done', 'last_bkp_error': '',
    'last_bkp_end_time': '2023/12/21 01:13', 'last_bkp_error_code': 4401, 'last_bkp_success_time': '2023/12/21 01:12',
    'last_bkp_time': '2023/12/21 01:13', 'next_bkp_time': '2023/12/22 01:00', 'schedule': SCHEDULE_VALID
}}
# =============================================

# Result of list endpoint with all backup tasks
# =============================================
DSM_7_HYPERBACKUP_LIST = {"success": True, "data": {
    "total": 6, "is_data_restoring": False, "is_downloading": False, "is_lun_restoring": False,
    "is_restoring": False, "is_snapshot_restoring": False, "task_list": [
        DSM_7_TASK_1_LIST_RUN_NO_SCHD_0_PCT,
        DSM_7_TASK_2_LIST_RUN_NO_SCHD_84_PCT,
        DSM_7_TASK_3_LIST_RUN_WITH_SCHD_SIZE_CNT,
        DSM_7_TASK_4_LIST_BROKEN,
        DSM_7_TASK_5_LIST_IDLE_NO_SCHEDULE,
        DSM_7_TASK_6_LIST_IDLE_WITH_SCHEDULE
]}}

DSM_7_STATUSES = {
    1: DSM_7_TASK_1_STATUS_RUN_NO_SCHD_0_PCT,
    2: DSM_7_TASK_2_STATUS_RUN_NO_SCHD_84_PCT,
    3: DSM_7_TASK_3_STATUS_RUN_WITH_SCHD_SIZE_CNT,
    4: DSM_7_TASK_4_STATUS_BROKEN,
    5: DSM_7_TASK_5_STATUS_IDLE_NO_SCHEDULE,
    6: DSM_7_TASK_6_STATUS_IDLE_WITH_SCHEDULE
}

TARGET_DATA_ONLINE = {'success': True, 'data': {
    'capability': {'support_download': True, 'support_filter': True, 'support_statistics': True},
    'data_comp': True, 'data_enc': True, 'format_type': 'image', 'host_name': 'synology_nas', 'is_online': True,
    'last_detect_time': '', 'owner_id': 1040, 'owner_name': 'backup_user', 'support_multi_version': True,
    'uni_key': '001122AA66AAA_00_1234567890', 'used_size': 2000000000
}}
TARGET_DATA_OFFLINE = {'success': True, 'data': {
    'capability': {'support_download': True, 'support_filter': True, 'support_statistics': True},
    'data_comp': True, 'data_enc': True, 'format_type': 'image', 'host_name': 'synology_nas', 'is_online': False,
    'last_detect_time': '', 'owner_id': 1040, 'owner_name': 'backup_user', 'support_multi_version': True,
    'uni_key': '001122AA66AAA_00_1234567890',
}}
# =============================================
