Project description can be found on
[my website](https://mateusznowak.dev/projects/automatic-door-controller/).

User manual can be found in [docs](./docs/README.md) directory.

## Installing

(instructions for Linux)

1. Make sure recent version of Python and Git are installed.
2. Clone the repository.
3. Download and flash CircuitPython 9.0.3 using the official instructions.
    - [Download](https://adafruit-circuit-python.s3.amazonaws.com/bin/raspberry_pi_pico/en_US/adafruit-circuitpython-raspberry_pi_pico-en_US-9.0.3.uf2)
4. Download mpy-cross binary to the `firmware` directory, rename it and make it
   executable.
    - [Download (amd64)](https://adafruit-circuit-python.s3.amazonaws.com/bin/mpy-cross/linux-amd64/mpy-cross-linux-amd64-9.0.3.static)
5. Install circup:
    - `pip install -U pip setuptools`
    - `pip install circup`
6. Build and upload the code to the CIRCUITPY drive
    - `cd firmware`
    - `./upload.sh --full`

## Language options

Can be changed by creating `settings.toml` file on the CIRCUITPY drive, with the
following content:

```toml
LANG = "pl"
```

Supported languages: `en`, `pl`
