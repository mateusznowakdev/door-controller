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
ACT_OPEN_START = 32
ACT_OPEN_START_AUTO = 33
ACT_OPEN_START_MEASURE = 34
ACT_OPEN_STOP = 35
ACT_CLOSE_START = 36
ACT_CLOSE_START_AUTO = 36
ACT_CLOSE_START_MEASURE = 37
ACT_CLOSE_STOP = 39

MENU_PREVIEW = 128
MENU_OPEN = 129
MENU_CLOSE = 130
MENU_SET_OPEN = 131
MENU_SET_CLOSE = 132
MENU_SET_TIME = 133
MENU_HISTORY = 134
MENU_RETURN = 135

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
        ACT_OPEN_START: "Opening (1)",
        ACT_OPEN_START_AUTO: "Opening (A)",
        ACT_OPEN_START_MEASURE: "Opening (M)",
        ACT_OPEN_STOP: "Opened",
        ACT_CLOSE_START: "Closing (1)",
        ACT_CLOSE_START_AUTO: "Closing (A)",
        ACT_CLOSE_START_MEASURE: "Closing (M)",
        ACT_CLOSE_STOP: "Closed",
        INVALID: "(empty)",
        MENU_PREVIEW: "Preview",
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
        ACT_OPEN_START: "Otwieranie (1)",
        ACT_OPEN_START_AUTO: "Otwieranie (A)",
        ACT_OPEN_START_MEASURE: "Otwieranie (M)",
        ACT_OPEN_STOP: "Otworzono",
        ACT_CLOSE_START: "Zamykanie (1)",
        ACT_CLOSE_START_AUTO: "Zamykanie (A)",
        ACT_CLOSE_START_MEASURE: "Zamykanie (M)",
        ACT_CLOSE_STOP: "Zamknieto",
        INVALID: "(pusty)",
        MENU_PREVIEW: "Podglad",
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
