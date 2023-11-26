def run(sh: int, sm: int, eh: int, em: int, dur: int, div: int) -> None:
    raise NotImplementedError()


def test_day_schedule():
    expected = ()
    actual = run(9, 0, 17, 30, 456, 10)

    assert expected == actual


def test_day_schedule_split_by_two():
    expected = ()
    actual = run(9, 0, 17, 30, 456, 2)

    assert expected == actual


def test_day_schedule_split_by_one():
    expected = ()
    actual = run(9, 0, 17, 30, 456, 1)

    assert expected == actual


def test_day_schedule_no_time():
    expected = ()
    actual = run(9, 0, 17, 30, 0, 1)

    assert expected == actual


def test_night_schedule():
    expected = ()
    actual = run(17, 30, 9, 0, 456, 10)

    assert expected == actual


def test_tight_schedule():
    expected = ()
    actual = run(9, 0, 9, 0, 456, 10)

    assert expected == actual
