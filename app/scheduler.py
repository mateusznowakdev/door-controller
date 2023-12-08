import asyncio
import time

from app import settings
from app.classes import Task
from app.hardware import Motor, WatchDog, motor, rtc, wdt
from app.utils import DAY, SECOND, get_time_offsets, log

_tasks = []


def init() -> None:
    global _tasks  # pylint:disable=global-statement

    opening_tasks = get_tasks_by_motor(Motor.ID_OPEN)
    closing_tasks = get_tasks_by_motor(Motor.ID_CLOSE)

    _tasks = opening_tasks + closing_tasks

    log("Scheduler has been initialized")


def get_tasks_by_motor(motor_id: int) -> list[Task]:
    tasks = []

    now = time.localtime()
    now_ts = time.mktime(now)

    midnight_ts = time.mktime((now.tm_year, now.tm_mon, now.tm_mday, 0, 0, 0, 0, 0, -1))

    motor_settings = settings.load(motor_id)
    offsets = get_time_offsets(motor_settings)

    for offset in offsets:
        # add extra 5s delay before any task can be run
        ts = midnight_ts + offset
        while ts < now_ts + 5 * SECOND:
            ts += DAY

        task = Task(ts, lambda: motor.run(motor_id, motor_settings.duration_single))
        tasks.append(task)

    return tasks


async def _loop() -> None:
    wdt.feed()
    await asyncio.sleep(WatchDog.TIMEOUT / 2)

    if rtc.lost_power:
        return

    now = time.time()

    for idx, task in enumerate(_tasks):
        if now < task.timestamp:
            continue

        task.function()
        _tasks[idx] = Task(task.timestamp + DAY, task.function)

        # skip processing other operations for now
        return


async def loop() -> None:
    init()

    while True:
        await _loop()


restart = init
