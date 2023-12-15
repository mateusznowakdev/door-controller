import os

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR

BOARD_INIT = 0
RTC_SAVE = 8
SETTINGS_ERROR = 16
SETTINGS_SAVE = 17
SETTINGS_RESET = 18
SCHEDULER_INIT = 24
SCHEDULER_ERROR = 25
SCHEDULER_ACTION = 26
ACT_OPEN_START = 32
ACT_OPEN_STOP = 33
ACT_CLOSE_START = 34
ACT_CLOSE_STOP = 35

MENU_OPEN = 128
MENU_CLOSE = 129
MENU_SET_OPEN = 130
MENU_SET_CLOSE = 131
MENU_SET_TIME = 132
MENU_HISTORY = 133
MENU_RETURN = 134

INVALID = 255

TRANSLATIONS = {
    "en": {
        BOARD_INIT: "Device start",
        RTC_SAVE: "Clock updated",
        SETTINGS_ERROR: "Settings error",
        SETTINGS_SAVE: "Settings updated",
        SETTINGS_RESET: "Factory settings",
        SCHEDULER_INIT: "Scheduler start",
        SCHEDULER_ERROR: "Clock error",
        SCHEDULER_ACTION: "Task start",
        ACT_OPEN_START: "Opening",
        ACT_OPEN_STOP: "Opened",
        ACT_CLOSE_START: "Closing",
        ACT_CLOSE_STOP: "Closed",
        INVALID: "(empty)",
        MENU_OPEN: "Open",
        MENU_CLOSE: "Close",
        MENU_SET_OPEN: "Set opening",
        MENU_SET_CLOSE: "Set closing",
        MENU_SET_TIME: "Set clock",
        MENU_HISTORY: "History",
        MENU_RETURN: "Return",
    },
    "pl": {
        BOARD_INIT: "Start urzadzenia",
        RTC_SAVE: "Zmiana czasu",
        SETTINGS_ERROR: "Blad ustawien",
        SETTINGS_SAVE: "Zmiana ustawien",
        SETTINGS_RESET: "Ustaw.fabryczne",
        SCHEDULER_INIT: "Start planisty",
        SCHEDULER_ERROR: "Blad zegara",
        SCHEDULER_ACTION: "Start zadania",
        ACT_OPEN_START: "Otwieranie",
        ACT_OPEN_STOP: "Otworzono",
        ACT_CLOSE_START: "Zamykanie",
        ACT_CLOSE_STOP: "Zamknieto",
        INVALID: "(pusty)",
        MENU_OPEN: "Otworz",
        MENU_CLOSE: "Zamknij",
        MENU_SET_OPEN: "Ust.otwierania",
        MENU_SET_CLOSE: "Ust.zamykania",
        MENU_SET_TIME: "Ust.zegara",
        MENU_HISTORY: "Historia",
        MENU_RETURN: "Powrot",
    },
}

LANG = os.getenv("LANG", "en")
