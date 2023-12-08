from app.classes import Settings
from app.hardware import Motor, eeprom
from app.utils import get_checksum, log, verify_checksum

DEFAULTS = Settings(0, 0, 0, 0, 0, 1)


def load(motor_id: int) -> Settings:
    raw = eeprom[motor_id : motor_id + 8]
    log(f"Motor #{motor_id} settings have been retrieved")

    if not verify_checksum(raw):
        log("Checksum is invalid, using default settings")
        return DEFAULTS

    return Settings(raw[0], raw[1], raw[2], raw[3], raw[4] + raw[5] * 256, raw[6])


def save(motor_id: int, obj: Settings) -> None:
    raw = [obj[0], obj[1], obj[2], obj[3], obj[4] % 256, obj[4] // 256, obj[5]]
    raw.append(get_checksum(raw))

    eeprom[motor_id : motor_id + 8] = bytearray(raw)

    log(f"Motor #{motor_id} settings have been changed")


def reset() -> None:
    save(Motor.ID_OPEN, DEFAULTS)
    save(Motor.ID_CLOSE, DEFAULTS)
