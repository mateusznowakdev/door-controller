import asyncio


async def main() -> None:
    from app.menu import menu_loop  # pylint:disable=import-outside-toplevel

    await asyncio.gather(menu_loop())
