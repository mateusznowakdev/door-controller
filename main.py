import board
import keypad
import time
from digitalio import DigitalInOut, Direction
from pwmio import PWMOut

from adafruit_character_lcd.character_lcd import Character_LCD_Mono
from adafruit_datetime import datetime


class Motor:
    def __init__(self) -> None:
        self._motor_f = DigitalInOut(board.GP18)
        self._motor_f.direction = Direction.OUTPUT

        self._motor_b = DigitalInOut(board.GP19)
        self._motor_b.direction = Direction.OUTPUT

    def start(self, duration: float) -> None:
        self._motor_f.value = True
        time.sleep(duration)
        self._motor_f.value = False

    def stop(self, duration: float) -> None:
        self._motor_b.value = True
        time.sleep(duration)
        self._motor_b.value = False


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

        self._buffer = bytearray(b" " * Display.WIDTH * Display.HEIGHT)
        self.clear()

        self._backlight = PWMOut(board.GP3)
        self.set_backlight(Display.BACKLIGHT_OFF)

    def clear(self) -> None:
        self._buffer[:] = b" " * len(self._buffer)

    def write(self, pos: tuple[int, int], data: bytes) -> None:
        col, row = pos
        byte_id = row * Display.WIDTH + col

        self._buffer[byte_id : byte_id + len(data)] = data

    def flush(self) -> None:
        lines = []

        for row in range(0, Display.HEIGHT):
            first_byte_id = row * Display.WIDTH
            last_byte_id = (row + 1) * Display.WIDTH

            line = "".join(chr(b) for b in self._buffer[first_byte_id:last_byte_id])
            lines.append(line)

        self._display.message = "\n".join(lines)

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

    HOLD_THRESHOLD = 1.0

    def __init__(self):
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

        if self._key_number is None:
            return None, 0.0

        diff = time.monotonic() - self._key_timestamp
        if diff > Keys.HOLD_THRESHOLD:
            return self._key_number, diff
        else:
            if self._press_read:
                return None, 0.0
            else:
                self._press_read = True
                return self._key_number, 0.0


display = Display()
keys = Keys()
motor = Motor()


def clamp(value: int, low: int, hi: int) -> int:
    return max(min(value, hi), low)


class MenuExit(Exception):
    pass


class Menu:
    CURSORS = ()
    MIN_MAX_VALUES = ()

    def __init__(self) -> None:
        self.data = []
        self.pos = 0
        self.edit = False

    def get_cursor(self) -> tuple[tuple[int, int], tuple[int, int]]:
        return self.CURSORS[self.pos]

    def get_min_max_values(self) -> tuple[int, int]:
        return self.MIN_MAX_VALUES[self.pos]

    def render(self) -> None:
        display.clear()
        display.write((0, 0), b"???")
        display.flush()

    def enter(self) -> None:
        self.render()

    def loop(self) -> None:
        if self.edit:
            self.loop_edit()
        else:
            self.loop_navi()

    def loop_navi(self) -> None:
        time.sleep(0.05)

        key, duration = keys.get()
        if key == Keys.LEFT:
            self.loop_navi_left(duration)
        elif key == Keys.RIGHT:
            self.loop_navi_right(duration)
        elif key == Keys.ENTER:
            self.loop_navi_enter(duration)

        if key is not None:
            self.render()

    def loop_navi_left(self, duration: float) -> None:
        _ = duration
        self.pos = clamp(self.pos - 1, 0, len(self.CURSORS) - 1)

    def loop_navi_right(self, duration: float) -> None:
        _ = duration
        self.pos = clamp(self.pos + 1, 0, len(self.CURSORS) - 1)

    def loop_navi_enter(self, duration: float) -> None:
        _ = duration
        self._enter_edit_mode()

    def loop_edit(self) -> None:
        time.sleep(0.05)

        key, duration = keys.get()
        if key == Keys.LEFT:
            self.loop_edit_left(duration)
        elif key == Keys.RIGHT:
            self.loop_edit_right(duration)
        elif key == Keys.ENTER:
            self.loop_edit_enter(duration)

        if key is not None:
            self.render()

    def loop_edit_left(self, duration: float) -> None:
        lo, hi = self.MIN_MAX_VALUES[self.pos]
        self.data[self.pos] = clamp(self.data[self.pos] - int(duration or 1), lo, hi)

    def loop_edit_right(self, duration: float) -> None:
        lo, hi = self.MIN_MAX_VALUES[self.pos]
        self.data[self.pos] = clamp(self.data[self.pos] + int(duration or 1), lo, hi)

    def loop_edit_enter(self, duration: float) -> None:
        _ = duration
        self._leave_edit_mode()

    def exit(self) -> None:
        pass

    def _enter_submenu(self, instance: "Menu") -> None:
        try:
            instance.enter()
            while True:
                instance.loop()
        except MenuExit:
            instance.exit()
            self.enter()

    def _enter_edit_mode(self) -> None:
        display.set_backlight(Display.BACKLIGHT_HIGH)
        display.set_alternate_cursor()
        self.edit = True

    def _leave_edit_mode(self) -> None:
        self.edit = False
        display.set_backlight(Display.BACKLIGHT_LOW)
        display.set_default_cursor()


