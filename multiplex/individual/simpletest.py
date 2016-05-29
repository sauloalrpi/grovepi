#!/usr/bin/env python

# Simple demo of reading each analog input from the ADS1x15 and printing it to
# the screen.
# Author: Tony DiCola
# License: Public Domain
import time
import os
import sys
import json
from   collections import defaultdict

import converters

# Import the ADS1x15 module.
import Adafruit_ADS1x15


class adcs(object):
    def __init__(self):
        self.adcs      = {}

    def get(self, address):
        # Create an ADS1115 ADC (16-bit) instance.

        if address not in self.adcs:
            print "adding address", address

            addressInt = address
            if any([isinstance(addressInt, x) for x in [str, unicode]]):
                print "converting address {}".format(addressInt),
                addressInt = int(addressInt, 16)
                print "to {}".format( addressInt )

            else:
                print "address {} already {}".format(addressInt, type(addressInt))
            
            self.adcs[ address ] = Adafruit_ADS1x15.ADS1115( addressInt )
        
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

    def __init__(self, address=None, port=None, gain=None, name=None, model=None, samples=1, data_rate=128, delay=0, version=""):
        if any([x is None for x in address, port, gain, name, model]):
            print "Address {} port {} gain {} name {} model {} are all compulsory parameters".format(address, port, gain, name, model)
            sys.exit(1)

        if gain == "2/3": gain = 2/3

        self.address    = address
        self.port       = port
        self.gain       = gain
        self.name       = name
        self.model      = model

        self.samples    = samples
        self.data_rate  = data_rate
        self.delay      = delay
        self.version    = version

        self.to_voltage = converters.ADS1115_value_converter(gain)
        self.converter  = converters.get_converter(self.model, self.version, self.to_voltage)

    def read_adc(self):
        adc  = self.adcs.get(self.address)

        val = adc.read_adc(self.port, gain=self.gain)

        # https://forums.adafruit.com/viewtopic.php?f=19&t=83633
        # The chip might have some accumulated charge or ADC offset, so try taking two readings, 
        # throwing the first away, then using the second. Sometimes that's the best way to 
        # handle such a change.

        time.sleep(0.0001)

        val = adc.read_adc(self.port, gain=self.gain, data_rate=self.data_rate)

        return val

    def raw(self):
        """
        Note you can also pass in an optional data_rate parameter that controls
        the ADC conversion time (in samples/second). Each chip has a different
        set of allowed data rate values, see datasheet Table 9 config register
        DR bit values.
        values[i] = adc.read_adc(i, gain=GAIN, data_rate=128)
        Each value will be a 12 or 16 bit signed integer value depending on the
        ADC (ADS1015 = 12-bit, ADS1115 = 16-bit).
        """

        val  = None
        if self.samples > 1:
            vals = []

            for i in xrange(self.samples):
                val  = self.read_adc()
                vals.append(val)
                if self.delay > 0:
                    #print "s",
                    time.sleep(self.delay)

            val  = float(sum(vals))/float(len(vals))

        else:
            val  = self.read_adc()

        return val
        
    def conv(self, val=None):
        if val is None:
            val = self.raw()

        return self.converter(val)

    def both(self):
        val = self.raw()
        cnv = self.conv(val=val)

        return (val, cnv)

    def conf_as_dict(self):
        return {
            'address'  : self.address  ,
            'port'     : self.port     ,
            'gain'     : self.gain     ,
            'name'     : self.name     ,
            'samples'  : self.samples  ,
            'data_rate': self.data_rate,
            'delay'    : self.delay    ,
            'model'    : self.model    ,
            'version'  : self.version
        }

    def conf_as_str(self):
        conf = self.conf_as_dict()
        return " ".join(["{}: {}".format(x, conf[x]) for x in sorted(conf.keys())])

    def as_dict(self):
        raw, conv = self.both()

        conf      = self.conf_as_dict()

        conf['raw' ] = raw

        for c in conv:
            conf['conv {}'.format(c)] = conv[c]

        return conf

    def as_str(self, data=None):
        if data is not None:
            data = self.as_dict()

        res  =       " ".join( ["{}: {}"     .format(x, data[x]) for x in sorted( data        .keys() ) if x != 'conv' ] )
        res += " " + " ".join( ["conv {}: {}".format(x, data[x]) for x in sorted( data['conv'].keys() )                ] )

        return res

    def printer(self):
        print str(self)

    def __repr__(self):
        return "<SENSOR :: {}>".format(self.conf_as_str())
        

