"""Synology HyperBackup API constants."""

PROP_NAME = "name"
PROP_TRANSFER_TYPE = "transfer_type"
PROP_LAST_RESULT = "last_bkp_result"  # Raw previous result
PROP_LAST_BACKUP_TIME = "last_bkp_time"
PROP_LAST_BACKUP_END_TIME = "last_bkp_end_time"
PROP_LAST_BACKUP_ERROR = "last_bkp_error"
PROP_NEXT_BACKUP_TIME = "next_bkp_time"
PROP_LAST_BACKUP_PROGRESS = "last_bkp_progress"
PROP_LAST_BACKUP_SUCCESS_TIME = "last_bkp_success_time"
PROP_STATE = "state"
PROP_STATUS = "status"  # 'raw status' from API.
PROP_TARGET_ID = "target_id"
PROP_TASKID = "task_id"
PROP_ONLINE = "is_online"
PROP_USED_SIZE = "used_size"
PROP_PROGRESS = "progress"

# Hyper backup Task raw status values
PROP_STATUS_NONE = "none"
PROP_STATUS_WAITING = "waiting"
PROP_STATUS_BACKUP = "backup"
PROP_STATUS_DETECT = "detect"
PROP_STATUS_VER_DEL = "version_deleting"
PROP_STATUS_PREP_VER_DEL = "preparing_version_delete"
PROP_STATUS_DETECT_WAIT = "detect_waiting"

# Hyper backup raw result values
RESULT_NONE = "none"
RESULT_DONE = "done"
RESULT_RESUME = "resuming"
RESULT_SUSPEND = "suspend"

# Raw state values
STATE_BACKUP = "backupable"
STATE_EXPORT = "exportable"
STATE_IMPORT = "importable"
STATE_RELINK = "relinkable"
STATE_ERROR = "error_detect"
STATE_BROKEN = "broken"
STATE_RESTORE_ONLY = "restore_only"
STATE_UNAUTH = "unauth"
STATE_END_SERVICE = "endofservice"

# Hyper backup *derived* Health values
HEALTH_GOOD = "Good"
HEALTH_WARN = "Warning"
HEALTH_CRIT = "Error"

# Hyper backup *derived* status values
STATUS_OK = "OK"
STATUS_RUNNING = "Backing up"
STATUS_RUNNING_NO_SCHEDULE = "Backing up (no schedule)"
STATUS_WAITING = "Waiting to backup"
STATUS_RESUMING = "Resuming"
STATUS_SUSPENDED = "Suspended"
STATUS_NEVER_RUN = "Never backed up"
# Backup task has run successfully, but there is no active schedule
STATUS_NO_SCHEDULE = "No schedule set"
STATUS_RESTORE_ONLY = "Restore Only"  # Not backup-able, but can restore
STATUS_UNKNOWN = "Unhandled/Unknown"
STATUS_DETECT = "Waiting: target offline"
# An error occurred, or unknown combination of raw status/prev result.
STATUS_ERROR = "Error"
