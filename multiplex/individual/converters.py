import math

"""
#https://learn.adafruit.com/adafruit-4-channel-adc-breakouts?view=all

The ADS1115 and ADS1015 4-channel breakout boards are perfect for 
adding high-resolution analog to digital conversion to any 
microprocessor-based project. These boards can run with power and 
logic signals between 2v to 5v, so they are compatible with all 
common 3.3v and 5v processors.  As many of 4 of these boards can 
be controlled from the same 2-wire I2C bus, giving you up to 16 
single-ended or 8 differential channels.  A programmable gain 
amplifier provides up to x16 gain for small signals.

ADS1115:
Resolution: 16 Bits
Programmable Sample Rate: 8 to 860 Samples/Second
Power Supply/Logic Levels: 2.0V to 5.5V

Single ended inputs can, by definition, only measure positive 
voltages. Without the sign bit, you only get an effective 15 bit 
resolution.

If we had an analog sensor with an output voltage ~1V (a TMP36, 
for example), we could set the gain on the ADC to GAIN_FOUR, which 
would give us a +/-1.024V range. This would push the 1V input 
signal over the entire 12-bit or 16-bit range of the ADC, compared 
to the very limited range 1V would cover without adjusting the 
gain settings

Choose a gain of 1 for reading voltages from 0 to 4.09V.
Or pick a different gain to change the range of voltages that are read:
 - 2/3 = +/-6.144V 1 bit = 3mV (default)
 -   1 = +/-4.096V 1 bit = 2mV
 -   2 = +/-2.048V 1 bit = 1mV
 -   4 = +/-1.024V 1 bit = 0.5mV
 -   8 = +/-0.512V 1 bit = 0.25mV
 -  16 = +/-0.256V 1 bit = 0.125mV
"""


def ADS1115_value_converter(gain, bits=15):
    if gain == 2/3:
        gain = 2.0/3.0

    maxRange    = math.pow(2, bits)

    gainVoltage = ((float(math.pow(2,12))/1000.0) / gain) # 4096 / 1000 = 4.096

    vRange      = [0, gainVoltage]

    print "gain {:.2f} maxRange {} vRange {}".format(gain, maxRange, str(vRange))

    def conv(value):
        res = (float(value) / float(maxRange)) * float(vRange[1] - vRange[0])
        #print "maxRange {} vRange {} value {} res {}".format(maxRange, str(vRange), value, res)
        return res

    return conv

def APDS_9002(version, to_voltage, fmt="{:4.0f} Lux"):
    """
    Luminance sensor
    http://www.seeedstudio.com/wiki/Grove_-_Luminance_Sensor

    Grove - Luminance Sensor detects the intensity of the ambient 
    light on a surface area. It uses APDS-9002 analog output ambient 
    light photo sensor. This has responsivity closer to human eye.

    Specification

    Parameter                   Value
    Vcc                         2.4V ~ 5.5V
    Linear output range         0.0 ~ 2.3V
    Luminance measurement range 0 ~ 1000 Lux

    // MeasuredVout = ADC Value * (Vcc / 1023) * (3 / Vcc)
    // Vout samples are with reference to 3V Vcc
    // The above expression is simplified by cancelling out Vcc 
    float MeasuredVout = analogRead(A0) * (3.0 / 1023.0);
    //Above 2.3V , the sensor value is saturated

    /**************************************************************************
    
    The Luminance in Lux is calculated based on APDS9002 datasheet -- > Graph 1 
    ( Output voltage vs. luminance at different load resistor)
    The load resistor is 1k in this board. Vout is referenced to 3V Vcc.
    
    The data from the graph is extracted using WebPlotDigitizer 
    http://arohatgi.info/WebPlotDigitizer/app/
    
    VoutArray[] and LuxArray[] are these extracted data. Using MultiMap, the data
    is interpolated to get the Luminance in Lux.
    
    This implementation uses floating point arithmetic and hence will consume 
    more flash, RAM and time.
    
    The Luminance in Lux is an approximation and depends on the accuracy of
    Graph 1 used.
    
    ***************************************************************************/

    float VoutArray[] =  { 0.0011498,  0.0033908,   0.011498, 0.041803,0.15199,     0.53367, 1.3689,   1.9068,  2.3};
    float  LuxArray[] =  { 1.0108,     3.1201,  9.8051,   27.43,   69.545,   232.67,  645.11,   873.52,  1000};

    // MeasuredVout = ADC Value * (Vcc / 1023) * (3 / Vcc)
    // Vout samples are with reference to 3V Vcc
    // The above expression is simplified by cancelling out Vcc 
    float MeasuredVout = analogRead(A0) * (3.0 / 1023.0);
    float Luminance = FmultiMap(MeasuredVout, VoutArray, LuxArray, 9);
    """

    #             1          2          3         4          5         6          7         8         9
    VoutArray = [ 0.0011498, 0.0033908, 0.011498,  0.041803,  0.15199,   0.53367,   1.3689,   1.9068,    2.3 ];
    LuxArray  = [ 1.0108000, 3.1201000, 9.805100, 27.430000, 69.54500, 232.67000, 645.1100, 873.5200, 1000.0 ];
    size      = len(VoutArray)

    def func(value):
        #print "APDS_9002 :: value  : {}".format(value)
        val = to_voltage( value )
        #print "APDS_9002 :: voltage: {}".format(val  )

        Luminance = -1

        # take care the value is within range
        # val = constrain(val, _in[0], _in[size-1]);
        if   (val <= VoutArray[0     ]):
            Luminance = LuxArray[0     ]

        elif (val >= VoutArray[size-1]):
            Luminance =  LuxArray[size-1]

        else:
            # search right interval
            pos = 1;  # _in[0] allready tested
            while(val > VoutArray[pos]): pos += 1

            # this will handle all exact "points" in the _in array
            if (val == VoutArray[pos]):
                Luminance = LuxArray[pos]

            else:
                # interpolate in the right segment for the rest
                Luminance = (val - VoutArray[pos-1]) * (LuxArray[pos] - LuxArray[pos-1]) / (VoutArray[pos] - VoutArray[pos-1]) + LuxArray[pos-1]

        return fmt.format( Luminance )

    return func

def GL5528(version, to_voltage, fmt="{:4.0f} Lux"):
    """
    Light sensor
    http://www.seeedstudio.com/wiki/Grove_-_Light_Sensor

    The Grove - Light Sensor module incorporates a Light Dependent Resistor 
    (LDR). Typically, the resistance of the LDR or Photoresistor will 
    decrease when the ambient light intensity increases. This means that 
    the output signal from this module will be HIGH in bright light, and 
    LOW in the dark.

    Specifications:
    Voltage: 3-5V
    Supply Current: 0.5-3mA
    Light resistance: 20KΩ
    Dark resistance: 1MΩ
    Response time: 20-30 secs
    Peak Wavelength: 540 nm
    Ambient temperature: -30~70℃
    """

    def func(value):
        print "APDS_9002 :: value  : {}".format(value)
        val = to_voltage( value )
        print "APDS_9002 :: voltage: {}".format(val  )

        return val

    return func

def get_converter(model, version, gain):
    if model in db:
        return db[model](version, gain)

    else:
        print "no such converter {}".format(model)
        sys.exit(1)


db = {
    "GL5528"   :    GL5528,
    "APDS-9002": APDS_9002,
}


def main():
    print "\n".join(sorted(db.keys()))


if __name__ == "__main__":
    main()
