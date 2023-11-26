try:
    from app.menu import IdleMenu
except ImportError:
    # not in CircuitPython environment
    # if errors occur, run ./update.sh --full
    pass


def main() -> None:
    menu = IdleMenu()
    menu.enter()

    while True:
        menu.loop()
