"""
This configuration file is used to mock CircuitPython modules
in CPython environment
"""

import sys

app_hardware = type(sys)("app.hardware")
app_hardware.Motor = None
app_hardware.eeprom = None
app_hardware.rtc = None

sys.modules["app.hardware"] = app_hardware
