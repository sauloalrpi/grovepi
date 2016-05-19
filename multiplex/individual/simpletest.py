#!/usr/bin/env python

# Simple demo of reading each analog input from the ADS1x15 and printing it to
# the screen.
# Author: Tony DiCola
# License: Public Domain
import time

# Import the ADS1x15 module.
import Adafruit_ADS1x15


addresses = (0x48, 0x49, 0x4A, 0x4B)
ports     = (   0,    1,    2,    3)

adcs      = []
# Create an ADS1115 ADC (16-bit) instance.
for a in addresses:
    print "adding address", a
    adc  = Adafruit_ADS1x15.ADS1115(a)
    adcs.append( [ a, adc ] )

# Or create an ADS1015 ADC (12-bit) instance.
#adc = Adafruit_ADS1x15.ADS1015()

# Note you can change the I2C address from its default (0x48), and/or the I2C
# bus by passing in these optional parameters:
#adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 1

print('Reading ADS1x15 values, press Ctrl-C to quit...')
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

# Main loop.
while True:
    values  = [ -1 for n in xrange((len(ports)*len(addresses))) ]

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

    # Pause for half a second.
    time.sleep(0.5)
