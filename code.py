import board
import time
from digitalio import DigitalInOut
from keypad import Event, Keys
from pwmio import PWMOut

from adafruit_character_lcd.character_lcd import Character_LCD_Mono
from adafruit_datetime import datetime

DISPLAY_WIDTH = 16
DISPLAY_HEIGHT = 2

BACKLIGHT_HIGH = 50
BACKLIGHT_LOW = 15
BACKLIGHT_OFF = 0

KEY_L = 0
KEY_R = 1
KEY_OK = 2

display = Character_LCD_Mono(
    rs=DigitalInOut(board.GP9),
    en=DigitalInOut(board.GP8),
    db4=DigitalInOut(board.GP7),
    db5=DigitalInOut(board.GP6),
    db6=DigitalInOut(board.GP5),
    db7=DigitalInOut(board.GP4),
    columns=DISPLAY_WIDTH,
    lines=DISPLAY_HEIGHT,
)

CHAR_PLAY = 0b00000, 0b11000, 0b10110, 0b10001, 0b10110, 0b11000, 0b00000, 0b00000
CHAR_REWIND = 0b00000, 0b00011, 0b01101, 0b10001, 0b01101, 0b00011, 0b00000, 0b00000
CHAR_UP = 0b00000, 0b00100, 0b01110, 0b10101, 0b00100, 0b00100, 0b00000, 0b00000
CHAR_DOWN = 0b00000, 0b00100, 0b00100, 0b10101, 0b01110, 0b00100, 0b00000, 0b00000
CHAR_TIME = 0b00000, 0b01110, 0b10101, 0b10111, 0b10001, 0b01110, 0b00000, 0b00000
CHAR_BACK = 0b00000, 0b01000, 0b11110, 0b01001, 0b00001, 0b00110, 0b00000, 0b00000
CHAR_CURSOR_A0 = 0b00101, 0b00000, 0b00100, 0b00000, 0b00100, 0b00000, 0b00101, 0b00000
CHAR_CURSOR_A1 = 0b10100, 0b00000, 0b00100, 0b00000, 0b00100, 0b00000, 0b10100, 0b00000
CHAR_CURSOR_B0 = 0b00111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00111, 0b00000
CHAR_CURSOR_B1 = 0b11100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b11100, 0b00000

display.create_char(0, CHAR_PLAY)
display.create_char(1, CHAR_REWIND)
display.create_char(2, CHAR_UP)
display.create_char(3, CHAR_DOWN)
display.create_char(4, CHAR_TIME)
display.create_char(5, CHAR_BACK)
display.create_char(6, CHAR_CURSOR_A0)
display.create_char(7, CHAR_CURSOR_A1)

display_bl = PWMOut(board.GP3)

display_buf = bytearray(DISPLAY_WIDTH * DISPLAY_HEIGHT)

keys = Keys(pins=(board.GP13, board.GP14, board.GP15), value_when_pressed=False)


def clamp(value: int, low: int, hi: int) -> int:
    return max(min(value, hi), low)


def set_default_cursor() -> None:
    display.create_char(6, CHAR_CURSOR_A0)
    display.create_char(7, CHAR_CURSOR_A1)


def set_alternate_cursor() -> None:
    display.create_char(6, CHAR_CURSOR_B0)
    display.create_char(7, CHAR_CURSOR_B1)


def set_backlight(percentage: int) -> None:
    display_bl.duty_cycle = percentage * 65535 // 100


def clear_buffer() -> None:
    display_buf[:] = b" " * len(display_buf)


def update_buffer(pos: tuple[int, int], data: bytes) -> None:
    col, row = pos
    byte_id = row * DISPLAY_WIDTH + col

    display_buf[byte_id : byte_id + len(data)] = data


