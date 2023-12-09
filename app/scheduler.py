import asyncio
import time

from app import logging, settings
from app.classes import Task
from app.hardware import Motor, WatchDog, logger, motor, rtc, wdt
from app.utils import DAY, SECOND, get_time_offsets

_tasks = []


def init() -> None:
    global _tasks  # pylint:disable=global-statement

    if rtc.lost_power:
        logger.log(logging.SCHEDULER_ERR)
        return

    opening_tasks = get_tasks_for_action(Motor.ACT_OPEN)
    closing_tasks = get_tasks_for_action(Motor.ACT_CLOSE)

    _tasks = opening_tasks + closing_tasks

    logger.log(logging.SCHEDULER_INIT)


def get_tasks_for_action(action_id: int) -> list[Task]:
    tasks = []

    now = time.localtime()
    now_ts = time.mktime(now)

    midnight_ts = time.mktime((now.tm_year, now.tm_mon, now.tm_mday, 0, 0, 0, 0, 0, -1))

    motor_settings = settings.load(action_id)
    offsets = get_time_offsets(motor_settings)

    for offset in offsets:
        # add extra 5s delay before any task can be run
        ts = midnight_ts + offset
        while ts < now_ts + 5 * SECOND:
            ts += DAY

        task = Task(ts, lambda: motor.run(action_id, motor_settings.duration_single))
        tasks.append(task)

    return tasks


async def _loop() -> None:
    wdt.feed()
    await asyncio.sleep(WatchDog.TIMEOUT / 2)

    now = time.time()

    for idx, task in enumerate(_tasks):
        if now < task.timestamp:
            continue

        logger.log(logging.SCHEDULER_ACT)
        task.function()
        _tasks[idx] = Task(task.timestamp + DAY, task.function)

        # skip processing other operations for now
        return


async def loop() -> None:
    init()

    while True:
        await _loop()


restart = init
