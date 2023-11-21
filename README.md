## Setting up

- Install CircuitPython on Raspberry Pi Pico
- Install `circup`
- Use `circup install -r requirements.txt` to install dependencies
- Use `bash upload.sh` to upload the code

## Usage

There are three buttons on the button board:

|    |                           |                                                                                             |
|----|---------------------------|---------------------------------------------------------------------------------------------|
| 1. | <kbd>&nbsp;<-&nbsp;</kbd> | (1) Press and hold to enter the menu.                                                       |
|    |                           | (2) Tap to move the cursor left or decrease the value by 1. Press and hold to do it faster. |
|    |                           |                                                                                             |
| 2. | <kbd>&nbsp;->&nbsp;</kbd> | Tap to move the cursor right or increase the value by 1. Press and hold to do it faster.    |
|    |                           |                                                                                             |
| 3. | <kbd>&nbsp;OK&nbsp;</kbd> | (1) Tap to select a highlighted option.                                                     |
|    |                           | (2) Tap to enter edit mode. Tap again to return to cursor mode.                             |
|    |                           |                                                                                             |

## Troubleshooting

| Problem                            | Solution                                                                          |
|------------------------------------|-----------------------------------------------------------------------------------|
| Buttons are not working correctly. | (1) Make sure the pins are not shorted.                                           |
|                                    | (2) Disconnect the button board and use thin wire to short pins 1-2, 1-3 and 1-4. |
