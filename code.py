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


def set_backlight(percentage: int) -> None:
    lcd_bl.duty_cycle = percentage * 65535 // 100


if __name__ == "__main__":
    display.message = "Test"
    set_backlight(25)

    while True:
        pass
