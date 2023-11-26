from app.menu import IdleMenu


def main() -> None:
    menu = IdleMenu()
    menu.enter()

    while True:
        menu.loop()
