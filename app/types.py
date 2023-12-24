from collections import namedtuple

_SettingsT = namedtuple(
    "_SettingsT",
    ("first_hr", "first_min", "last_hr", "last_min", "duration", "divided_by"),
)
HistoryT = namedtuple(
    "HistoryT",
    ("id", "message", "hour", "minute", "second"),
)
TaskT = namedtuple(
    "TaskT",
    ("action_id", "timestamp", "function"),
)


class SettingsT(_SettingsT):
    @property
    def duration_single(self) -> float:
        return self.duration / self.divided_by
