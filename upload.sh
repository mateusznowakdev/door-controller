#!/usr/bin/env bash

set -e

CPY_HOME=/media/$USER/CIRCUITPY
CPY_VERSION="CircuitPython 8.2.8"

if [ ! -f mpy-cross ]
then
  echo "mpy-cross binary must be present in the root directory"
  exit 1
fi

if ! ./mpy-cross --version | grep "$CPY_VERSION"
then
  echo "mpy-cross binary is not compatible with $CPY_VERSION"
  exit 1
fi

if ! grep "$CPY_VERSION" "$CPY_HOME/boot_out.txt"
then
  echo "$CPY_VERSION must be installed"
  exit 1
fi

find app -name '*.py' -exec ./mpy-cross {} \;

mkdir -p "$CPY_HOME/app"

if [[ $1 == "--full" ]]
then
  circup install -r requirements.txt
  cp -v app/*.mpy "$CPY_HOME/app"
  cp -v boot.py code.py safemode.py "$CPY_HOME"
else
  cp -uv app/*.mpy "$CPY_HOME/app"
  cp -uv boot.py code.py safemode.py "$CPY_HOME"
fi