class IdleMenu(Menu):
    def render(self) -> None:
        display.clear()
        display.write((0, 0), b"" + datetime.now().time().isoformat())
        display.flush()

    def loop_navi(self) -> None:
        super().loop_navi()

        # time should be refreshed even if there is no input
        self.render()
        time.sleep(0.9)

    def loop_navi_left(self, duration: float) -> None:
        if duration > 3.0:
            self._enter_submenu(MainMenu())

    def loop_navi_right(self, duration: float) -> None:
        return

    def loop_navi_enter(self, duration: float) -> None:
        return


class MainMenu(Menu):
    CURSORS = (
        ((0, 0), (2, 0)),
        ((2, 0), (4, 0)),
        ((4, 0), (6, 0)),
        ((6, 0), (8, 0)),
        ((8, 0), (10, 0)),
        ((10, 0), (12, 0)),
        ((12, 0), (14, 0)),
    )

    LABELS = (
        b"Open",
        b"Close",
        b"Set up opening",
        b"Set up closing",
        b"Set system time",
        b"Event log",
        b"Return",
    )

    ID_OPEN = 0
    ID_SET_OPEN = 2
    ID_RETURN = 6

    def get_label(self) -> bytes:
        return self.LABELS[self.pos]

    def enter(self) -> None:
        super().enter()
        display.set_backlight(Display.BACKLIGHT_LOW)

    def render(self) -> None:
        ca, cb = self.get_cursor()
        label = self.get_label()

        display.clear()
        display.write((1, 0), b"\x00 \x01 \x7E \x7F \x04 \x02 \x05")
        display.write((1, 1), label)
        display.write(ca, b"\x06")
        display.write(cb, b"\x07")
        display.flush()

    def loop_navi_enter(self, duration: float) -> None:
        if self.pos == self.ID_OPEN:
            super().loop_navi_enter(duration)
        elif self.pos == self.ID_SET_OPEN:
            self._enter_submenu(OpenMenu())
        elif self.pos == self.ID_RETURN:
            raise MenuExit()

    def loop_edit(self) -> None:
        if self.pos == self.ID_OPEN:
            motor.start(2.0)
            self._leave_edit_mode()
        else:
            super().loop_navi()

    def exit(self) -> None:
        super().exit()
        display.set_backlight(Display.BACKLIGHT_OFF)


class OpenMenu(Menu):
    CURSORS = (
        ((0, 0), (3, 0)),
        ((3, 0), (6, 0)),
        ((8, 0), (11, 0)),
        ((11, 0), (14, 0)),
        ((0, 1), (5, 1)),
        ((5, 1), (9, 1)),
        ((11, 1), (13, 1)),
        ((13, 1), (15, 1)),
    )

    MIN_MAX_VALUES = (
        (0, 23),
        (0, 59),
        (0, 23),
        (0, 59),
        (0, 500),
        (0, 20),
    )

    ID_PREVIEW = 6
    ID_RETURN = 7

    def __init__(self) -> None:
        super().__init__()
        self.data = [1, 12, 23, 34, 456, 56]

    def render(self) -> None:
        ca, cb = self.get_cursor()

        display.clear()
        display.write((1, 0), b"  :   -   :  ")
        display.write((1, 1), b"   s   x   \x02 \x03")
        display.write((1, 0), f"{self.data[0]:02}".encode())
        display.write((4, 0), f"{self.data[1]:02}".encode())
        display.write((9, 0), f"{self.data[2]:02}".encode())
        display.write((12, 0), f"{self.data[3]:02}".encode())
        display.write((1, 1), f"{self.data[4]:3}".encode())
        display.write((6, 1), f"{self.data[5]:2}".encode())
        display.write(ca, b"\x06")
        display.write(cb, b"\x07")
        display.flush()

    def loop_navi_enter(self, duration: float) -> None:
        if self.pos == self.ID_PREVIEW:
            ...
        elif self.pos == self.ID_RETURN:
            raise MenuExit()
        else:
            super().loop_navi_enter(duration)


def main() -> None:
    menu = IdleMenu()
    menu.enter()

    while True:
        menu.loop()
