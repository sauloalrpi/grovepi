#!/usr/bin/env python

import sys

from grove_rgb_lcd import *

if __name__ == "__main__":
    r,g,b = [int(i) for i in sys.argv[1:4]]
    text  = " ".join(sys.argv[4:])

    setRGB(r,g,b)

    setText(text)
