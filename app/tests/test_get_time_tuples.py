from app.classes import Settings
from app.utils import get_time_offsets

S = 1
M = 60 * S
H = 60 * M


def test_day_schedule():
    expected = [
        9 * H + 0 * M + 0 * S,
        9 * H + 56 * M + 40 * S,
        10 * H + 53 * M + 20 * S,
        11 * H + 50 * M + 0 * S,
        12 * H + 46 * M + 40 * S,
        13 * H + 43 * M + 20 * S,
        14 * H + 40 * M + 0 * S,
        15 * H + 36 * M + 40 * S,
        16 * H + 33 * M + 20 * S,
        17 * H + 30 * M + 0 * S,
    ]
    actual = get_time_offsets(Settings(9, 0, 17, 30, 456, 10))

    assert expected == actual


def test_day_schedule_split_by_two():
    expected = [
        9 * H + 0 * M,
        17 * H + 30 * M,
    ]
    actual = get_time_offsets(Settings(9, 0, 17, 30, 456, 2))

    assert expected == actual


def test_day_schedule_split_by_one():
    expected = [
        9 * H + 0 * M,
    ]
    actual = get_time_offsets(Settings(9, 0, 17, 30, 456, 1))

    assert expected == actual


def test_day_schedule_no_time():
    expected = []
    actual = get_time_offsets(Settings(9, 0, 17, 30, 0, 10))

    assert expected == actual


def test_night_schedule():
    expected = [
        17 * H + 30 * M + 0 * S,
        19 * H + 13 * M + 20 * S,
        20 * H + 56 * M + 40 * S,
        22 * H + 40 * M + 0 * S,
        0 * H + 23 * M + 20 * S,
        2 * H + 6 * M + 40 * S,
        3 * H + 50 * M + 0 * S,
        5 * H + 33 * M + 20 * S,
        7 * H + 16 * M + 40 * S,
        9 * H + 0 * M + 0 * S,
    ]
    actual = get_time_offsets(Settings(17, 30, 9, 0, 456, 10))

    assert expected == actual
