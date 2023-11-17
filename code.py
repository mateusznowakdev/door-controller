import board
from digitalio import DigitalInOut
from pwmio import PWMOut

from adafruit_character_lcd.character_lcd import Character_LCD_Mono

lcd_rs = DigitalInOut(board.GP9)
lcd_en = DigitalInOut(board.GP8)
lcd_d4 = DigitalInOut(board.GP7)
lcd_d5 = DigitalInOut(board.GP6)
lcd_d6 = DigitalInOut(board.GP5)
lcd_d7 = DigitalInOut(board.GP4)
lcd_bl = PWMOut(board.GP3)

display = Character_LCD_Mono(rs=lcd_rs, en=lcd_en, db4=lcd_d4, db5=lcd_d5, db6=lcd_d6, db7=lcd_d7, columns=16, lines=2)
display.create_char(0, [0b00000, 0b11000, 0b10110, 0b10001, 0b10110, 0b11000, 0b00000, 0b00000])
display.create_char(1, [0b00000, 0b00011, 0b01101, 0b10001, 0b01101, 0b00011, 0b00000, 0b00000])
display.create_char(2, [0b00000, 0b00100, 0b01110, 0b10101, 0b00100, 0b00100, 0b00000, 0b00000])
display.create_char(3, [0b00000, 0b00100, 0b00100, 0b10101, 0b01110, 0b00100, 0b00000, 0b00000])
display.create_char(4, [0b00000, 0b01110, 0b10101, 0b10111, 0b10001, 0b01110, 0b00000, 0b00000])
display.create_char(5, [0b00000, 0b01000, 0b11110, 0b01001, 0b00001, 0b00110, 0b00000, 0b00000])
display.create_char(6, [0b00101, 0b00000, 0b00100, 0b00000, 0b00100, 0b00000, 0b00101, 0b00000])
display.create_char(7, [0b10100, 0b00000, 0b00100, 0b00000, 0b00100, 0b00000, 0b10100, 0b00000])


def set_backlight(percentage: int) -> None:
    lcd_bl.duty_cycle = percentage * 65535 // 100


if __name__ == "__main__":
    display.message = f"\x06\x00\x07\x01 \x02 \x03 \x04 \xD0 \x05\n Open"
    set_backlight(25)

    while True:
        pass
