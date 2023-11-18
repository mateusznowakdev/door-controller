#!/usr/bin/env bash

black . && isort . && pylint code.py
