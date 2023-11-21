#!/usr/bin/env bash

CPY_HOME=/media/$USER/CIRCUITPY
CPY_VERSION="CircuitPython 8.2.8"

if ! grep "$CPY_VERSION" "$CPY_HOME/boot_out.txt" >/dev/null
then
  echo "$CPY_VERSION must be installed"
  exit 1
fi

cp code.py "$CPY_HOME/code.py"
