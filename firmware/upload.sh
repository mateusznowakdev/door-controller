#!/usr/bin/env bash

set -e

CPY_HOME=/media/$USER/CIRCUITPY
CPY_VERSION="CircuitPython 9.0.3"

LIB_FILES=(
  lib/Adafruit_CircuitPython_24LC32/adafruit_24lc32.mpy
  lib/Adafruit_CircuitPython_asyncio/asyncio
  lib/Adafruit_CircuitPython_CharLCD/adafruit_character_lcd
  lib/Adafruit_CircuitPython_DS3231/adafruit_ds3231.mpy
  lib/Adafruit_CircuitPython_Register/adafruit_register
  lib/Adafruit_CircuitPython_Ticks/adafruit_ticks.mpy
)

if [ ! -f mpy-cross ]
then
  echo "mpy-cross binary must be present in the root directory. Exiting."
  exit 1
fi

if ! ./mpy-cross --version | grep "$CPY_VERSION"
then
  echo "mpy-cross binary is not compatible with $CPY_VERSION. Exiting."
  exit 1
fi

if ! grep "$CPY_VERSION" "$CPY_HOME/boot_out.txt"
then
  echo "$CPY_VERSION must be installed. Exiting."
  exit 1
fi

find app -name '*.py' -exec ./mpy-cross {} \;
find lib -name '*.py' -exec ./mpy-cross {} \;

mkdir -p "$CPY_HOME/app" "$CPY_HOME/lib"
rsync -crv --include="*/" --include="*.mpy" --exclude="*" app/*.mpy "$CPY_HOME/app/"
rsync -crv --include="*/" --include="*.mpy" --exclude="*" "${LIB_FILES[@]}" "$CPY_HOME/lib/"
rsync -crv boot.py code.py safemode.py "$CPY_HOME/"
sync

rm -r app/*.mpy
