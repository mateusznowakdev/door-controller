import asyncio


async def main() -> None:
    from app import menu, scheduler  # pylint:disable=import-outside-toplevel

    await asyncio.gather(menu.loop(), scheduler.loop())
