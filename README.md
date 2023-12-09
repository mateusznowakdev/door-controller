## Installation instructions

- Install CircuitPython on the Raspberry Pi Pico. The supported version is defined in the `upload.sh` file.
- Set up a development environment using the provided Poetry configuration.
- Download `mpy-cross` binary for the supported CircuitPython
  version, [detailed instructions can be found here](https://learn.adafruit.com/welcome-to-circuitpython/frequently-asked-questions).
- Run `upload.sh --full` to install dependencies, build .mpy files, and upload the code.

### Language

Connect the device to the PC and open `settings.toml` file. Add a single `LANG=...` line to change the language of user
menu.

Available languages:

- English (`LANG="en"`)
- Polish (`LANG="pl"`)

## Pinout

(left to right)

|   | Buttons      | |   | Motor                         | |    | Power        | |    | Watchdog |
|---|--------------|-|---|-------------------------------|-|----|--------------|-|----|----------|
| 1 | Ground (GND) | | 5 | Motor A (programmable on/off) | | 9  | +3V3         | | 12 | +3V3     |
| 2 | Button ⬅️    | | 6 | Motor B (programmable on/off) | | 9  | +3V3         | | 13 | Signal   |
| 3 | Button ➡️    | | 7 | Motor A (programmable PWM)    | | 10 | Ground (GND) | |    |          |
| 4 | Button ☑️    | | 8 | Motor B (programmable PWM)    | | 11 | +5V          | |    |          |
|   |              | |   |                               | | 11 | +5V          | |    |          |

## User menu

There are three buttons on the button board:

|                                                              | ⬅️                                                              | ➡️                                                              | ☑️                                                                                    |
|--------------------------------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------|---------------------------------------------------------------------------------------|
| **On the idle screen**                                       | Press and hold for a few seconds to enter the menu.             |                                                                 |                                                                                       |
| ![](assets/cursor1.png) <br/> **In the menu (cursor mode)**  | Tap to move the cursor left.                                    | Tap to move the cursor right.                                   | Tap to select a highlighted option. This will invoke an action or enter editing mode. |
| ![](assets/cursor2.png) <br/> **In the menu (editing mode)** | Tap to decrease the value by 1. Press and hold to do it faster. | Tap to increase the value by 1. Press and hold to do it faster. | Tap to confirm the value you have entered and return to cursor mode.                  |

### Idle screen

![](assets/canvas1.png)

This is the idle screen. The error message is shown only if the system time is not set. Check the battery and set the
current time again.

### Main menu

![](assets/canvas2.png)

This is the main menu screen. The following options are available:

- **Open** immediately
- **Close** immediately
- **Set up opening** options
- **Set up closing** options
- **Set system time**
- **Return** to the idle screen

### Motor menu

![](assets/canvas3.png)

This is the motor menu for either the opening or closing operation. The following options are available:

- Time of the first operation in a series
- Time of the last operation in a series (does not apply if the divider is set to 1)
- Total time reserved for all operations
- Total number of operations in a series (a _divider_)
- Preview changes
- Save and return to the main menu screen

This example configuration will turn on the motor for approximately 25 seconds at 08:00, 11:00, 14:00, and 17:00 every
day.

It might be necessary to fine-tune these values according to the weather conditions and motor parameters.

To disable any opening or closing operation, set the total time to 0.

### Preview menu

![](assets/canvas4.png)

This is the list of opening and closing operations to be scheduled.

Use ⬅️ or ➡️ to see other entries, and ☑️ to return to the motor settings menu.

### System menu

![](assets/canvas5.png)

This is the system menu. It can be used to change the current time.

Changes **will not** be saved if the new time value is the same as the previous one, even if some time has passed since
this menu has been entered. Changes **will** be saved, and seconds will be reset to 0 if values are different or if the
previous time was invalid.

## Troubleshooting

| Problem                           | Solution                                                                   |
|-----------------------------------|----------------------------------------------------------------------------|
| Buttons are not working properly. | (1) Tap ⬅️ or ➡️ to make sure buttons are not stuck.                       |
|                                   | (2) Make sure the pins are not shorted.                                    |
|                                   | (3) Disconnect the button board and bridge pins 1-2, 1-3 and 1-4 manually. |
