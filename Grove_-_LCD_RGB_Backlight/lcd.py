#!/usr/bin/env python

import logging

import time

import I2C


# usage:
# ./lcd.py <color> <text>

# I2C addresses
LCD_ADDR_BACKLIGHT       = 0x62
LCD_ADDR_CHARACTER       = 0x3e

# backlight registers
LCD_REG_BACKLIGHT_MODE1  = 0x00
LCD_REG_BACKLIGHT_MODE2  = 0x01

LCD_REG_BACKLIGHT_PWM0   = 0x02
LCD_REG_BACKLIGHT_PWM1   = 0x03
LCD_REG_BACKLIGHT_PWM2   = 0x04
LCD_REG_BACKLIGHT_LEDOUT = 0x08

# character registers
LCD_REG_CHAR_DISPLAY     = 0x80
LCD_REG_CHAR_LETTERS     = 0x40



class lcd(object):
    def __init__(self,
                 backlight = LCD_ADDR_BACKLIGHT   ,
                 character = LCD_ADDR_CHARACTER   ,
                 busnum    = I2C.get_default_bus()
        ):

        self._logger    = logging.getLogger('LCD')

        # Create I2C device.
        self._backlight = I2C.Device( backlight, busnum )
        self._character = I2C.Device( character, busnum )

        #reset device
        #self._reset()

        # Load calibration values.
        #self._load_calibration()

        self.on()
        self.clear()

    def set_led_output_state(self):
        self._backlight.write8(self.LCD_REG_BACKLIGHT_LEDOUT, 0xAA)
        #i2cset -y 1 self._backlight self.LCD_REG_BACKLIGHT_LEDOUT 0xAA   # led output state

    def set_color(self,red,green,blue):
        self._backlight.write8(self.LCD_REG_BACKLIGHT_MODE1 , 0xAA )
        self._backlight.write8(self.LCD_REG_BACKLIGHT_MODE2 , 0xAA )
        self._backlight.write8(self.LCD_REG_BACKLIGHT_PWM0  , blue )
        self._backlight.write8(self.LCD_REG_BACKLIGHT_PWM1  , green)
        self._backlight.write8(self.LCD_REG_BACKLIGHT_PWM2  , red  )

        #i2cset -y 1 self._backlight self.LCD_REG_BACKLIGHT_MODE1  0x00   # mode 1 init, normal mode
        #i2cset -y 1 self._backlight self.LCD_REG_BACKLIGHT_MODE2  0x00   # mode 2 init
        #i2cset -y 1 self._backlight self.LCD_REG_BACKLIGHT_PWM0   blue   # blue
        #i2cset -y 1 self._backlight self.LCD_REG_BACKLIGHT_PWM1   green  # green
        #i2cset -y 1 self._backlight self.LCD_REG_BACKLIGHT_PWM2   red    # red

        self.set_led_output_state()

    def clear(self):
        self._character.write8(self.LCD_REG_CHAR_DISPLAY, 0x01  )
        #i2cset -y 1 self._character self.LCD_REG_CHAR_DISPLAY 0x01  # clear LCD_REG_CHAR_DISPLAY

    def on(self, cursor_type = 'block'):
        if   cursor_type == 'underline':
            self._character.write8(self.LCD_REG_CHAR_DISPLAY, 0x0E  )
            #i2cset -y 1 self._character self.LCD_REG_CHAR_DISPLAY 0x0E  # LCD_REG_CHAR_DISPLAY on, underline cursor

        elif cursor_type == 'block':
            self._character.write8(self.LCD_REG_CHAR_DISPLAY, 0x0F  )
            #i2cset -y 1 self._character self.LCD_REG_CHAR_DISPLAY 0x0F  # LCD_REG_CHAR_DISPLAY on, block cursor

        else:
            print "no suck cursor type:", cursor_type
            sys.exit(1)

    def set_row(self, row):
        if   row == 1:
            self._character.write8(self.LCD_REG_CHAR_DISPLAY, 0x38  )
            #i2cset -y 1 self._character self.LCD_REG_CHAR_DISPLAY 0x38  # 2 lines

        elif row == 2:
            self._character.write8(self.LCD_REG_CHAR_DISPLAY, 0x38  )
            #i2cset -y 1 self._character self.LCD_REG_CHAR_DISPLAY 0x38  # 2 lines

        else:
            print "no such row", row
            sys.exit(1)

    def set_text(self, text):
        for c in text:
            self._character.write8(self.LCD_REG_CHAR_LETTERS, ord(c)  )
            #i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS ord(c)

    def set_text_1(self, text):
        """
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 72    # H
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 101   # e
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 108   # l
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 108   # l
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 111   # o
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 32    # space
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 87    # W
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 111   # o
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 114   # r
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 108   # l
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 100   # d
        """
        pass

    def set_text_2(self, text):
        """
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 80    # P
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 111   # o
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 116   # t
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 97    # a
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 116   # t
        i2cset -y 1 self._character self.LCD_REG_CHAR_LETTERS 111   # o
        """
        pass

    def set_one_line(self):
        self._character.write8(self.LCD_REG_CHAR_DISPLAY, 0xc0 )
        #i2cset -y 1 self._character self.LCD_REG_CHAR_DISPLAY 0xc0  # move cursor to row 2, col 0

    def set_two_lines(self):
        self._character.write8(self.LCD_REG_CHAR_DISPLAY, 0x38 )
        #i2cset -y 1 self._character self.LCD_REG_CHAR_DISPLAY 0x38  # 2 lines



if __name__ == "__main__":
    print "initing"
    disp = lcd()
    disp.on()
    disp.clear()
    disp.set_two_lines()

    print "hello world"
    disp.set_row(1)
    disp.set_text("hello world")
    time.sleep(1)

    print "potato"
    disp.set_row(2)
    disp.set_text("potato")
    time.sleep(1)

    print "red"
    disp.set_color(255,  0,  0) # red
    time.sleep(1)

    print "green"
    disp.set_color(  0,255,  0) # green
    time.sleep(1)

    print "blue"
    disp.set_color(  0,  0,255) # blue
    time.sleep(1)

    print "cyan"
    disp.set_color(  0,255,255) # cyan
    time.sleep(1)

    print "yellow"
    disp.set_color(255,255,  0) # yellow
    time.sleep(1)

    print "pink"
    disp.set_color(255,  0,255) # pink

    print "sleeping"
    time.sleep(10)

    print "bye"

