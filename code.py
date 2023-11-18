import board
import time
from digitalio import DigitalInOut
from keypad import Keys
from pwmio import PWMOut

from adafruit_character_lcd.character_lcd import Character_LCD_Mono

DISPLAY_WIDTH = 16
DISPLAY_HEIGHT = 2

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

display.create_char(
    0, [0b00000, 0b11000, 0b10110, 0b10001, 0b10110, 0b11000, 0b00000, 0b00000]
)
display.create_char(
    1, [0b00000, 0b00011, 0b01101, 0b10001, 0b01101, 0b00011, 0b00000, 0b00000]
)
display.create_char(
    2, [0b00000, 0b00100, 0b01110, 0b10101, 0b00100, 0b00100, 0b00000, 0b00000]
)
display.create_char(
    3, [0b00000, 0b00100, 0b00100, 0b10101, 0b01110, 0b00100, 0b00000, 0b00000]
)
display.create_char(
    4, [0b00000, 0b01110, 0b10101, 0b10111, 0b10001, 0b01110, 0b00000, 0b00000]
)
display.create_char(
    5, [0b00000, 0b01000, 0b11110, 0b01001, 0b00001, 0b00110, 0b00000, 0b00000]
)
display.create_char(
    6, [0b00101, 0b00000, 0b00100, 0b00000, 0b00100, 0b00000, 0b00101, 0b00000]
)
display.create_char(
    7, [0b10100, 0b00000, 0b00100, 0b00000, 0b00100, 0b00000, 0b10100, 0b00000]
)

display_bl = PWMOut(board.GP3)

display_buf = bytearray(DISPLAY_WIDTH * DISPLAY_HEIGHT)

keys = Keys(pins=(board.GP13, board.GP14, board.GP15), value_when_pressed=False)


def set_backlight(percentage):
    display_bl.duty_cycle = percentage * 65535 // 100


def clear_buffer():
    display_buf[:] = b" " * len(display_buf)


def update_buffer(pos, data):
    col, row = pos
    byte_id = row * DISPLAY_WIDTH + col

    display_buf[byte_id : byte_id + len(data)] = data


def send_buffer():
    lines = []

    for row in range(0, DISPLAY_HEIGHT):
        first_byte_id = row * DISPLAY_WIDTH
        last_byte_id = (row + 1) * DISPLAY_WIDTH

        line = "".join(chr(b) for b in display_buf[first_byte_id:last_byte_id])
        lines.append(line)

    display.message = "\n".join(lines)


class Menu:
    def render(self):
        raise NotImplementedError()

    def loop(self):
        raise NotImplementedError()


class MainMenu(Menu):
    MIN_CURSOR = 0
    MAX_CURSOR = 6

    LABELS = (
        b"Open",
        b"Close",
        b"Set up opening",
        b"Set up closing",
        b"Set system time",
        b"Event log",
        b"Return",
    )

    def __init__(self):
        super().__init__()
        self.cursor = 0

    def render(self):
        clear_buffer()
        update_buffer((1, 0), b"\x00 \x01 \x02 \x03 \x04 \xD0 \x05")
        update_buffer((1, 1), MainMenu.LABELS[self.cursor])
        update_buffer((self.cursor * 2, 0), b"\x06")
        update_buffer((self.cursor * 2 + 2, 0), b"\x07")
        send_buffer()

    def loop(self):
        event = keys.events.get()
        if event and event.pressed:
            if event.key_number == 0 and self.cursor != MainMenu.MIN_CURSOR:
                self.cursor -= 1
            if event.key_number == 1 and self.cursor != MainMenu.MAX_CURSOR:
                self.cursor += 1
            self.render()

        time.sleep(0.1)


if __name__ == "__main__":
    set_backlight(25)

    menu = MainMenu()
    menu.render()

    while True:
        menu.loop()
