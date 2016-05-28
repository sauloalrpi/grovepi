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

    def __init__(self, address, port, gain, name, model="", version=""):
        print 'address', address

        if gain == "2/3": gain = 2/3

        self.address    = address
        self.port       = port
        self.gain       = gain
        self.name       = name
        self.model      = model
        self.version    = version
        self.to_voltage = converters.ADS1115_value_converter(gain)
        self.converter  = converters.get_converter(self.model, self.version, self.to_voltage)

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
        adc = self.adcs.get(self.address)
        val = adc.read_adc(self.port, gain=self.gain)
        return val
        
    def conv(self, val=None):
        if val is None:
            val = self.raw()
        return self.converter(val)

    def both(self):
        val = self.raw()
        cnv = self.conv(val=val)
        return (val, cnv)

    def as_dict(self):
        raw, conv = self.both()

        return {
            'address'  : self.address ,
            'port'     : self.port    ,
            'gain'     : self.gain    ,
            'name'     : self.name    ,
            'model'    : self.model   ,
            'version'  : self.version ,
            'raw'      : raw          ,
            'conv'     : conv
        }

    def printer(self):
        print str(self)

    def __repr__(self):
        return "<SENSOR :: {} : address: {} port: {} gain: {} model: {} version: {}>".format(self.name, hex(self.address), self.port, self.gain, self.model, self.version)
        

class controller(object):
    def __init__(self):
        self.sensors = defaultdict(lambda: defaultdict(dict))

        self.print_fmts = {
            'table': self.print_as_table,
            'list' : self.print_as_list ,
            'raw'  : self.print_as_raw
        }

        self.max_address   = 0
        self.max_cell      = 0

        self.fmt_address   = ""
        self.fmt_cell      = ""
        self.fmt_row_line  = ""
        self.fmt_list      = ""
        self.fmt_list_len  = 0

    def add_sensor(self, address, port, gain, name, model="", version="", converter=None):
        self.sensors[address][port][name] = sensor(address, port, gain, name, model=model, version=version)

        self.max_address   = len(str(hex(address))) if len(str(hex(address))) > self.max_address else self.max_address
        self.max_cell      = max([len(str(x)) for x in [hex(address), str(port), str(gain), str(name), str(model), str(version)]] + [self.max_cell])

        self.fmt_address   = '|'
        self.fmt_cell      = '|'
        self.fmt_row_line  = '|'

        num_ids            = 5
        num_vals           = 2
        num_cols           = num_ids + num_vals
        self.fmt_list      = '|' + (('{:'+str(self.max_cell)+'s}|')*(num_ids)) + (('{:>'+str(self.max_cell)+'s}|')*(num_vals))
        self.fmt_list_len  = (self.max_cell*num_cols) + num_cols + 1

        for sensor_num, (address, ports) in enumerate(sorted(self.sensors.items())):
            num_ports          = len(ports)
            len_port           = ( self.max_cell * num_ports )
            self.fmt_address  += '{:'+str(len_port)+'s}|'
            self.fmt_row_line += '-'*(len_port) + '|'

            for port_num, (port, names) in enumerate(sorted(ports.items())):
                self.fmt_cell += '{:'+str(self.max_cell)+'s}|'

    def as_dict(self):
        data = defaultdict(lambda: defaultdict(dict))
        
        for address, ports in sorted(self.sensors.items()):
            for port, names in sorted(ports.items()):
                for name, sensor in sorted(names.items()):
                    data[address][port][name] = sensor.as_dict()

        return data

    def as_table(self):
        data = self.as_dict()
        res  = []

        for address, ports in sorted(data.items()):
            for port, names in sorted(ports.items()):
                for name, vals in sorted(names.items()):
                    model   = vals['model'  ]
                    version = vals['version']
                    raw     = vals['raw'    ]
                    conv    = vals['conv'   ]
                    res.append( ( hex(address), port, name, model, version, raw, conv ) )

        return res

    def printer(self, fmt='table'):
        if fmt in self.print_fmts:
            self.print_fmts[fmt]()

        else:
            print "unknown format"
            sys.exit(1)

    def print_as_table(self, fmt="raw"):
        data      = self.as_table()

        gtr       = 5 if fmt == "raw" else 6

        addresses = [ str(d[  0]) for d in data ]
        ports     = [ str(d[  1]) for d in data ]
        names     = [     d[  2]  for d in data ]
        models    = [     d[  3]  for d in data ]
        versions  = [     d[  4]  for d in data ]
        vals      = [ str(d[gtr]) for d in data ]

        print self.fmt_row_line.format()
        print self.fmt_address .format( *addresses )
        print self.fmt_cell    .format( *ports     )
        print self.fmt_cell    .format( *names     )
        print self.fmt_cell    .format( *models    )
        print self.fmt_cell    .format( *versions  )
        print self.fmt_row_line.format()
        print self.fmt_cell    .format( *vals      )
        print self.fmt_row_line.format()
        print

    def print_as_list(self):
        data      = self.as_table()

        print '-'*(self.fmt_list_len)

        for row_num, line in enumerate(data):
            lineFmt =  self.fmt_list.format(*[str(x) for x in line])
            print lineFmt

        print '-'*(self.fmt_list_len)
        print

    def print_as_raw(self):
        print str(self)

    def __repr__(self):
        data = self.as_table()

        line  = "CONTROLLER START\n"

        for dat in data:
            line += " address {} port {} name {} model {} version {} raw {} conv {}\n".format(*dat)

        line += "CONTROLLER END\n"

        return line

def correct_devices(devices):
    for address, ports in devices.items():
        for port, data in ports.items():
            ports[int(port)] = data
            del ports[port]
        devices[int(address, 16)] = ports
        del devices[address]
    return devices

def start(config):
    print('Reading ADS1x15 values, press Ctrl-C to quit...')

    print_as  = config.get('print_as' , 'table')
    sleep_for = config.get('sleep_for', 0.5)
    devices   = config['devices']

    devices   = correct_devices(devices)

    ctrl      = controller()

    for address, ports in sorted(devices.items()):
        for port, cfg in sorted(ports.items()):
            name      = cfg["name"]
            gain      = cfg.get("gain"     ,    1)
            model     = cfg.get("model"    ,   "")
            version   = cfg.get("version"  ,   "")
            ctrl.add_sensor( address, port, gain, name, model=model, version=version )

    # Main loop.
    while True:
        ctrl.printer(fmt=print_as)

        #ctrl.printer(fmt='raw'  )
        #ctrl.printer(fmt='list' )
        #ctrl.printer(fmt='table')

        # Pause for half a second.
        time.sleep(sleep_for)





def main():
    infile = sys.argv[1]

    filecont = open(infile, 'r').read()

    print filecont

    config = json.loads(filecont)

    print config

    start(config)



if __name__ == "__main__":
    main()
