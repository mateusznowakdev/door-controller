import math

SECONDS_IN_MINUTE = 60
MINUTES_IN_HOUR = 60
MINUTES_IN_DAY = 1440


def clamp(value: int, low: int, hi: int) -> int:
    return max(min(value, hi), low)


def format_time(hour: int, minute: int) -> bytes:
    return f"{hour:02}:{minute:02}".encode()


def format_time_full(hour: int, minute: int, second: int) -> bytes:
    return f"{hour:02}:{minute:02}:{second:02}".encode()


def get_time_tuples(
    start_hour: int,
    start_minute: int,
    end_hour: int,
    end_minute: int,
    duration: int,
    divided_by: int,
) -> tuple[tuple[int, int], ...]:
    if duration == 0:
        return ()
    if divided_by < 2:
        return ((start_hour, start_minute),)

    first_minute = time_to_minutes(start_hour, start_minute)
    last_minute = time_to_minutes(end_hour, end_minute)

    # handle night schedule
    if first_minute > last_minute:
        last_minute += MINUTES_IN_DAY

    total_distance = last_minute - first_minute
    distance = total_distance / (divided_by - 1)

    # handle distance between start and end times being too small
    safe_distance_seconds = math.ceil(duration / divided_by) + SECONDS_IN_MINUTE / 2
    safe_distance_minutes = math.ceil(safe_distance_seconds / SECONDS_IN_MINUTE)
    distance = max(distance, safe_distance_minutes)

    entries = []
    for idx in range(divided_by):
        minutes = int(first_minute + idx * distance) % MINUTES_IN_DAY
        time = minutes_to_time(minutes)
        entries.append(time)

    return tuple(entries)


def minutes_to_time(minutes: int) -> tuple[int, int]:
    return divmod(minutes, MINUTES_IN_HOUR)


def time_to_minutes(hour: int, minute: int) -> int:
    return hour * MINUTES_IN_HOUR + minute
