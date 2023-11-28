import math

from app.hardware import rtc
from app.utils import minutes_to_time, time_to_minutes

SECONDS_IN_MINUTE = 60
MINUTES_IN_DAY = 1440


class TimeService:
    @staticmethod
    def get_current_time_tuple() -> tuple[int, int, int]:
        return rtc.datetime[3:6]

    @staticmethod
    def get_time_tuples(settings: list[int]) -> list[tuple[int, int]]:
        (first_hr, first_min, last_hr, last_min, duration, divided_by) = settings

        if duration == 0:
            return []
        if divided_by < 2:
            return [(first_hr, first_min)]

        first_minute = time_to_minutes(first_hr, first_min)
        last_minute = time_to_minutes(last_hr, last_min)

        # handle night schedule
        if first_minute > last_minute:
            last_minute += MINUTES_IN_DAY

        total_distance = last_minute - first_minute
        distance = total_distance / (divided_by - 1)

        # handle distance between start and end times being too small
        safe_distance_seconds = math.ceil(duration / divided_by) + SECONDS_IN_MINUTE / 2
        safe_distance_minutes = math.ceil(safe_distance_seconds / SECONDS_IN_MINUTE)
        distance = max(distance, safe_distance_minutes)

        tuples = []
        for idx in range(divided_by):
            minutes = round(first_minute + idx * distance) % MINUTES_IN_DAY
            time_tuple = minutes_to_time(minutes)
            tuples.append(time_tuple)

        return tuples