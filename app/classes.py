from collections import namedtuple

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