class controller_fmt(object):
    def __init__(self, cols):
        self.cols          = cols

        self.max_address   = 0
        self.max_cell      = 0

        self.fmt_address   = ""
        self.fmt_cell_t    = ""
        self.fmt_cell_v    = ""
        self.fmt_row_line  = ""
        self.fmt_cols      = [ c.title() for c in self.cols ]
        self.fmt_cols_max  = max([len(x) for x in self.fmt_cols])
        self.fmt_list      = ""
        self.fmt_list_len  = 0

    def update(self, sensors, sens):
        self.max_address   = len(str(sens.address)) if len(str(sens.address)) > self.max_address else self.max_address
        self.max_cell      = max([len(str(x)) for x in [sens.address, sens.port, sens.name, sens.model, sens.version, sens.gain, sens.samples]] + [self.max_cell, self.fmt_cols_max])

        self.fmt_address   = '|{:'+str(self.max_cell)+'s}|'
        self.fmt_cell_t    = '|{:'+str(self.max_cell)+'s}|'
        self.fmt_cell_v    = '|{:'+str(self.max_cell)+'s}|'
        self.fmt_row_line  = '|' + ('-'*self.max_cell) + '|'

        num_ids            = 7
        num_vals           = 2
        num_cols           = num_ids + num_vals

        self.fmt_list      = '|' + (('{:'+str(self.max_cell)+'s}|')*(num_ids)) + (('{:>'+str(self.max_cell)+'s}|')*(num_vals))
        self.fmt_list_len  = (self.max_cell*num_cols) + num_cols + 1

        for sensor_num, (address, ports) in enumerate(sorted(sensors.items())):
            num_ports          = len(ports)
            len_port           = ( self.max_cell * num_ports )
            self.fmt_address  += '{:'+str(len_port+num_ports-1)+'s}|'
            self.fmt_row_line += '-'*(len_port+num_ports-1) + '|'

            for port_num, (port, sen) in enumerate(sorted(ports.items())):
                self.fmt_cell_t += '{:' +str(self.max_cell)+'s}|'
                self.fmt_cell_v += '{:>'+str(self.max_cell)+'s}|'

    def get_as_table(self, data):
        addresses = [self.fmt_cols[0]] + [     d[0]  for d in data ]

        line  = self.fmt_row_line.format() + "\n"
        line += self.fmt_address .format( *addresses ) + "\n"

        for i in xrange(1, len(data[0]) -2):
            vals = [self.fmt_cols[i]] + [ str(d[i]) for d in data ]
            line += self.fmt_cell_t  .format( *vals ) + "\n"

        line += self.fmt_row_line.format() + "\n"

        for i in xrange(len(data[0]) -2, len(data[0])):
            vals = [self.fmt_cols[i]] + [ str(d[i]) for d in data ]
            line += self.fmt_cell_v  .format( *vals )  + "\n"

        line += self.fmt_row_line.format() + "\n\n"

        return line

    def get_as_list(self, data):
        line  = '-'*(self.fmt_list_len) + "\n"

        line += self.fmt_list.format(*self.fmt_cols) + "\n"

        line += '-'*(self.fmt_list_len) + "\n"

        for row_num, row in enumerate(data):
            line += self.fmt_list.format(*[str(x) for x in row])  + "\n"

        line += '-'*(self.fmt_list_len) + "\n\n"

        return line

    def get_as_str(self, data):
        line  = ""

        for row in data:
            line += " ".join( [ " {}: {}".format(self.fmt_cols[c], row[c]) for c in xrange(len(self.fmt_cols)) ] ) + "\n"

        return line


class controller(object):
    def __init__(self, delay=0):
        self.delay      = delay

        self.sensors    = defaultdict(dict)

        self.print_fmts = {
            'table': self.print_as_table,
            'list' : self.print_as_list ,
            'str'  : self.print_as_str
        }

        self.cols      = ('address', 'port', 'name', 'model', 'version', 'gain', 'samples', 'raw', 'conv fmt')

        self.formatter = controller_fmt(self.cols)

    def add_sensor(self, data):
        sens = sensor(**data)

        self.sensors[sens.address][sens.port] = sens

        self.formatter.update(self.sensors, sens)

    def as_dict(self):
        data = defaultdict(dict)
        
        for address, ports in sorted(self.sensors.items()):
            for port, sensor in sorted(ports.items()):
                data[address][port] = sensor.as_dict()
                time.sleep(self.delay)

        return data

    def as_table(self, data=None):
        if data is None:
            data      = self.as_dict()

        res  = []

        for address, ports in sorted(data.items()):
            for port, sens in sorted(ports.items()):
                res.append( tuple( [ sens[x] for x in self.cols ] ) )

        return res

    def printer(self, data=None, fmt='table'):
        if fmt in self.print_fmts:
            self.print_fmts[fmt](data=data)

        else:
            print "unknown format"
            sys.exit(1)

    def print_as_table(self, data=None):
        if data is None:
            data      = self.as_table()

        print self.formatter.get_as_table(data)

    def print_as_list(self, data=None):
        if data is None:
            data      = self.as_table()

        print self.formatter.get_as_list(data)

    def print_as_str(self, data=None):
        if data is None:
            data      = self.as_table()

        print "CONTROLLER START"

        print self.formatter.get_as_str(data),

        print "CONTROLLER END\n"

    def __repr__(self, data=None):
        line  = "CONTROLLER START\n"

        for address, ports in sorted(data.items()):
            for port, sens in sorted(ports.items()):
                line += sens.conf_as_str() + "\n"

        line += "CONTROLLER END\n"

        return line

def correct_devices(devices):
    for address, ports in devices.items():
        for port, data in ports.items():
            ports[int(port)] = data
            del ports[port]
        #devices[int(address, 16)] = ports
        #del devices[address]
    return devices

def getController(config):
    print('Reading ADS1x15 values, press Ctrl-C to quit...')

    devices   = config['devices']
    devices   = correct_devices(devices)
    delay     = config.get('delay', 0)
    ctrl      = controller(delay=delay)

    for address, ports in sorted(devices.items()):
        for port, cfg in sorted(ports.items()):
            cfg["address"] = address
            cfg["port"   ] = port
            ctrl.add_sensor( cfg )

    return ctrl



def main():
    infile    = sys.argv[1]

    filecont  = open(infile, 'r').read()

    config    = json.loads(filecont)

    ctrl      = getController(config)

    print_as  = config.get('print_as' , 'table')

    sleep_for = config.get('sleep_for',     0.5)

    print "sleep_for", sleep_for

    # Main loop.
    while True:
        ctrl.printer(fmt=print_as)

        """
        t = ctrl.as_table()
        for f in ('str', 'list', 'table'): ctrl.printer(fmt=f, data=t)
        """

        # Pause for half a second.
        time.sleep(sleep_for)




if __name__ == "__main__":
    main()
