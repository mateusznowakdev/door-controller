import asyncio


async def main() -> None:
    from app import core, menu  # pylint:disable=import-outside-toplevel

    await asyncio.gather(core.loop(), menu.loop())
