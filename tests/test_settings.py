def minutes_to_time(m: int) -> tuple[int, int]:
    return divmod(m, 60)


def time_to_minutes(h: int, m: int) -> int:
    return h * 60 + m


def run(
    start_hour: int,
    start_minute: int,
    end_hour: int,
    end_minute: int,
    duration: int,
    divided_by: int,
) -> tuple[tuple[int, int], ...]:
    first_minute = time_to_minutes(start_hour, start_minute)
    last_minute = time_to_minutes(end_hour, end_minute)

    total_distance = last_minute - first_minute
    distance = total_distance / (divided_by - 1)

    entries = tuple(
        minutes_to_time(int(first_minute + x * distance)) for x in range(divided_by)
    )

    return entries


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
    actual = run(9, 0, 17, 30, 0, 1)

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
