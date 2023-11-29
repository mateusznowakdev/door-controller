import math
import time

from app.hardware import Motor, eeprom, rtc
from app.utils import log, minutes_to_time, time_to_minutes

SECONDS_IN_MINUTE = 60
MINUTES_IN_DAY = 1440


class SettingService:
    @staticmethod
    def get(motor_id: int) -> list[int]:
        data = eeprom[motor_id : motor_id + 7]
        log(f"Motor #{motor_id} settings have been retrieved")

        return [data[0], data[1], data[2], data[3], data[4] + data[5] * 256, data[6]]

    @staticmethod
    def set(motor_id: int, data: list[int]) -> None:
        d = [data[0], data[1], data[2], data[3], data[4] % 256, data[4] // 256, data[5]]
        eeprom[motor_id : motor_id + 7] = bytearray(d)

        log(f"Motor #{motor_id} settings have been changed")

    @staticmethod
    def reset() -> None:
        for motor_id in (Motor.ID_FORWARDS, Motor.ID_BACKWARDS):
            SettingService.set(motor_id, [0, 0, 0, 0, 0, 1])


class TimeService:
    @staticmethod
    def get_current_time_tuple() -> tuple[int, int, int]:
        return rtc.datetime[3:6]

    @staticmethod
    def get_time_tuples(data: list[int]) -> list[tuple[int, int]]:
        first_hr, first_min, last_hr, last_min, duration, divided_by = data

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

    @staticmethod
    def is_time_valid() -> bool:
        return not rtc.lost_power

    @staticmethod
    def set_time(data: list[int]) -> None:
        h1, m1, _ = TimeService.get_current_time_tuple()
        h2, m2 = data

        if h1 != h2 or m1 != m2 or not TimeService.is_time_valid():
            rtc.datetime = time.struct_time((2020, 1, 1, h2, m2, 0, 0, 0, -1))
            log("System time has been updated")
