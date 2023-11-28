import math
import time

MINUTES_IN_HOUR = 60


def chunk(items: list, size: int) -> list[tuple]:
    chunk_count = math.ceil(len(items) / size)
    return [items[x * size : (x + 1) * size] for x in range(chunk_count)]


def clamp(value: int, low: int, hi: int) -> int:
    return max(min(value, hi), low)


def format_time(hour: int, minute: int) -> bytes:
    return f"{hour:02}:{minute:02}".encode()


def format_time_full(hour: int, minute: int, second: int) -> bytes:
    return f"{hour:02}:{minute:02}:{second:02}".encode()


def log(message: str) -> None:
    print(f"[{time.monotonic():10.2f}] {message}")


def minutes_to_time(minutes: int) -> tuple[int, int]:
    return divmod(minutes, MINUTES_IN_HOUR)


def time_to_minutes(hour: int, minute: int) -> int:
    return hour * MINUTES_IN_HOUR + minute
