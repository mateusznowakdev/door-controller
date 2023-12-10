SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR

BOARD_INIT = 0

SETTINGS_LOAD_ERR = 16
SETTINGS_SAVE = 17
RTC_SAVE = 18

SCHEDULER_INIT = 32
SCHEDULER_RST = 33
SCHEDULER_ERR = 34
SCHEDULER_ACT = 35

ACT_OPEN_START = 48
ACT_OPEN_STOP = 49
ACT_CLOSE_START = 50
ACT_CLOSE_STOP = 51

LOG_INVALID = 255

MESSAGES = {
    BOARD_INIT: "Board initialized",
    #
    SETTINGS_LOAD_ERR: "Invalid settings, using defaults",
    SETTINGS_SAVE: "Settings updated",
    RTC_SAVE: "RTC time changed",
    #
    SCHEDULER_INIT: "Scheduler initialized",
    SCHEDULER_RST: "Scheduler restarted",
    SCHEDULER_ERR: "Could not initialize the scheduler",
    SCHEDULER_ACT: "Scheduled task is executed",
    #
    ACT_OPEN_START: "Opening started",
    ACT_OPEN_STOP: "Opening stopped",
    ACT_CLOSE_START: "Closing started",
    ACT_CLOSE_STOP: "Closing stopped",
    #
    LOG_INVALID: "Invalid entry",
}
