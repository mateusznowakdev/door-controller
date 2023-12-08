import board
import keypad
import rtc as _rtc
import time
from busio import I2C
from digitalio import DigitalInOut, Direction
from microcontroller import watchdog
from pwmio import PWMOut
from watchdog import WatchDogMode

from adafruit_24lc32 import EEPROM_I2C
from adafruit_character_lcd.character_lcd import Character_LCD_Mono
from adafruit_ds3231 import DS3231

from app.utils import log


class WatchDog:
    TIMEOUT = 8.0

    def __init__(self) -> None:
        self.wdt_pin = DigitalInOut(board.GP28)
        self.wdt_pin.direction = Direction.INPUT
        self.enabled = False

    def feed(self) -> None:
        if not self.enabled and self.wdt_pin.value is True:
            watchdog.timeout = WatchDog.TIMEOUT
            watchdog.mode = WatchDogMode.RESET
            self.enabled = True

            log("Watchdog has been initialized")

        if self.enabled:
            watchdog.feed()


class Motor:
    ID_OPEN = 0
    ID_CLOSE = 64

    def __init__(self) -> None:
        self._motor_f = DigitalInOut(board.GP18)
        self._motor_f.direction = Direction.OUTPUT

        self._motor_b = DigitalInOut(board.GP19)
        self._motor_b.direction = Direction.OUTPUT

    def sleep(self, duration: float) -> None:
        max_loop_duration = WatchDog.TIMEOUT / 2

        while duration > 0:
            wdt.feed()
            time.sleep(max_loop_duration if duration > max_loop_duration else duration)
            duration -= max_loop_duration

        wdt.feed()

    def run(self, motor_id: int, duration: float) -> None:
        if motor_id == Motor.ID_OPEN:
            return self.open(duration)
        if motor_id == Motor.ID_CLOSE:
            return self.close(duration)

        raise ValueError("Unknown motor_id")

    def open(self, duration: float) -> None:
        log(f"Motor #{Motor.ID_OPEN} has been started")

        self._motor_f.value = True
        self.sleep(duration)
        self._motor_f.value = False

        log(f"Motor #{Motor.ID_OPEN} has been stopped")

    def close(self, duration: float) -> None:
        log(f"Motor #{Motor.ID_CLOSE} has been started")

        self._motor_b.value = True
        self.sleep(duration)
        self._motor_b.value = False

        log(f"Motor #{Motor.ID_CLOSE} has been stopped")


class Display:
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
            columns=Display.WIDTH,
            lines=Display.HEIGHT,
        )
        self._display.create_char(0, Display.CHAR_PLAY)
        self._display.create_char(1, Display.CHAR_REWIND)
        self._display.create_char(2, Display.CHAR_MENU)
        self._display.create_char(3, Display.CHAR_CHECK)
        self._display.create_char(4, Display.CHAR_TIME)
        self._display.create_char(5, Display.CHAR_BACK)
        self._display.create_char(6, Display.CHAR_CUR_A0)
        self._display.create_char(7, Display.CHAR_CUR_A1)

        self._cur_buffer = bytearray(b" " * Display.WIDTH * Display.HEIGHT)
        self._old_buffer = self._cur_buffer[:]
        self.clear()

        self._backlight = PWMOut(board.GP3)
        self.set_backlight(Display.BACKLIGHT_OFF)

    def clear(self) -> None:
        self._cur_buffer[:] = b" " * len(self._cur_buffer)

    def write(self, pos: tuple[int, int], data: bytes) -> None:
        col, row = pos
        byte_id = row * Display.WIDTH + col

        self._cur_buffer[byte_id : byte_id + len(data)] = data

    def flush(self) -> None:
        if self._cur_buffer == self._old_buffer:
            return

        lines = []

        for row in range(0, Display.HEIGHT):
            first_byte_id = row * Display.WIDTH
            last_byte_id = (row + 1) * Display.WIDTH

            line = "".join(chr(b) for b in self._cur_buffer[first_byte_id:last_byte_id])
            lines.append(line)

        self._display.message = "\n".join(lines)
        self._old_buffer = self._cur_buffer[:]

    def set_default_cursor(self) -> None:
        self._display.create_char(6, Display.CHAR_CUR_A0)
        self._display.create_char(7, Display.CHAR_CUR_A1)

    def set_alternate_cursor(self) -> None:
        self._display.create_char(6, Display.CHAR_CUR_B0)
        self._display.create_char(7, Display.CHAR_CUR_B1)

    def set_backlight(self, value: int) -> None:
        self._backlight.duty_cycle = value * 65535 // 100


class Keys:
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
        if self._key_number in Keys.HOLD_KEYS and diff > Keys.HOLD_THRESHOLD:
            return self._key_number, diff

        # key is pressed but it was acknowledged
        if self._press_read:
            return None, 0.0

        # key is pressed
        self._press_read = True
        return self._key_number, 0.0


wdt = WatchDog()
wdt.feed()

i2c = I2C(scl=board.GP11, sda=board.GP10)
log("I2C bus has been initialized")

rtc = DS3231(i2c)
_rtc.set_time_source(rtc)
log("RTC has been initialized")

eeprom = EEPROM_I2C(i2c, 0x57)
eeprom._max_size = 32768  # pylint:disable=protected-access
log("EEPROM has been initialized")

motor = Motor()
log("Motor has been initialized")

display = Display()
log("Display has been initialized")

keys = Keys()
log("Keypad has been initialized")
