import math
import time

BASE_CHECKSUM = 42

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR


def chunk(items: list, size: int) -> list[tuple]:
    chunk_count = math.ceil(len(items) / size)
    return [items[x * size : (x + 1) * size] for x in range(chunk_count)]


def clamp(value: int, low: int, hi: int) -> int:
    return max(min(value, hi), low)


def format_time(hour: int, minute: int, second: int | None = None) -> bytes:
    if second is None:
        return f"{hour:02}:{minute:02}".encode()
    else:
        return f"{hour:02}:{minute:02}:{second:02}".encode()


def get_checksum(data: list[int]) -> int:
    result = BASE_CHECKSUM

    for value in data:
        result ^= value

    return result


def get_time_offsets(data: list[int]) -> list[int]:
    first_hr, first_min, last_hr, last_min, duration, divided_by = data

    first_sec = first_hr * HOUR + first_min * MINUTE
    last_sec = last_hr * HOUR + last_min * MINUTE

    if duration == 0:
        return []
    if divided_by < 2:
        return [first_sec]

    # handle night schedule
    if first_sec > last_sec:
        last_sec += DAY

    total_distance = last_sec - first_sec
    distance = total_distance / (divided_by - 1)

    offsets = []
    for idx in range(divided_by):
        offsets.append(round(first_sec + idx * distance) % DAY)

    return offsets


def get_time_offset_strings(data: list[int]) -> list[bytes]:
    strings = []

    for value in get_time_offsets(data):
        hour, minute = divmod(value, HOUR)
        minute, second = divmod(minute, MINUTE)
        strings.append(format_time(hour, minute, second))

    return strings


def log(message: str) -> None:
    print(f"[{time.monotonic():10.2f}] {message}")


def verify_checksum(data: list[int]) -> bool:
    return get_checksum(data[:-1]) == data[-1]
