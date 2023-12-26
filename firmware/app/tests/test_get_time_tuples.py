from app.const import HOUR, MINUTE, SECOND
from app.shared import get_time_offsets
from app.types import SettingsT


def test_day_schedule():
    expected = [
        9 * HOUR + 0 * MINUTE + 0 * SECOND,
        9 * HOUR + 56 * MINUTE + 40 * SECOND,
        10 * HOUR + 53 * MINUTE + 20 * SECOND,
        11 * HOUR + 50 * MINUTE + 0 * SECOND,
        12 * HOUR + 46 * MINUTE + 40 * SECOND,
        13 * HOUR + 43 * MINUTE + 20 * SECOND,
        14 * HOUR + 40 * MINUTE + 0 * SECOND,
        15 * HOUR + 36 * MINUTE + 40 * SECOND,
        16 * HOUR + 33 * MINUTE + 20 * SECOND,
        17 * HOUR + 30 * MINUTE + 0 * SECOND,
    ]
    actual = get_time_offsets(SettingsT(9, 0, 17, 30, 456, 10))

    assert expected == actual


def test_day_schedule_split_by_two():
    expected = [
        9 * HOUR + 0 * MINUTE,
        17 * HOUR + 30 * MINUTE,
    ]
    actual = get_time_offsets(SettingsT(9, 0, 17, 30, 456, 2))

    assert expected == actual


def test_day_schedule_split_by_one():
    expected = [
        9 * HOUR + 0 * MINUTE,
    ]
    actual = get_time_offsets(SettingsT(9, 0, 17, 30, 456, 1))

    assert expected == actual


def test_day_schedule_no_time():
    expected = []
    actual = get_time_offsets(SettingsT(9, 0, 17, 30, 0, 10))

    assert expected == actual


def test_night_schedule():
    expected = [
        17 * HOUR + 30 * MINUTE + 0 * SECOND,
        19 * HOUR + 13 * MINUTE + 20 * SECOND,
        20 * HOUR + 56 * MINUTE + 40 * SECOND,
        22 * HOUR + 40 * MINUTE + 0 * SECOND,
        0 * HOUR + 23 * MINUTE + 20 * SECOND,
        2 * HOUR + 6 * MINUTE + 40 * SECOND,
        3 * HOUR + 50 * MINUTE + 0 * SECOND,
        5 * HOUR + 33 * MINUTE + 20 * SECOND,
        7 * HOUR + 16 * MINUTE + 40 * SECOND,
        9 * HOUR + 0 * MINUTE + 0 * SECOND,
    ]
    actual = get_time_offsets(SettingsT(17, 30, 9, 0, 456, 10))

    assert expected == actual
