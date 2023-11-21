import board
import keypad
import time
from digitalio import DigitalInOut
from pwmio import PWMOut

from adafruit_character_lcd.character_lcd import Character_LCD_Mono
from adafruit_datetime import datetime


class Display:
    WIDTH = 16
    HEIGHT = 2

    BACKLIGHT_HIGH = 50
    BACKLIGHT_LOW = 15
    BACKLIGHT_OFF = 0

    CHAR_PLAY = 0b00000, 0b11000, 0b10110, 0b10001, 0b10110, 0b11000, 0b00000, 0b00000
    CHAR_REWIND = 0b00000, 0b00011, 0b01101, 0b10001, 0b01101, 0b00011, 0b00000, 0b00000
    CHAR_UP = 0b00000, 0b00100, 0b01110, 0b10101, 0b00100, 0b00100, 0b00000, 0b00000
    CHAR_DOWN = 0b00000, 0b00100, 0b00100, 0b10101, 0b01110, 0b00100, 0b00000, 0b00000
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
        self._display.create_char(2, Display.CHAR_UP)
        self._display.create_char(3, Display.CHAR_DOWN)
        self._display.create_char(4, Display.CHAR_TIME)
        self._display.create_char(5, Display.CHAR_BACK)
        self._display.create_char(6, Display.CHAR_CUR_A0)
        self._display.create_char(7, Display.CHAR_CUR_A1)

        self._buffer = bytearray(b" " * Display.WIDTH * Display.HEIGHT)
        self.clear()

        self._backlight = PWMOut(board.GP3)

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


def clamp(value: int, low: int, hi: int) -> int:
    return max(min(value, hi), low)


