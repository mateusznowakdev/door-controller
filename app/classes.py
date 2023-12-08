from collections import namedtuple

Settings = namedtuple(
    "Settings",
    ("first_hr", "first_min", "last_hr", "last_min", "duration", "divided_by"),
)

Task = namedtuple(
    "Task",
    ("timestamp", "function"),
)
