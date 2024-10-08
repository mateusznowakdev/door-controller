import asyncio
import time

from app import const
from app.core import display, keys, logger, motor, rtc, scheduler, settings, wdt
from app.shared import _, chunk, clamp, format_time, log
from app.types import SettingsT


class MenuExit(Exception):
    def __init__(self, code: int = 0) -> None:
        self.code = code


class Menu:
    CURSORS = ()
    MIN_MAX_VALUES = ()

    ALT_ICONS = False

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

        if self.ALT_ICONS:
            display.set_alternate_icons()

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
        if self.ALT_ICONS:
            display.set_default_icons()

    async def _enter_submenu(self, instance: "Menu") -> int:
        try:
            instance.enter()
            while True:
                await instance.loop()
        except MenuExit as e:
            instance.exit()
            self.enter()
            return e.code

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
        display.write((11, 0), b"\x04!" if not wdt.enabled else b"")
        display.write((14, 0), b"\x05!" if rtc.lost_power else b"")
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
        ((14, 0), (16, 0)),
    )

    LABELS = (
        _(const.MENU_PREVIEW),
        _(const.MENU_OPEN),
        _(const.MENU_CLOSE),
        _(const.MENU_SET_OPEN),
        _(const.MENU_SET_CLOSE),
        _(const.MENU_SET_TIME),
        _(const.MENU_HISTORY),
        _(const.MENU_RETURN),
    )

    ID_PREVIEW = 0
    ID_OPEN = 1
    ID_CLOSE = 2
    ID_SET_OPEN = 3
    ID_SET_CLOSE = 4
    ID_SET_TIME = 5
    ID_HISTORY = 6
    ID_RETURN = 7

    def get_label(self) -> bytes:
        return self.LABELS[self.pos].encode()

    def enter(self) -> None:
        super().enter()
        display.set_backlight(display.BACKLIGHT_LOW)

    def render(self) -> None:
        (cax, cay), (cbx, cby) = self.get_cursor()
        label = self.get_label()

        # scroll menu to the left
        offset = 0 if self.pos < 4 else -1

        display.clear()
        display.write((1 + offset, 0), b"\x05 \x00 \x01 \x02 \x03 \x04 \xD0 \x7F")
        display.write((cax + offset, cay), b"\x06")
        display.write((cbx + offset, cby), b"\x07")
        display.write((1, 1), label)
        display.flush()

    async def loop_navi_enter(self, duration: float) -> None:
        if self.pos == self.ID_PREVIEW:
            await self._enter_submenu(PreviewMenu())
        elif self.pos == self.ID_SET_OPEN:
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
        reason = motor.REASON_ONESHOT

        if self.pos == self.ID_OPEN:
            motor.open(reason, settings.load(motor.ACT_OPEN).duration_single)
            self._leave_edit_mode()
        elif self.pos == self.ID_CLOSE:
            motor.close(reason, settings.load(motor.ACT_CLOSE).duration_single)
            self._leave_edit_mode()
        else:
            await super().loop_navi()

    def exit(self) -> None:
        super().exit()
        display.set_backlight(display.BACKLIGHT_OFF)


class PreviewMenu(Menu):
    def __init__(self) -> None:
        super().__init__()

        tasks = sorted(scheduler.tasks, key=lambda t: t.timestamp)
        self.data = chunk(tasks, 2)

    def get_min_max_cursors(self) -> tuple[int, int]:
        return 0, len(self.data) - 1

    def render(self) -> None:
        display.clear()
        display.write((5, 0), b"--:--:--")

        lo, hi = self.get_min_max_cursors()
        display.write((0, 1), b"\x7F" if self.pos > lo else b" ")
        display.write((1, 1), f"{self.pos + 1:02}".encode())
        display.write((3, 1), b"\x7E" if self.pos < hi else b" ")

        for row in (0, 1):
            try:
                task = self.data[self.pos][row]
            except IndexError:
                break

            if task.action_id == motor.ACT_OPEN:
                icon = b"(\x00)"
            elif task.action_id == motor.ACT_CLOSE:
                icon = b"(\x01)"
            else:
                icon = b""

            t = time.localtime(task.timestamp)
            display.write((5, row), format_time(t.tm_hour, t.tm_min, t.tm_sec))
            display.write((13, row), icon)

        display.flush()

    async def loop_navi_enter(self, duration: float) -> None:
        raise MenuExit()