def send_buffer() -> None:
    lines = []

    for row in range(0, DISPLAY_HEIGHT):
        first_byte_id = row * DISPLAY_WIDTH
        last_byte_id = (row + 1) * DISPLAY_WIDTH

        line = "".join(chr(b) for b in display_buf[first_byte_id:last_byte_id])
        lines.append(line)

    display.message = "\n".join(lines)


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
        set_backlight(BACKLIGHT_OFF)

    def render(self) -> None:
        clear_buffer()
        update_buffer((0, 0), b"" + datetime.now().time().isoformat())
        send_buffer()

    def loop(self) -> None:
        event = keys.events.get()
        if event and event.pressed:
            if event.key_number == KEY_OK:
                self._enter_submenu(MainMenu())

        self.render()
        time.sleep(1.0)


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
        set_backlight(BACKLIGHT_LOW)

    def render(self) -> None:
        cursor_a, cursor_b = MainMenu.CURSOR_POSITIONS[self.cursor]

        clear_buffer()
        update_buffer((1, 0), b"\x00 \x01 \x02 \x03 \x04 \xD0 \x05")
        update_buffer((1, 1), MainMenu.CURSOR_LABELS[self.cursor])
        update_buffer(cursor_a, b"\x06")
        update_buffer(cursor_b, b"\x07")
        send_buffer()

    def loop(self) -> None:
        event = keys.events.get()
        if event and event.pressed:
            if event.key_number == KEY_L:
                if self.cursor != MainMenu.MIN_CURSOR:
                    self.cursor -= 1
            if event.key_number == KEY_R:
                if self.cursor != MainMenu.MAX_CURSOR:
                    self.cursor += 1
            if event.key_number == KEY_OK:
                if self.cursor == MainMenu.SET_OPEN:
                    self._enter_submenu(OpenMenu())
                if self.cursor == MainMenu.RETURN:
                    raise MenuExit()
            self.render()

        time.sleep(0.1)


class OpenMenu(BaseMenu):
    MIN_CURSOR = 0
    MAX_CURSOR = 7

    NUM_FIELDS = (0, 1, 2, 3, 4, 5)
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
        (0, 120),
        (0, 25),
    )

    def __init__(self) -> None:
        super().__init__()

        self.cursor = 0
        self.edit = False

        self.values = [1, 12, 23, 34, 456, 56]

    def render(self) -> None:
        cursor_a, cursor_b = OpenMenu.CURSOR_POSITIONS[self.cursor]

        clear_buffer()
        update_buffer((1, 0), b"  :   -   :  ")
        update_buffer((1, 1), b"   s   x  \xD0 OK")
        update_buffer((1, 0), f"{self.values[0]:02}".encode())
        update_buffer((4, 0), f"{self.values[1]:02}".encode())
        update_buffer((9, 0), f"{self.values[2]:02}".encode())
        update_buffer((12, 0), f"{self.values[3]:02}".encode())
        update_buffer((1, 1), f"{self.values[4]:3}".encode())
        update_buffer((6, 1), f"{self.values[5]:2}".encode())
        update_buffer(cursor_a, b"\x06")
        update_buffer(cursor_b, b"\x07")
        send_buffer()

    def loop(self) -> None:
        event = keys.events.get()
        if event and event.pressed:
            if self.edit:
                self._loop_edit(event)
            else:
                self._loop_navi(event)
            self.render()

        time.sleep(0.1)

    def _loop_navi(self, event: Event) -> None:
        if event.key_number == KEY_L:
            if self.cursor != OpenMenu.MIN_CURSOR:
                self.cursor -= 1
        if event.key_number == KEY_R:
            if self.cursor != OpenMenu.MAX_CURSOR:
                self.cursor += 1
        if event.key_number == KEY_OK:
            if self.cursor in OpenMenu.NUM_FIELDS:
                set_alternate_cursor()
                set_backlight(BACKLIGHT_HIGH)
                self.edit = True
            if self.cursor == OpenMenu.RETURN:
                raise MenuExit()

    def _loop_edit(self, event: Event) -> None:
        value = self.values[self.cursor]
        low, hi = OpenMenu.CURSOR_MIN_MAX_VALUES[self.cursor]

        if event.key_number == KEY_L:
            if self.cursor in OpenMenu.NUM_FIELDS:
                self.values[self.cursor] = clamp(value - 1, low, hi)
        if event.key_number == KEY_R:
            if self.cursor in OpenMenu.NUM_FIELDS:
                self.values[self.cursor] = clamp(value + 1, low, hi)
        if event.key_number == KEY_OK:
            if self.cursor in OpenMenu.NUM_FIELDS:
                set_default_cursor()
                set_backlight(BACKLIGHT_LOW)
                self.edit = False


if __name__ == "__main__":
    menu = IdleMenu()
    menu.enter()

    while True:
        menu.loop()
