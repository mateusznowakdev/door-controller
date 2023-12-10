import asyncio
import board
import keypad
import rtc as _rtc
import time
from busio import I2C
from digitalio import DigitalInOut, Direction, Pull
from microcontroller import watchdog
from pwmio import PWMOut
from watchdog import WatchDogMode

from adafruit_24lc32 import EEPROM_I2C
from adafruit_character_lcd.character_lcd import Character_LCD_Mono
from adafruit_ds3231 import DS3231

from app import const
from app.const import _
from app.shared import get_checksum, get_time_offsets, log, verify_checksum
from app.types import LogT, SettingsT, TaskT


class _WatchDog:
    TIMEOUT = 8.0

    def __init__(self) -> None:
        self.wdt_pin = DigitalInOut(board.GP28)
        self.wdt_pin.direction = Direction.INPUT
        self.wdt_pin.pull = Pull.DOWN
        self.enabled = False

    def feed(self) -> None:
        if not self.enabled and self.wdt_pin.value is True:
            watchdog.timeout = self.TIMEOUT
            watchdog.mode = WatchDogMode.RESET
            self.enabled = True

            log("Watchdog initialized")

        if self.enabled:
            watchdog.feed()


class _Logger:
    START_ADDRESS = 1024
    END_ADDRESS = 1024 + 128

    FRAME_SIZE = 8

    END_FRAME = bytearray((255, 0, 0, 0, 0, 0, 0, 213))

    def __init__(self) -> None:
        self.address = self.START_ADDRESS

        raw = eeprom[self.START_ADDRESS : self.END_ADDRESS]

        for address in range(self.START_ADDRESS, self.END_ADDRESS, self.FRAME_SIZE):
            start = address - self.START_ADDRESS
            if raw[start : start + self.FRAME_SIZE] == self.END_FRAME:
                self.address = address
                break

    def get(self, log_id: int) -> LogT:
        address = self.address
        for __ in range(log_id + 1):
            address -= self.FRAME_SIZE
            if address < self.START_ADDRESS:
                address = self.END_ADDRESS - self.FRAME_SIZE

        raw = eeprom[address : address + self.FRAME_SIZE]
        if not verify_checksum(raw):
            return LogT(255, _(255), 0, 0, 0)

        return LogT(raw[0], _(raw[0]), raw[1], raw[2], raw[3])

    def log(self, message_id: int) -> None:
        log(_(message_id))

        now = time.localtime()

        raw = [message_id, now.tm_hour, now.tm_min, now.tm_sec, 0, 0, 0]
        raw.append(get_checksum(raw))

        a = self.address
        b = a + self.FRAME_SIZE
        eeprom[a:b] = bytearray(raw)

        self.address += self.FRAME_SIZE
        if self.address == self.END_ADDRESS:
            self.address = self.START_ADDRESS

        a = self.address
        b = a + self.FRAME_SIZE
        eeprom[a:b] = self.END_FRAME


class _Motor:
    # Action ID describes the first EEPROM address for its settings
    ACT_OPEN = 0
    ACT_CLOSE = 64

    def __init__(self) -> None:
        self._motor_f = DigitalInOut(board.GP18)
        self._motor_f.direction = Direction.OUTPUT

        self._motor_b = DigitalInOut(board.GP19)
        self._motor_b.direction = Direction.OUTPUT

    def sleep(self, duration: float) -> None:
        max_loop_duration = wdt.TIMEOUT / 2

        while duration > 0:
            wdt.feed()
            time.sleep(max_loop_duration if duration > max_loop_duration else duration)
            duration -= max_loop_duration

        wdt.feed()

    def run(self, action_id: int, duration: float) -> None:
        if action_id == self.ACT_OPEN:
            self.open(duration)
        elif action_id == self.ACT_CLOSE:
            self.close(duration)
        else:
            raise ValueError("Unknown action ID")

    def open(self, duration: float) -> None:
        logger.log(const.ACT_OPEN_START)

        self._motor_f.value = True
        self.sleep(duration)
        self._motor_f.value = False

        logger.log(const.ACT_OPEN_STOP)

    def close(self, duration: float) -> None:
        logger.log(const.ACT_CLOSE_START)

        self._motor_b.value = True
        self.sleep(duration)
        self._motor_b.value = False

        logger.log(const.ACT_CLOSE_STOP)