class MotorMenu(Menu):
    CURSORS = (
        ((0, 0), (3, 0)),
        ((3, 0), (6, 0)),
        ((8, 0), (11, 0)),
        ((11, 0), (14, 0)),
        ((0, 1), (5, 1)),
        ((5, 1), (9, 1)),
        ((9, 1), (11, 1)),
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

    ALT_ICONS = True

    ID_DURATION = 4
    ID_MEASURE = 6
    ID_OK = 7
    ID_CANCEL = 8

    def __init__(self, action_id: int) -> None:
        super().__init__()

        self.initial = list(settings.load(action_id))
        self.data = list(self.initial)
        self.action_id = action_id

    def render(self) -> None:
        ca, cb = self.get_cursor()

        display.clear()
        display.write((1, 0), format_time(self.data[0], self.data[1]))
        display.write((7, 0), b"-")
        display.write((9, 0), format_time(self.data[2], self.data[3]))
        display.write((1, 1), f"{self.data[4]:3}s".encode())
        display.write((6, 1), f"/{self.data[5]}".encode())
        display.write((10, 1), b"\x05 \x02 \x03")
        display.write(ca, b"\x06")
        display.write(cb, b"\x07")
        display.flush()

    async def loop_navi_enter(self, duration: float) -> None:
        if self.pos == self.ID_MEASURE:
            duration = await self._enter_submenu(MeasurementMenu(self.action_id))
            self.data[self.ID_DURATION] = duration
        elif self.pos == self.ID_OK:
            self.save()
            raise MenuExit()
        elif self.pos == self.ID_CANCEL:
            raise MenuExit()
        else:
            await super().loop_navi_enter(duration)

    def save(self) -> None:
        if tuple(self.initial) != tuple(self.data):
            settings.save(self.action_id, SettingsT(*self.data))
            scheduler.restart()


class MeasurementMenu(Menu):
    MAX_VALUE = 999

    def __init__(self, action_id: int) -> None:
        super().__init__()

        reason = motor.REASON_MEASURE

        if action_id == motor.ACT_OPEN:
            coro = motor.aopen(reason, self.MAX_VALUE)
        elif action_id == motor.ACT_CLOSE:
            coro = motor.aclose(reason, self.MAX_VALUE)
        else:
            raise ValueError("Unknown action ID")

        self.time = time.time()
        self.task = asyncio.create_task(coro)

    def get_duration(self) -> int:
        return int(time.time() - self.time)

    def render(self) -> None:
        display.clear()
        display.write((0, 1), f"{self.get_duration():4}s ...".encode())
        display.flush()

    async def loop_navi(self) -> None:
        await super().loop_navi()

        # time should be refreshed even if there is no input
        self.render()

    async def loop_navi_left(self, duration: float) -> None:
        return

    async def loop_navi_right(self, duration: float) -> None:
        return

    async def loop_navi_enter(self, duration: float) -> None:
        try:
            self.task.cancel()
        except asyncio.CancelledError:
            pass

        duration = min(self.get_duration(), self.MAX_VALUE)
        raise MenuExit(duration)


class SystemMenu(Menu):
    CURSORS = (
        ((0, 0), (3, 0)),
        ((3, 0), (6, 0)),
        ((6, 0), (9, 0)),
        ((11, 1), (13, 1)),
        ((13, 1), (15, 1)),
    )
    MIN_MAX_VALUES = (
        (0, 23),
        (0, 59),
        (0, 59),
    )

    ALT_ICONS = True

    ID_OK = 3
    ID_CANCEL = 4

    def __init__(self) -> None:
        super().__init__()

        now = time.localtime()
        self.data = [now.tm_hour, now.tm_min, now.tm_sec]

    def render(self) -> None:
        ca, cb = self.get_cursor()

        display.clear()
        display.write((1, 0), format_time(self.data[0], self.data[1], self.data[2]))
        display.write((12, 1), b"\x02 \x03")
        display.write(ca, b"\x06")
        display.write(cb, b"\x07")
        display.flush()

    async def loop_navi_enter(self, duration: float) -> None:
        if self.pos == self.ID_OK:
            self.save()
            raise MenuExit()
        if self.pos == self.ID_CANCEL:
            raise MenuExit()

        await super().loop_navi_enter(duration)

    def save(self) -> None:
        h, m, s = self.data
        rtc.datetime = time.struct_time((2000, 1, 1, h, m, s, 0, 0, -1))
        logger.log(const.RTC_SAVE)
        scheduler.restart()


class HistoryMenu(Menu):
    MAX_VALUE = 98

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.MAX_VALUE

    def get_min_max_cursors(self) -> tuple[int, int]:
        return 0, self.MAX_VALUE

    def render(self) -> None:
        entry = logger.get(self.MAX_VALUE - self.pos)

        display.clear()
        display.write((8, 1), format_time(entry.hour, entry.minute, entry.second))
        display.write((0, 0), _(entry.id)[:16].encode())

        lo, hi = self.get_min_max_cursors()
        display.write((0, 1), b"\x7F" if self.pos > lo else b" ")
        display.write((1, 1), f"{self.pos + 1:02}".encode())
        display.write((3, 1), b"\x7E" if self.pos < hi else b" ")

        display.flush()

    async def loop_navi_enter(self, duration: float) -> None:
        raise MenuExit()


async def loop() -> None:
    menu = IdleMenu()
    menu.enter()

    while True:
        await menu.loop()
