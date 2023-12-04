from app.hardware import Motor, eeprom
from app.utils import get_checksum, log, verify_checksum


class SettingService:
    DEFAULT_SETTINGS = [0, 0, 0, 0, 0, 1]

    @staticmethod
    def get(motor_id: int) -> list[int]:
        data = eeprom[motor_id : motor_id + 8]
        log(f"Motor #{motor_id} settings have been retrieved")

        if not verify_checksum(data):
            log("Checksum is invalid, using default settings")
            return list(SettingService.DEFAULT_SETTINGS)

        return [data[0], data[1], data[2], data[3], data[4] + data[5] * 256, data[6]]

    @staticmethod
    def set(motor_id: int, data: list[int]) -> None:
        d = [data[0], data[1], data[2], data[3], data[4] % 256, data[4] // 256, data[5]]
        d.append(get_checksum(d))

        eeprom[motor_id : motor_id + 8] = bytearray(d)

        log(f"Motor #{motor_id} settings have been changed")

    @staticmethod
    def reset() -> None:
        for motor_id in Motor.ID_LIST:
            SettingService.set(motor_id, list(SettingService.DEFAULT_SETTINGS))
