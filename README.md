## Setting up

- Install CircuitPython on the Raspberry Pi Pico
- Set up a development environment using Poetry
- Download `mpy-cross` binary for CircuitPython
- Run `upload.sh --full` to install dependencies, build and upload the code

## Usage

There are three buttons on the button board:

|                                | ⬅️                                                              | ➡️                                                              | ☑️                                                                                    |
|--------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------|---------------------------------------------------------------------------------------|
| **On the idle screen**         | Press and hold for a few seconds to enter the menu.             |                                                                 |                                                                                       |
| **In the menu (cursor mode)**  | Tap to move the cursor left.                                    | Tap to move the cursor right.                                   | Tap to select a highlighted option. This will invoke an action or enter editing mode. |
| **In the menu (editing mode)** | Tap to decrease the value by 1. Press and hold to do it faster. | Tap to increase the value by 1. Press and hold to do it faster. | Tap to confirm the value you have entered and return to cursor mode.                  |

## Troubleshooting

| Problem                           | Solution                                                                   |
|-----------------------------------|----------------------------------------------------------------------------|
| Buttons are not working properly. | (1) Tap ⬅️ or ➡️.                                                          |
|                                   | (2) Make sure the pins are not shorted.                                    |
|                                   | (3) Disconnect the button board and bridge pins 1-2, 1-3 and 1-4 manually. |
