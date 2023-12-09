from app import logging
from app.classes import Settings
from app.hardware import Motor, eeprom
from app.utils import get_checksum, verify_checksum

DEFAULTS = Settings(0, 0, 0, 0, 0, 1)


def load(action_id: int) -> Settings:
    raw = eeprom[action_id : action_id + 8]

    if not verify_checksum(raw):
        logging.log(logging.SETTINGS_LOAD_ERR)
        return DEFAULTS

    return Settings(raw[0], raw[1], raw[2], raw[3], raw[4] + raw[5] * 256, raw[6])


def save(action_id: int, obj: Settings) -> None:
    raw = [obj[0], obj[1], obj[2], obj[3], obj[4] % 256, obj[4] // 256, obj[5]]
    raw.append(get_checksum(raw))

    eeprom[action_id : action_id + 8] = bytearray(raw)

    logging.log(logging.SETTINGS_SAVE)


def reset() -> None:
    save(Motor.ACT_OPEN, DEFAULTS)
    save(Motor.ACT_CLOSE, DEFAULTS)
