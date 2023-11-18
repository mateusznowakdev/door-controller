## Setting up

- Install CircuitPython on Raspberry Pi Pico
- Install `circup`
- Use `circup install -r requirements.txt` to install dependencies
- Use `bash upload.sh` to upload the code

## Known issues

| Issue                                   | Explanation / Solution                                                                                                         |
|-----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| System time is not displayed correctly. | This is an expected behavior, introduced to prioritize more important tasks. Internal system time should be working correctly. |
| There are bad pixels visible.           | The LCD module can display up to 8 icons. Some similar built-in characters are used to work around this limitation.            |
| Buttons are not working correctly.      | (1) Make sure the pins are not shorted. (2) Disconnect the button board and use thin wire to short pins 1-2, 1-3 and 1-4.      |
