#!/usr/bin/env python

# Simple demo of reading each analog input from the ADS1x15 and printing it to
# the screen.
# Author: Tony DiCola
# License: Public Domain
import time
from   collections import defaultdict

# Import the ADS1x15 module.
import Adafruit_ADS1x15


class adcs(object):
    def __init__(self):
        self.adcs      = {}

    def get(self, address):
        # Create an ADS1115 ADC (16-bit) instance.

        if address not in self.adcs:
            print "adding address", address
            self.adcs[ address ] = Adafruit_ADS1x15.ADS1115( address )
        
        return self.adcs[ address ]
        

class sensor(object):
    """
    Or create an ADS1015 ADC (12-bit) instance.
    adc = Adafruit_ADS1x15.ADS1015()

    Note you can change the I2C address from its default (0x48), and/or the I2C
    bus by passing in these optional parameters:
    
    adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)

    Choose a gain of 1 for reading voltages from 0 to 4.09V.
    Or pick a different gain to change the range of voltages that are read:
    - 2/3 = +/-6.144V
    -   1 = +/-4.096V
    -   2 = +/-2.048V
    -   4 = +/-1.024V
    -   8 = +/-0.512V
    -  16 = +/-0.256V
    See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
    """

    adcs    = adcs()

    def __init__(self, name, address, port, gain):
        self.name    = name
        self.address = address
        self.port    = port
        self.gain    = gain

    def read(self):
        adc = self.adcs.get(self.address)
        val = adc.read_adc(self.port, gain=self.gain)
        return val
        
    def printer(self):
        print str(self)

    def __repr__(self):
        return "<SENSOR :: {} : address: {} port: {} gain: {}>".format(self.name, hex(self.address), self.port, self.gain)
        

class controller(object):
    def __init__(self):
        self.sensors = defaultdict(lambda: defaultdict(dict))

    def add_sensor(self, name, address, port, gain):
        self.sensors[address][port][name] = sensor(name, address, port, gain)

    def __repr__(self):
        line = "CONTROLLER START\n"

        for address, ports in sorted(self.sensors.items()):
            for port, names in sorted(ports.items()):
                for name, sensor in sorted(names.items()):
                    line += " address {} port {} name {} sensor {} val {}\n".format(hex(address), port, name, sensor, sensor.read())

        line += "CONTROLLER END\n"

        return line

    def printer(self):
        print str(self)

"""
# Print nice channel column headers.

header_1_address = ('{:'+str(7*len(ports)-1)+'s}|')*len(addresses)
header_2_ports   = '{:>6}|' * len(ports)
values_str       = header_2_ports * len(addresses)

#print 'header_1_address', header_1_address
#print 'header_2_ports  ', header_2_ports
#print 'values_str      ', values_str

header_1 = '|' + ( header_1_address.format( *[hex(x) for x in addresses] )                  )
header_2 = '|' + ( header_2_ports  .format( *ports                       ) * len(addresses) )
header_3 = '-' * ( len(addresses) * len(ports) * 7 + 1                                      )

print( header_1 )
print( header_2 )
print( header_3 )
"""

"""
    values  = [ '' for n in xrange((len(ports)*len(addresses))) ]

    for an, add in enumerate(adcs):
        #print 'address', an, add[0]

        # Read all the ADC channel values in a list.
        ap, adc = add

        for pn, p in enumerate(ports):
            key = ( an * len(ports) )+pn

            #print ' port', pn, ' ', p, 'key', key

            # Read the specified ADC channel using the previously set gain value.
            try:
                v             = adc.read_adc(p, gain=GAIN)
                values[ key ] = v

            except IOError:
                break

            # Note you can also pass in an optional data_rate parameter that controls
            # the ADC conversion time (in samples/second). Each chip has a different
            # set of allowed data rate values, see datasheet Table 9 config register
            # DR bit values.
            #values[i] = adc.read_adc(i, gain=GAIN, data_rate=128)
            # Each value will be a 12 or 16 bit signed integer value depending on the
            # ADC (ADS1015 = 12-bit, ADS1115 = 16-bit).

    # Print the ADC values.
    print('|' + values_str.format(*values) )

"""

def main(config):
    print('Reading ADS1x15 values, press Ctrl-C to quit...')

    ctrl = controller()

    for address, ports in sorted(config.items()):
        for port, cfg in sorted(ports.items()):
            name = cfg["name"]
            gain = cfg["gain"]
            ctrl.add_sensor( name, address, port, gain )

    # Main loop.
    while True:
        ctrl.printer()
        # Pause for half a second.
        time.sleep(0.5)



config = {
    0x48: {
        0: {
            "name": "Luminosity",
            "gain": 1
        }
    }
}



if __name__ == "__main__":
    main(config)
