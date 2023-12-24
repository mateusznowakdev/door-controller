#!/usr/bin/env bash

set -e

CPY_HOME=/media/$USER/CIRCUITPY
CPY_VERSION="CircuitPython 8.2.9"

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

find app -maxdepth 1 -name '*.py' -exec ./mpy-cross {} \;

mkdir -p "$CPY_HOME/app"

if [[ $1 == "--full" ]]
then
  circup install -r requirements.txt
fi

rsync -cv app/*.mpy "$CPY_HOME/app"
rsync -cv boot.py main.py safemode.py "$CPY_HOME"
sync

rm -r app/*.mpy
