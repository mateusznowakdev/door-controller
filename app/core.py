import time

from app.classes import Settings, Task
from app.hardware import Motor, eeprom, motor
from app.utils import DAY, SECOND, get_checksum, get_time_offsets, log, verify_checksum


class SettingService:
    DEFAULT_SETTINGS = Settings(0, 0, 0, 0, 0, 1)

    @staticmethod
    def get(motor_id: int) -> Settings:
        raw = eeprom[motor_id : motor_id + 8]
        log(f"Motor #{motor_id} settings have been retrieved")

        if not verify_checksum(raw):
            log("Checksum is invalid, using default settings")
            return SettingService.DEFAULT_SETTINGS

        return Settings(raw[0], raw[1], raw[2], raw[3], raw[4] + raw[5] * 256, raw[6])

    @staticmethod
    def set(motor_id: int, obj: Settings) -> None:
        raw = [obj[0], obj[1], obj[2], obj[3], obj[4] % 256, obj[4] // 256, obj[5]]
        raw.append(get_checksum(raw))

        eeprom[motor_id : motor_id + 8] = bytearray(raw)

        log(f"Motor #{motor_id} settings have been changed")

    @staticmethod
    def reset() -> None:
        for motor_id in Motor.ID_LIST:
            SettingService.set(motor_id, SettingService.DEFAULT_SETTINGS)


class SchedulerService:
    @staticmethod
    async def get_tasks() -> list[Task]:
        tasks = []

        now = time.localtime()
        now_ts = time.mktime(now)

        midnight_ts = time.mktime(
            (now.tm_year, now.tm_mon, now.tm_mday, 0, 0, 0, 0, 0, -1)
        )

        settings = SettingService.get(Motor.ID_OPEN)
        offsets = get_time_offsets(settings)

        for offset in offsets:
            ts = midnight_ts + offset
            while ts < now_ts + 10 * SECOND:
                ts += DAY

            task = Task(ts, lambda: motor.open(settings.duration / settings.divided_by))

            # todo: repeat for closing tasks

            tasks.append(task)

        for event in tasks:
            print(event.timestamp, time.localtime(event.timestamp))

        return tasks
