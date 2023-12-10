from collections import namedtuple

LogEntry = namedtuple(
    "LogEntry",
    ("log_id", "hour", "minute", "second"),
)

_Settings = namedtuple(
    "_Settings",
    ("first_hr", "first_min", "last_hr", "last_min", "duration", "divided_by"),
)


class Settings(_Settings):
    @property
    def duration_single(self) -> float:
        return self.duration / self.divided_by


Task = namedtuple(
    "Task",
    ("timestamp", "function"),
)
