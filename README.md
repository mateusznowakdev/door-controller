<details>
<summary>Build and install</summary>

- Install CircuitPython on the Raspberry Pi Pico
- Set up a development environment using Poetry
- Download `mpy-cross` binary for CircuitPython
- Run `upload.sh --full` to install dependencies, build and upload the code

</details>

## Usage

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
- Divider (total number of operations in a series)
- Preview changes
- Save and return to the main menu screen

This example configuration will turn on the motor for 25 seconds at 08:00, 11:00, 14:00, and 17:00 every day.

It might be necessary to change these values according to the weather conditions and motor parameters.

To disable the operation, set the total time to 0.

### Preview menu

![](assets/canvas4.png)

This is the list of opening and closing operations to be scheduled.

Use ⬅️ or ➡️ to turn pages, and ☑️ to return to the motor settings menu.

### System menu

![](assets/canvas5.png)

This is the system menu. It can be used to change the current time.

## Troubleshooting

| Problem                           | Solution                                                                   |
|-----------------------------------|----------------------------------------------------------------------------|
| Buttons are not working properly. | (1) Tap ⬅️ or ➡️ to make sure buttons are not stuck.                       |
|                                   | (2) Make sure the pins are not shorted.                                    |
|                                   | (3) Disconnect the button board and bridge pins 1-2, 1-3 and 1-4 manually. |
