import time

from app.hardware import Display, Keys, display, keys, motor
from app.utils import clamp, format_time, format_time_full


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
        h, m, s = time.localtime()[3:6]

        display.clear()
        display.write((0, 0), format_time_full(h, m, s))
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
        (0, 900),
        (1, 20),
    )

    ID_PREVIEW = 6
    ID_RETURN = 7

    def __init__(self) -> None:
        super().__init__()
        self.data = [0, 0, 0, 0, 0, 1]

    def render(self) -> None:
        ca, cb = self.get_cursor()

        display.clear()
        display.write((0, 0), b"       -      ")
        display.write((0, 1), b"    s /     \x02 \x03")
        display.write((1, 0), format_time(self.data[0], self.data[1]))
        display.write((9, 0), format_time(self.data[2], self.data[3]))
        display.write((1, 1), f"{self.data[4]:3}".encode())
        display.write((7, 1), f"{self.data[5]:2}".encode())
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
