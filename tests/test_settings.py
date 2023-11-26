MINUTES_IN_HOUR = 60
MINUTES_IN_DAY = 1440


def minutes_to_time(minutes: int) -> tuple[int, int]:
    return divmod(minutes, MINUTES_IN_HOUR)


def time_to_minutes(hour: int, minute: int) -> int:
    return hour * MINUTES_IN_HOUR + minute


def run(
    start_hour: int,
    start_minute: int,
    end_hour: int,
    end_minute: int,
    duration: int,
    divided_by: int,
) -> tuple[tuple[int, int], ...]:
    if duration == 0:
        return ()
    if divided_by == 1:
        return ((start_hour, start_minute),)

    first_minute = time_to_minutes(start_hour, start_minute)
    last_minute = time_to_minutes(end_hour, end_minute)

    if first_minute > last_minute:
        last_minute += MINUTES_IN_DAY

    total_distance = last_minute - first_minute
    distance = total_distance / (divided_by - 1)

    entries = []
    for idx in range(divided_by):
        minutes = int(first_minute + idx * distance) % MINUTES_IN_DAY
        time = minutes_to_time(minutes)
        entries.append(time)

    return tuple(entries)


def test_day_schedule():
    expected = (
        (9, 0),
        (9, 56),
        (10, 53),
        (11, 50),
        (12, 46),
        (13, 43),
        (14, 40),
        (15, 36),
        (16, 33),
        (17, 30),
    )
    actual = run(9, 0, 17, 30, 456, 10)

    assert expected == actual


def test_day_schedule_split_by_two():
    expected = ((9, 0), (17, 30))
    actual = run(9, 0, 17, 30, 456, 2)

    assert expected == actual


def test_day_schedule_split_by_one():
    expected = ((9, 0),)
    actual = run(9, 0, 17, 30, 456, 1)

    assert expected == actual


def test_day_schedule_no_time():
    expected = ()
    actual = run(9, 0, 17, 30, 0, 10)

    assert expected == actual


def test_night_schedule():
    expected = (
        (17, 30),
        (19, 13),
        (20, 56),
        (22, 40),
        (0, 23),
        (2, 6),
        (3, 50),
        (5, 33),
        (7, 16),
        (9, 0),
    )
    actual = run(17, 30, 9, 0, 456, 10)

    assert expected == actual


def test_tight_schedule():
    expected = (
        (9, 0),
        (9, 2),
        (9, 4),
        (9, 6),
        (9, 8),
        (9, 10),
        (9, 12),
        (9, 14),
        (9, 16),
        (9, 18),
    )
    actual = run(9, 0, 9, 0, 456, 10)

    assert expected == actual
