# Raspberry Pi Pico-based motor controller<br/>User manual

## 1. Overview

<img src="overview.svg" width="400" />

1. HD44780 LCD module
2. Contrast potentiometer
3. DS3231 Real Time Clock (RTC) + AT24LC32 EEPROM module
4. Raspberry Pi Pico microcontroller module
5. Button module - Left button
6. Button module - Right button
7. Button module - OK button
8. Programmable motor output signal
9. Power input / output, in the following order: 3V3, GND, 5V
10. Auto-reset jumper

### 1.1. Safe default settings

The RTC / EEPROM module is used to keep track of the current time and store user settings.

Automatic opening and closing will be temporarily disabled if the time setting is invalid. Open time settings and set the current time again. Replace the battery if the problem is not resolved.

If EEPROM contents cannot be read due to the bad checksum, the default settings will be used:

- run from 00:00 to 00:00 for 0 seconds divided by 1

### 1.2. Auto-reset feature

This device is automatically reset after failure, such as lost communication with the real time clock module. LCD and button modules are not monitored.

This feature can be disabled if access to the USB serial console is required. Remove the jumper (10.) only if requested by qualified personnel.

## 2. User menu

### 2.1. Using the button module

The three buttons of the button module are used in the user menu, and produce different results in one of two modes:

|                                                           | Left                                                              | Right                                                             | OK                                                                                                            |
|-----------------------------------------------------------|-------------------------------------------------------------------|-------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| ![](cursor-navi.png) <br/> **In the menu (cursor mode)**  | Press to move the cursor left.                                    | Press to move the cursor right.                                   | Press to select a highlighted option. This will invoke an action, enter a sub-menu or switch to editing mode. |
| ![](cursor-edit.png) <br/> **In the menu (editing mode)** | Press to decrease the value by 1. Press and hold to do it faster. | Press to increase the value by 1. Press and hold to do it faster. | Press to confirm the value you have entered and return to cursor mode.                                        |

The button module may stop working temporarily in the following conditions:

- Ongoing opening or closing operation
- Hardware failure

### 2.2. Idle screen

![](menu-idle.png)

The following information is displayed on the idle screen:

| Icon                          | Description                 |
|-------------------------------|-----------------------------|
| &nbsp;                        | Current time                |
| ![](menu-icon-set-system.png) | Automatic reset is disabled |
| ![](menu-icon-time.png)       | System time is invalid      |

Press and hold the **Left** button for a few seconds to enter the main menu.

### 2.3. Main menu

![](menu-main.png)

The following menu options are available:

| Icon                          | Description                                            |
|-------------------------------|--------------------------------------------------------|
| ![](menu-icon-time.png)       | Show scheduled operations                              |
| ![](menu-icon-open.png)       | Open now (single operation according to the schedule)  |
| ![](menu-icon-close.png)      | Close now (single operation according to the schedule) |
| ![](menu-icon-set-open.png)   | Change opening parameters                              |
| ![](menu-icon-set-close.png)  | Change closing parameters                              |
| ![](menu-icon-set-system.png) | Change system time                                     |
| ![](menu-icon-list.png)       | Show operation history                                 |
| ![](menu-icon-left.png)       | Return to the idle screen                              |

"Open" and "Close" operations requested from the main menu are run synchronously at the best precision possible, which means these cannot be stopped prematurely.

### 2.4. "Preview" menu

![](menu-preview.png)

This menu is used to list all scheduled operations and their directions. Press the **Left** or **Right** button to switch to the previous or next page, respectively, or the **OK** button to return to the main menu.

If no operations are scheduled or if the system time is invalid, the following empty screen is shown:

![](menu-preview-empty.png)

### 2.5. "History" menu

![](menu-history.png)

This menu is similar to the preview menu but is used to list important events in the past, such as:

- device status
- opening and closing operations
- changed settings

Some log entries have an extra context:

| Icon                 | Description     |
|----------------------|-----------------|
| ![](menu-icon-1.png) | Single (manual) |
| ![](menu-icon-a.png) | Automatic       |
| ![](menu-icon-m.png) | Measurement     |

### 2.6. "Set opening" and "Set closing" menus

![](menu-set-open.png)

These menus are used to change the parameters of the scheduled opening and closing operations. The following parameters can be set:

- Time of the first operation in the series
- Time of the last operation in the series
- Total duration for all operations in series during a day
- Number of operations during a day

The following actions are also available:

| Icon                      | Description                                                |
|---------------------------|------------------------------------------------------------|
| ![](menu-icon-time.png)   | Start automatic measurement. See "2.6.1. Measurement menu" |
| ![](menu-icon-ok.png)     | Save the updated settings, then return to the main menu    |
| ![](menu-icon-cancel.png) | Ignore the updated settings, then return to the main menu  |

**Example**: This example configuration will turn on the motor for approximately 10 seconds at 08:00, 09:00, ..., 15:00, and 16:00 every
day.

It might be necessary to fine-tune these values according to the weather conditions and motor parameters.

To disable opening or closing operations, set the total duration to 0s.

#### 2.6.1. Measurement menu

![](menu-measure.png)

This sub-menu is used to run an opening or closing operation for an unspecified amount of time, usually for measurement purposes.

The opening or closing operation is run asynchronously, which means it can be stopped by pressing the **OK** button at the cost of worse precision. The displayed value is then set as a total duration in the "Set opening" or "Set closing" menu.

### 2.7. "Set clock" menu

![](menu-set-time.png)

This menu is used to change the system time to the specified value.