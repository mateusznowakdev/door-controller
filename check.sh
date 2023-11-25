#!/usr/bin/env bash

black . && isort . && pylint *.py
