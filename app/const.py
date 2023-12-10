SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR

WATCHDOG_INIT = 0
I2C_INIT = 1
RTC_INIT = 2
EEPROM_INIT = 3
LOGGER_INIT = 4
MOTOR_INIT = 5
DISPLAY_INIT = 6
KEYPAD_INIT = 7

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
ACT_UNKNOWN = 52

MENU = 64

LOG_INVALID = 255

MESSAGES = {
    WATCHDOG_INIT: "Watchdog initialized",
    I2C_INIT: "I2C bus initialized",
    RTC_INIT: "RTC initialized",
    EEPROM_INIT: "EEPROM initialized",
    LOGGER_INIT: "Logger initialized",
    MOTOR_INIT: "Motor initialized",
    DISPLAY_INIT: "Display initialized",
    KEYPAD_INIT: "Keypad initialized",
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
    ACT_UNKNOWN: "Unknown action",
    #
    MENU: "Entering menu:",
    #
    LOG_INVALID: "Invalid entry",
}
