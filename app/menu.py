import asyncio
import time

from app import const
from app.common import SettingsGroup, chunk, clamp, format_time, get_time_offsets, log
from app.const import _
from app.core import display, keys, logger, motor, rtc, scheduler, settings, wdt


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

    def get_min_max_cursors(self) -> tuple[int, int]:
        return 0, len(self.CURSORS) - 1

    def get_min_max_values(self) -> tuple[int, int]:
        return self.MIN_MAX_VALUES[self.pos]

    def render(self) -> None:
        display.clear()
        display.write((0, 0), b"???")
        display.flush()

    def enter(self) -> None:
        log(f"Switching to {self.__class__.__name__}")
        self.render()

    async def loop(self) -> None:
        if self.edit:
            await self.loop_edit()
        else:
            await self.loop_navi()

    async def loop_navi(self) -> None:
        await asyncio.sleep(0.05)

        key, duration = keys.get()
        if key == keys.LEFT:
            await self.loop_navi_left(duration)
        elif key == keys.RIGHT:
            await self.loop_navi_right(duration)
        elif key == keys.ENTER:
            await self.loop_navi_enter(duration)

        if key is not None:
            self.render()

    async def loop_navi_left(self, duration: float) -> None:
        _ = duration
        lo, hi = self.get_min_max_cursors()
        self.pos = clamp(self.pos - 1, lo, hi)

    async def loop_navi_right(self, duration: float) -> None:
        _ = duration
        lo, hi = self.get_min_max_cursors()
        self.pos = clamp(self.pos + 1, lo, hi)

    async def loop_navi_enter(self, duration: float) -> None:
        _ = duration
        self._enter_edit_mode()

    async def loop_edit(self) -> None:
        await asyncio.sleep(0.05)

        key, duration = keys.get()
        if key == keys.LEFT:
            self.loop_edit_left(duration)
        elif key == keys.RIGHT:
            self.loop_edit_right(duration)
        elif key == keys.ENTER:
            self.loop_edit_enter(duration)

        if key is not None:
            self.render()

    def loop_edit_left(self, duration: float) -> None:
        lo, hi = self.get_min_max_values()
        self.data[self.pos] = clamp(self.data[self.pos] - int(duration or 1), lo, hi)

    def loop_edit_right(self, duration: float) -> None:
        lo, hi = self.get_min_max_values()
        self.data[self.pos] = clamp(self.data[self.pos] + int(duration or 1), lo, hi)

    def loop_edit_enter(self, duration: float) -> None:
        _ = duration
        self._leave_edit_mode()

    def exit(self) -> None:
        pass

    async def _enter_submenu(self, instance: "Menu") -> None:
        try:
            instance.enter()
            while True:
                await instance.loop()
        except MenuExit:
            instance.exit()
            self.enter()

    def _enter_edit_mode(self) -> None:
        display.set_backlight(display.BACKLIGHT_HIGH)
        display.set_alternate_cursor()
        self.edit = True

    def _leave_edit_mode(self) -> None:
        self.edit = False
        display.set_backlight(display.BACKLIGHT_LOW)
        display.set_default_cursor()


class IdleMenu(Menu):
    def render(self) -> None:
        now = time.localtime()

        display.clear()
        display.write((0, 0), format_time(now.tm_hour, now.tm_min, now.tm_sec))
        display.write((11, 0), b"\x05!" if not wdt.enabled else b"")
        display.write((14, 0), b"\x04!" if rtc.lost_power else b"")
        display.flush()

    async def loop_navi(self) -> None:
        await super().loop_navi()

        # time should be refreshed even if there is no input
        self.render()

    async def loop_navi_left(self, duration: float) -> None:
        if duration > 3.0:
            await self._enter_submenu(MainMenu())

    async def loop_navi_right(self, duration: float) -> None:
        return

    async def loop_navi_enter(self, duration: float) -> None:
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
        _(const.MENU_OPEN),
        _(const.MENU_CLOSE),
        _(const.MENU_SET_OPEN),
        _(const.MENU_SET_CLOSE),
        _(const.MENU_SET_TIME),
        _(const.MENU_HISTORY),
        _(const.MENU_RETURN),
    )

    ID_OPEN = 0
    ID_CLOSE = 1
    ID_SET_OPEN = 2
    ID_SET_CLOSE = 3
    ID_SET_TIME = 4
    ID_HISTORY = 5
    ID_RETURN = 6

    def get_label(self) -> bytes:
        return self.LABELS[self.pos].encode()

    def enter(self) -> None:
        super().enter()
        display.set_backlight(display.BACKLIGHT_LOW)

    def render(self) -> None:
        ca, cb = self.get_cursor()
        label = self.get_label()

        display.clear()
        display.write((1, 0), b"\x00 \x01 \x7E \x7F \x04 \x02 \x05")
        display.write((1, 1), label)
        display.write(ca, b"\x06")
        display.write(cb, b"\x07")
        display.flush()

    async def loop_navi_enter(self, duration: float) -> None:
        if self.pos == self.ID_SET_OPEN:
            await self._enter_submenu(MotorMenu(motor.ACT_OPEN))
        elif self.pos == self.ID_SET_CLOSE:
            await self._enter_submenu(MotorMenu(motor.ACT_CLOSE))
        elif self.pos == self.ID_SET_TIME:
            await self._enter_submenu(SystemMenu())
        elif self.pos == self.ID_HISTORY:
            await self._enter_submenu(HistoryMenu())
        elif self.pos == self.ID_RETURN:
            raise MenuExit()
        else:
            await super().loop_navi_enter(duration)

    async def loop_edit(self) -> None:
        if self.pos == self.ID_OPEN:
            motor.run(motor.ACT_OPEN, settings.load(motor.ACT_OPEN).duration_single)
            self._leave_edit_mode()
        elif self.pos == self.ID_CLOSE:
            motor.run(motor.ACT_CLOSE, settings.load(motor.ACT_CLOSE).duration_single)
            self._leave_edit_mode()
        else:
            await super().loop_navi()

    def exit(self) -> None:
        super().exit()
        display.set_backlight(display.BACKLIGHT_OFF)


