import asyncio


async def main() -> None:
    from app.core import SchedulerService  # pylint:disable=import-outside-toplevel
    from app.menu import menu_loop  # pylint:disable=import-outside-toplevel

    await asyncio.gather(menu_loop(), SchedulerService.get_tasks())
