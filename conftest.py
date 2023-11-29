"""
This configuration file is used to mock CircuitPython modules
in CPython environment
"""

import sys

app_menu = type(sys)("app.menu")
app_menu.IdleMenu = None

app_hardware = type(sys)("app.hardware")
app_hardware.Motor = None
app_hardware.rtc = None

sys.modules["app.hardware"] = app_hardware
sys.modules["app.menu"] = app_menu