class _Display:
    WIDTH = 16
    HEIGHT = 2

    BACKLIGHT_HIGH = 50
    BACKLIGHT_LOW = 15
    BACKLIGHT_OFF = 1

    CHAR_PLAY = 0b00000, 0b11000, 0b10110, 0b10001, 0b10110, 0b11000, 0b00000, 0b00000
    CHAR_REWIND = 0b00000, 0b00011, 0b01101, 0b10001, 0b01101, 0b00011, 0b00000, 0b00000
    CHAR_MENU = 0b00000, 0b01110, 0b00000, 0b01110, 0b00000, 0b01110, 0b00000, 0b00000
    CHAR_CHECK = 0b00000, 0b00001, 0b00010, 0b00100, 0b10100, 0b01000, 0b00000, 0b00000
    CHAR_TIME = 0b00000, 0b01110, 0b10101, 0b10111, 0b10001, 0b01110, 0b00000, 0b00000
    CHAR_BACK = 0b00000, 0b01000, 0b11110, 0b01001, 0b00001, 0b00110, 0b00000, 0b00000
    CHAR_CUR_A0 = 0b00101, 0b00000, 0b00100, 0b00000, 0b00100, 0b00000, 0b00101, 0b00000
    CHAR_CUR_A1 = 0b10100, 0b00000, 0b00100, 0b00000, 0b00100, 0b00000, 0b10100, 0b00000
    CHAR_CUR_B0 = 0b00111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00111, 0b00000
    CHAR_CUR_B1 = 0b11100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b11100, 0b00000

    def __init__(self) -> None:
        self._display = Character_LCD_Mono(
            rs=DigitalInOut(board.GP9),
            en=DigitalInOut(board.GP8),
            db4=DigitalInOut(board.GP7),
            db5=DigitalInOut(board.GP6),
            db6=DigitalInOut(board.GP5),
            db7=DigitalInOut(board.GP4),
            columns=self.WIDTH,
            lines=self.HEIGHT,
        )
        self._display.create_char(0, self.CHAR_PLAY)
        self._display.create_char(1, self.CHAR_REWIND)
        self._display.create_char(2, self.CHAR_MENU)
        self._display.create_char(3, self.CHAR_CHECK)
        self._display.create_char(4, self.CHAR_TIME)
        self._display.create_char(5, self.CHAR_BACK)
        self._display.create_char(6, self.CHAR_CUR_A0)
        self._display.create_char(7, self.CHAR_CUR_A1)

        self._cur_buffer = bytearray(b" " * self.WIDTH * self.HEIGHT)
        self._old_buffer = self._cur_buffer[:]
        self.clear()

        self._backlight = PWMOut(board.GP3)
        self.set_backlight(self.BACKLIGHT_OFF)

    def clear(self) -> None:
        self._cur_buffer[:] = b" " * len(self._cur_buffer)

    def write(self, pos: tuple[int, int], data: bytes) -> None:
        col, row = pos
        byte_id = row * self.WIDTH + col

        self._cur_buffer[byte_id : byte_id + len(data)] = data

    def flush(self) -> None:
        if self._cur_buffer == self._old_buffer:
            return

        lines = []

        for row in range(0, self.HEIGHT):
            first_byte_id = row * self.WIDTH
            last_byte_id = (row + 1) * self.WIDTH

            line = "".join(chr(b) for b in self._cur_buffer[first_byte_id:last_byte_id])
            lines.append(line)

        self._display.message = "\n".join(lines)
        self._old_buffer = self._cur_buffer[:]

    def set_default_cursor(self) -> None:
        self._display.create_char(6, self.CHAR_CUR_A0)
        self._display.create_char(7, self.CHAR_CUR_A1)

    def set_alternate_cursor(self) -> None:
        self._display.create_char(6, self.CHAR_CUR_B0)
        self._display.create_char(7, self.CHAR_CUR_B1)

    def set_backlight(self, value: int) -> None:
        self._backlight.duty_cycle = value * 65535 // 100