class BaseMenu:
    def enter(self) -> None:
        self.render()

    def render(self) -> None:
        pass

    def loop(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def _enter_submenu(self, instance: "BaseMenu") -> None:
        try:
            instance.enter()
            while True:
                instance.loop()
        except MenuExit:
            instance.exit()
            self.enter()


class MenuExit(Exception):
    pass


class IdleMenu(BaseMenu):
    def enter(self) -> None:
        super().enter()
        display.set_backlight(Display.BACKLIGHT_OFF)

    def render(self) -> None:
        display.clear()
        display.write((0, 0), b"" + datetime.now().time().isoformat())
        display.flush()

    def loop(self) -> None:
        time.sleep(1.0)

        key, _ = keys.get()
        if key == Keys.ENTER:
            self._enter_submenu(MainMenu())

        self.render()


class MainMenu(BaseMenu):
    MIN_CURSOR = 0
    MAX_CURSOR = 6

    SET_OPEN = 2
    RETURN = 6

    CURSOR_POSITIONS = (
        ((0, 0), (2, 0)),
        ((2, 0), (4, 0)),
        ((4, 0), (6, 0)),
        ((6, 0), (8, 0)),
        ((8, 0), (10, 0)),
        ((10, 0), (12, 0)),
        ((12, 0), (14, 0)),
    )

    CURSOR_LABELS = (
        b"Open",
        b"Close",
        b"Set up opening",
        b"Set up closing",
        b"Set system time",
        b"Event log",
        b"Return",
    )

    def __init__(self) -> None:
        super().__init__()
        self.cursor = 0

    def enter(self) -> None:
        super().enter()
        display.set_backlight(Display.BACKLIGHT_LOW)

    def render(self) -> None:
        cursor_a, cursor_b = MainMenu.CURSOR_POSITIONS[self.cursor]

        display.clear()
        display.write((1, 0), b"\x00 \x01 \x02 \x03 \x04 \xD0 \x05")
        display.write((1, 1), MainMenu.CURSOR_LABELS[self.cursor])
        display.write(cursor_a, b"\x06")
        display.write(cursor_b, b"\x07")
        display.flush()

    def loop(self) -> None:
        time.sleep(0.05)

        key, _ = keys.get()
        if key == Keys.LEFT:
            if self.cursor != MainMenu.MIN_CURSOR:
                self.cursor -= 1
        elif key == Keys.RIGHT:
            if self.cursor != MainMenu.MAX_CURSOR:
                self.cursor += 1
        elif key == Keys.ENTER:
            if self.cursor == MainMenu.SET_OPEN:
                self._enter_submenu(OpenMenu())
            elif self.cursor == MainMenu.RETURN:
                raise MenuExit()

        if key is not None:
            self.render()


class OpenMenu(BaseMenu):
    MIN_CURSOR = 0
    MAX_CURSOR = 7

    FIELDS = (0, 1, 2, 3, 4, 5)
    PREVIEW = 6
    RETURN = 7

    CURSOR_POSITIONS = (
        ((0, 0), (3, 0)),
        ((3, 0), (6, 0)),
        ((8, 0), (11, 0)),
        ((11, 0), (14, 0)),
        ((0, 1), (5, 1)),
        ((5, 1), (9, 1)),
        ((10, 1), (12, 1)),
        ((12, 1), (15, 1)),
    )

    CURSOR_MIN_MAX_VALUES = (
        (0, 23),
        (0, 59),
        (0, 23),
        (0, 59),
        (0, 900),
        (0, 30),
    )

    def __init__(self) -> None:
        super().__init__()

        self.cursor = 0
        self.edit = False

        self.values = [1, 12, 23, 34, 456, 56]

    def render(self) -> None:
        cursor_a, cursor_b = OpenMenu.CURSOR_POSITIONS[self.cursor]

        display.clear()
        display.write((1, 0), b"  :   -   :  ")
        display.write((1, 1), b"   s   x  \xD0 OK")
        display.write((1, 0), f"{self.values[0]:02}".encode())
        display.write((4, 0), f"{self.values[1]:02}".encode())
        display.write((9, 0), f"{self.values[2]:02}".encode())
        display.write((12, 0), f"{self.values[3]:02}".encode())
        display.write((1, 1), f"{self.values[4]:3}".encode())
        display.write((6, 1), f"{self.values[5]:2}".encode())
        display.write(cursor_a, b"\x06")
        display.write(cursor_b, b"\x07")
        display.flush()

    def loop(self) -> None:
        if self.edit:
            self._loop_edit()
        else:
            self._loop_navi()

    def _loop_navi(self) -> None:
        time.sleep(0.05)

        key, _ = keys.get()
        if key == Keys.LEFT:
            if self.cursor != OpenMenu.MIN_CURSOR:
                self.cursor -= 1
        elif key == Keys.RIGHT:
            if self.cursor != OpenMenu.MAX_CURSOR:
                self.cursor += 1
        elif key == Keys.ENTER:
            if self.cursor in OpenMenu.FIELDS:
                display.set_alternate_cursor()
                display.set_backlight(Display.BACKLIGHT_HIGH)
                self.edit = True
            elif self.cursor == OpenMenu.RETURN:
                raise MenuExit()

        if key is not None:
            self.render()

    def _loop_edit(self) -> None:
        if self.cursor not in OpenMenu.FIELDS:
            return

        time.sleep(0.05)

        value = self.values[self.cursor]
        low, hi = OpenMenu.CURSOR_MIN_MAX_VALUES[self.cursor]

        key, duration = keys.get()
        if key == Keys.LEFT:
            self.values[self.cursor] = clamp(value - int(duration or 1), low, hi)
        elif key == Keys.RIGHT:
            self.values[self.cursor] = clamp(value + int(duration or 1), low, hi)
        elif key == Keys.ENTER:
            display.set_default_cursor()
            display.set_backlight(Display.BACKLIGHT_LOW)
            self.edit = False

        if key is not None:
            self.render()


if __name__ == "__main__":
    menu = IdleMenu()
    menu.enter()

    while True:
        menu.loop()
