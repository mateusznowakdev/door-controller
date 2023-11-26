#!/usr/bin/env bash

black . && isort . && pylint app ./*.py && pytest
