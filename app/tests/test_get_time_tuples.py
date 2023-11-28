from app.core import TimeService

get_time_tuples = TimeService.get_time_tuples


def test_day_schedule():
    expected = [
        (9, 0),
        (9, 57),
        (10, 53),
        (11, 50),
        (12, 47),
        (13, 43),
        (14, 40),
        (15, 37),
        (16, 33),
        (17, 30),
    ]
    actual = get_time_tuples([9, 0, 17, 30, 456, 10])

    assert expected == actual


def test_day_schedule_split_by_two():
    expected = [(9, 0), (17, 30)]
    actual = get_time_tuples([9, 0, 17, 30, 456, 2])

    assert expected == actual


def test_day_schedule_split_by_one():
    expected = [(9, 0)]
    actual = get_time_tuples([9, 0, 17, 30, 456, 1])

    assert expected == actual


def test_day_schedule_no_time():
    expected = []
    actual = get_time_tuples([9, 0, 17, 30, 0, 10])

    assert expected == actual


def test_night_schedule():
    expected = [
        (17, 30),
        (19, 13),
        (20, 57),
        (22, 40),
        (0, 23),
        (2, 7),
        (3, 50),
        (5, 33),
        (7, 17),
        (9, 0),
    ]
    actual = get_time_tuples([17, 30, 9, 0, 456, 10])

    assert expected == actual


def test_tight_schedule():
    expected = [
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
    ]
    actual = get_time_tuples([9, 0, 9, 0, 456, 10])

    assert expected == actual
