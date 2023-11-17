import board
from digitalio import DigitalInOut

from adafruit_character_lcd.character_lcd import Character_LCD_Mono

lcd_rs = DigitalInOut(board.GP9)
lcd_en = DigitalInOut(board.GP8)
lcd_d4 = DigitalInOut(board.GP7)
lcd_d5 = DigitalInOut(board.GP6)
lcd_d6 = DigitalInOut(board.GP5)
lcd_d7 = DigitalInOut(board.GP4)

display = Character_LCD_Mono(rs=lcd_rs, en=lcd_en, db4=lcd_d4, db5=lcd_d5, db6=lcd_d6, db7=lcd_d7, columns=16, lines=2)
display.message = "Test"
