## About this document

This document can be converted to .DOCX format if `pandoc` is installed:

```bash
pandoc -f markdown -t docx README.md > README.docx
```

The output DOCX file has embedded images. It can be printed or uploaded to any online translation service.

## Installation instructions

- Install CircuitPython on the Raspberry Pi Pico. The supported version is defined in the `upload.sh` file.
- Set up a development environment using the provided Poetry configuration.
- Download `mpy-cross` binary for the supported CircuitPython
  version, [detailed instructions can be found here](https://learn.adafruit.com/welcome-to-circuitpython/frequently-asked-questions).
- Run `upload.sh --full` to install dependencies, build .mpy files, and upload the code.

## Pinout

(left to right)

|   | Buttons      | |   | Motor                         | |    | Power        |
|---|--------------|-|---|-------------------------------|-|----|--------------|
| 1 | Ground (GND) | | 5 | Motor A (programmable on/off) | | 9  | +3V3         |
| 2 | Button ⬅️    | | 6 | Motor B (programmable on/off) | | 9  | +3V3         |
| 3 | Button ➡️    | | 7 | Motor A (programmable PWM)    | | 10 | Ground (GND) |
| 4 | Button ☑️    | | 8 | Motor B (programmable PWM)    | | 11 | +5V          |
|   |              | |   |                               | | 11 | +5V          |

## User menu

There are three buttons on the button board:

|                                                              | ⬅️                                                              | ➡️                                                              | ☑️                                                                                    |
|--------------------------------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------|---------------------------------------------------------------------------------------|
| **On the idle screen**                                       | Press and hold for a few seconds to enter the menu.             |                                                                 |                                                                                       |
| ![](assets/cursor1.png) <br/> **In the menu (cursor mode)**  | Tap to move the cursor left.                                    | Tap to move the cursor right.                                   | Tap to select a highlighted option. This will invoke an action or enter editing mode. |
| ![](assets/cursor2.png) <br/> **In the menu (editing mode)** | Tap to decrease the value by 1. Press and hold to do it faster. | Tap to increase the value by 1. Press and hold to do it faster. | Tap to confirm the value you have entered and return to cursor mode.                  |

### Changing user menu language

1. Connect the device to the PC
2. Open `settings.toml` file
3. Add or change a single `LANG=...` line to change the language of user menu

Available languages:

- English (`LANG="en"`, default)
- Polish (`LANG="pl"`)

### Idle screen

![](assets/canvas1.png)

This is the idle screen. The following information is displayed:

| Icon                   | Information                                           |
|------------------------|-------------------------------------------------------|
|                        | Current time                                          |
| ![](assets/error1.png) | Automatic reset after failure is disabled (no jumper) |
| ![](assets/error2.png) | System time is invalid (missing or bad battery)       |

### Main menu

![](assets/canvas2.png)

This is the main menu. The following options are available:

- Open immediately
- Close immediately
- Set up opening
- Set up closing
- Set up clock
- Show history
- Return to the idle screen

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

Use ⬅️ or ➡️ to see other entries, and ☑️ to return to the motor menu.

### System menu

This is the system menu, and it is similar to the motor menu. It can be used to change the current time.

Changes **will not** be saved if the new time value is the same as the previous one, even if some time has passed since
this menu has been entered.

Changes **will** be saved, and seconds will be reset to 0 if values are different or if the previous time was invalid.

### History menu

![](assets/canvas5.png)

This is the history menu. Recent log entries are displayed, such as device status, errors and automated operations.

Use ⬅️ or ➡️ to see other entries, and ☑️ to return to the main menu.

## Known issues

- Sometimes buttons ⬅️ or ➡️ get stuck. Press one of these buttons again to resolve this issue.