class MotorMenu(Menu):
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

    def __init__(self, name: int) -> None:
        super().__init__()

        self.initial = list(settings.load(name))
        self.data = list(self.initial)
        self.name = name

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

    async def loop_navi_enter(self, duration: float) -> None:
        if self.pos == self.ID_PREVIEW:
            await self._enter_submenu(MotorPreviewMenu(SettingsGroup(*self.data)))
        elif self.pos == self.ID_RETURN:
            raise MenuExit()
        else:
            await super().loop_navi_enter(duration)

    def exit(self) -> None:
        super().exit()

        if tuple(self.initial) != tuple(self.data):
            settings.save(self.name, SettingsGroup(*self.data))
            scheduler.restart()


class MotorPreviewMenu(Menu):
    def __init__(self, data: SettingsGroup) -> None:
        super().__init__()
        self.data = chunk(self.get_time_offset_strings(data), 2)

    def get_min_max_cursors(self) -> tuple[int, int]:
        return 0, len(self.data) - 1

    def get_time_offset_strings(self, s: SettingsGroup) -> list[bytes]:
        strings = []

        for value in get_time_offsets(s):
            hour, minute = divmod(value, const.HOUR)
            minute, second = divmod(minute, const.MINUTE)
            strings.append(format_time(hour, minute, second))

        return strings

    def render(self) -> None:
        display.clear()
        display.write((8, 0), b"--:--:--")

        lo, hi = self.get_min_max_cursors()
        display.write((0, 1), b"\x7F" if self.pos > lo else b" ")
        display.write((1, 1), f"{self.pos + 1:02}/{hi + 1:02}".encode())
        display.write((6, 1), b"\x7E" if self.pos < hi else b" ")

        try:
            display.write((8, 0), self.data[self.pos][0])
            display.write((8, 1), self.data[self.pos][1])
        except IndexError:
            pass

        display.flush()

    async def loop_navi_enter(self, duration: float) -> None:
        raise MenuExit()


class SystemMenu(Menu):
    CURSORS = (
        ((0, 0), (3, 0)),
        ((3, 0), (6, 0)),
        ((13, 1), (15, 1)),
    )

    MIN_MAX_VALUES = (
        (0, 23),
        (0, 59),
    )

    ID_RETURN = 2

    def __init__(self) -> None:
        super().__init__()

        now = time.localtime()
        self.initial = [now.tm_hour, now.tm_min]
        self.data = list(self.initial)

    def render(self) -> None:
        ca, cb = self.get_cursor()

        display.clear()
        display.write((0, 1), b"              \x03")
        display.write((1, 0), format_time(self.data[0], self.data[1]))
        display.write(ca, b"\x06")
        display.write(cb, b"\x07")
        display.flush()

    async def loop_navi_enter(self, duration: float) -> None:
        if self.pos == self.ID_RETURN:
            raise MenuExit()

        await super().loop_navi_enter(duration)

    def exit(self) -> None:
        super().exit()

        if rtc.lost_power or tuple(self.initial) != tuple(self.data):
            h, m = self.data
            rtc.datetime = time.struct_time((2000, 1, 1, h, m, 0, 0, 0, -1))
            logger.log(const.RTC_SAVE)
            scheduler.restart()


class HistoryMenu(Menu):
    MAX_VALUE = 49

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.MAX_VALUE

    def get_min_max_cursors(self) -> tuple[int, int]:
        return 0, self.MAX_VALUE

    def render(self) -> None:
        entry = logger.get(self.MAX_VALUE - self.pos)

        display.clear()
        display.write((8, 1), format_time(entry.hour, entry.minute, entry.second))
        display.write((0, 0), entry.message[:16].encode())

        lo, hi = self.get_min_max_cursors()
        display.write((0, 1), b"\x7F" if self.pos > lo else b" ")
        display.write((1, 1), f"{self.pos + 1:02}/{hi + 1:02}".encode())
        display.write((6, 1), b"\x7E" if self.pos < hi else b" ")

        display.flush()

    async def loop_navi_enter(self, duration: float) -> None:
        raise MenuExit()


async def loop() -> None:
    menu = IdleMenu()
    menu.enter()

    while True:
        await menu.loop()
