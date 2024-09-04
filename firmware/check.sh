#!/usr/bin/env bash

FILES="app boot.py code.py safemode.py"
black $FILES && isort $FILES && pylint $FILES && pytest
