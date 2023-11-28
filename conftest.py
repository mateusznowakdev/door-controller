"""
This configuration file is used to mock CircuitPython modules
in CPython environment
"""

import sys

board = type(sys)("board")

app_hardware = type(sys)("app.hardware")
app_hardware.Display = None
app_hardware.Keys = None
app_hardware.display = None
app_hardware.keys = None
app_hardware.motor = None
app_hardware.rtc = None

sys.modules["board"] = board
sys.modules["app.hardware"] = app_hardware