class _Keys:
    LEFT = 0
    RIGHT = 1
    ENTER = 2

    HOLD_KEYS = [LEFT, RIGHT]
    HOLD_THRESHOLD = 1.0

    def __init__(self) -> None:
        self._keys = keypad.Keys(
            pins=(board.GP13, board.GP14, board.GP15),
            value_when_pressed=False,
            max_events=1,
        )

        self._key_number = None
        self._key_timestamp = 0.0
        self._press_read = False

    def get(self) -> tuple[int | None, float]:
        event = None
        while last_event := self._keys.events.get():
            event = last_event

        if event:
            if event.pressed:
                self._key_number = event.key_number
                self._key_timestamp = time.monotonic()
                self._press_read = False
            else:
                self._key_number = None
                self._key_timestamp = 0.0

        # no key is pressed
        if self._key_number is None:
            return None, 0.0

        # supported key is held
        diff = time.monotonic() - self._key_timestamp
        if self._key_number in self.HOLD_KEYS and diff > self.HOLD_THRESHOLD:
            return self._key_number, diff

        # key is pressed but it was acknowledged
        if self._press_read:
            return None, 0.0

        # key is pressed
        self._press_read = True
        return self._key_number, 0.0


class _Settings:
    DEFAULTS = SettingsT(0, 0, 0, 0, 0, 1)

    def load(self, action_id: int) -> SettingsT:
        raw = eeprom[action_id : action_id + 8]

        if not verify_checksum(raw):
            logger.log(const.SETTINGS_LOAD_ERR)
            return self.DEFAULTS

        return SettingsT(raw[0], raw[1], raw[2], raw[3], raw[4] + raw[5] * 256, raw[6])

    def save(self, action_id: int, obj: SettingsT) -> None:
        raw = [obj[0], obj[1], obj[2], obj[3], obj[4] % 256, obj[4] // 256, obj[5]]
        raw.append(get_checksum(raw))

        eeprom[action_id : action_id + 8] = bytearray(raw)

        logger.log(const.SETTINGS_SAVE)

    def reset(self) -> None:
        self.save(motor.ACT_OPEN, self.DEFAULTS)
        self.save(motor.ACT_CLOSE, self.DEFAULTS)


class _Scheduler:
    def __init__(self) -> None:
        self.tasks = self.get_tasks()

    def restart(self) -> None:
        self.tasks = self.get_tasks()

    def get_tasks(self) -> list[TaskT]:
        if rtc.lost_power:
            logger.log(const.SCHEDULER_ERR)
            return []

        opening_tasks = self.get_tasks_for_action(motor.ACT_OPEN)
        closing_tasks = self.get_tasks_for_action(motor.ACT_CLOSE)

        logger.log(const.SCHEDULER_INIT)
        return opening_tasks + closing_tasks

    def get_tasks_for_action(self, action_id: int) -> list[TaskT]:
        tasks = []

        now = time.localtime()
        now_ts = time.mktime(now)

        midnight_ts = time.mktime(
            (now.tm_year, now.tm_mon, now.tm_mday, 0, 0, 0, 0, 0, -1)
        )

        motor_settings = settings.load(action_id)
        offsets = get_time_offsets(motor_settings)

        for offset in offsets:
            # add extra 5s delay before any task can be run
            ts = midnight_ts + offset
            while ts < now_ts + 5 * const.SECOND:
                ts += const.DAY

            task = TaskT(
                ts,
                lambda: motor.run(action_id, motor_settings.duration_single),
            )
            tasks.append(task)

        return tasks

    async def loop(self) -> None:
        wdt.feed()
        await asyncio.sleep(wdt.TIMEOUT / 2)

        now = time.time()

        for idx, task in enumerate(self.tasks):
            if now < task.timestamp:
                continue

            logger.log(const.SCHEDULER_ACT)
            task.function()
            self.tasks[idx] = TaskT(task.timestamp + const.DAY, task.function)

            # skip processing other operations for now
            return


wdt = _WatchDog()
wdt.feed()

i2c = I2C(scl=board.GP11, sda=board.GP10)
log("I2C initialized")

rtc = DS3231(i2c)
_rtc.set_time_source(rtc)
log("RTC initialized")

eeprom = EEPROM_I2C(i2c, 0x57)
log("EEPROM initialized")

motor = _Motor()
log("Motor initialized")

display = _Display()
log("Display initialized")

keys = _Keys()
log("Keys initialized")

logger = _Logger()
logger.log(const.BOARD_INIT)

settings = _Settings()
scheduler = _Scheduler()


async def loop() -> None:
    while True:
        await scheduler.loop()
