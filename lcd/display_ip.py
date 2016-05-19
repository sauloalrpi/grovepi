#!/usr/bin/env python

import socket

from grove_rgb_lcd import *

if __name__ == "__main__":
    ip = "not connected"

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com",80))
        ip = str(s.getsockname()[0])
        s.close()
    except:
        pass

    #r,g,b = 0, 255, 0
    r,g,b = [int(x) for x in ip.split('.')[-3:]]

    setRGB(r,g,b)

    setText("IP:" + ip)

#ip = socket.gethostbyname(socket.getfqdn())
#print ip

