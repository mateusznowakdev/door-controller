Project description can be found on
[my website](https://mateusznowak.dev/projects/automatic-door-controller/).

User manual can be found in [docs](./docs/README.md) directory.

## Installing

(instructions for Linux)

1. Clone the repository.
    - `git clone --recurse-submodules https://github.com/mateusznowakdev/door-controller`
2. Download and flash CircuitPython 9.1.3 using the official instructions.
    - [Download](https://adafruit-circuit-python.s3.amazonaws.com/bin/raspberry_pi_pico/en_US/adafruit-circuitpython-raspberry_pi_pico-en_US-9.1.3.uf2)
3. Download mpy-cross binary to the `firmware` directory, rename it and make it
   executable.
    - [Download (amd64)](https://adafruit-circuit-python.s3.amazonaws.com/bin/mpy-cross/linux-amd64/mpy-cross-linux-amd64-9.1.3.static)
4. Build and upload the code to the CIRCUITPY drive
    - `cd firmware`
    - `./upload.sh`

## Language options

Can be changed by creating `settings.toml` file on the CIRCUITPY drive, with the
following content:

```toml
LANG = "pl"
```

Supported languages: `en`, `pl`
