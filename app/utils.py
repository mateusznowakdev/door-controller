def clamp(value: int, low: int, hi: int) -> int:
    return max(min(value, hi), low)


def format_time(hour: int, minute: int) -> bytes:
    return f"{hour:02}:{minute:02}".encode()


def format_time_full(hour: int, minute: int, second: int) -> bytes:
    return f"{hour:02}:{minute:02}:{second:02}".encode()
