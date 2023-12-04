import math
import time

BASE_CHECKSUM = 42

MINUTES_IN_DAY = 1440
MINUTES_IN_HOUR = 60
SECONDS_IN_MINUTE = 60


def chunk(items: list, size: int) -> list[tuple]:
    chunk_count = math.ceil(len(items) / size)
    return [items[x * size : (x + 1) * size] for x in range(chunk_count)]


def clamp(value: int, low: int, hi: int) -> int:
    return max(min(value, hi), low)


def format_time(hour: int, minute: int) -> bytes:
    return f"{hour:02}:{minute:02}".encode()


def format_time_full(hour: int, minute: int, second: int) -> bytes:
    return f"{hour:02}:{minute:02}:{second:02}".encode()


def get_checksum(data: list[int]) -> int:
    result = BASE_CHECKSUM

    for value in data:
        result ^= value

    return result


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


def log(message: str) -> None:
    print(f"[{time.monotonic():10.2f}] {message}")


def minutes_to_time(minutes: int) -> tuple[int, int]:
    return divmod(minutes, MINUTES_IN_HOUR)


def time_to_minutes(hour: int, minute: int) -> int:
    return hour * MINUTES_IN_HOUR + minute


def verify_checksum(data: list[int]) -> bool:
    return get_checksum(data[:-1]) == data[-1]
