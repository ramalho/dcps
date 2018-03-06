#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# Copyright (c) 2018, Stephen Goadhouse <sgoadhouse@virginia.edu>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
 
#-------------------------------------------------------------------------------
#  Control a Rigol DP832A DC Triple Power Supply with PyVISA
#
 
# python (http://www.python.org/) [Works with 2.7+ and 3+]
# pyvisa 1.9 (https://pyvisa.readthedocs.io/en/stable/)
# pyvisa-py 0.2 (https://pyvisa-py.readthedocs.io/en/latest/)
#
# NOTE: pyvisa-py replaces the need to install NI VISA libraries
# (have found the NI VISA libraries to cause my system to be unstable,
# at least on macOS, so having an alternative is a huge benefit for
# pyvisa-py)
#
#-------------------------------------------------------------------------------

# For future Python3 compatibility:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from os import environ
from time import sleep
import visa

class RigolDP832A(object):
    """Basic class for controlling and accessing a Rigol DP832A Triple Power Supply"""

    def __init__(self, resource):
        """Init the class with the instruments resource string

        resource - resource string or VISA descriptor, like TCPIP0::172.16.2.13::INSTR
        """
        self._resource = resource
        self._max_chan = 3                # number of channels

    def open(self):
        """Open a connection to the VISA device with PYVISA-py python library"""
        self._rm = visa.ResourceManager('@py')
        self._inst = self._rm.open_resource(self._resource)

    def close(self):
        """Close the VISA connection"""
        self._inst.close()
    
    def _chStr(self, channel):
        """return the channel string given the channel number and using the format CHx"""

        if (channel < 1) or (channel > self._max_chan):
            raise ValueError('Invalid channel number: {}. Must be between {} and {}, inclusive.'.
                                 format(channel, 1, self._max_chan))

        return 'CH{}'.format(channel)
    
    def _chanStr(self, channel):
        """return the channel string given the channel number and using the format x"""

        if (channel < 1) or (channel > self._max_chan):
            raise ValueError('Invalid channel number: {}. Must be between {} and {}, inclusive.'.
                                 format(channel, 1, self._max_chan))

        return '{}'.format(channel)
    
    def _onORoff(self, str):
        """Check if string says it is ON or OFF and return True if ON
        and False if OFF
        """

        # Only check first two characters so do not need to deal with
        # trailing whitespace and such
        if str[:2] == 'ON':
            return True
        else:
            return False
        
    def _wait(self):
        """Wait until all preceeding commands complete"""
        #self._inst.write('*WAI')
        self._inst.write('*OPC')
        wait = True
        while(wait):
            ret = self._inst.query('*OPC?')
            if ret[0] == '1':
                wait = False
        
    def idn(self):
        """Return response to *IDN? message"""
        return self._inst.query('*IDN?')

    def setLocal(self):
        """Set the power supply to LOCAL mode where front panel keys work again
        """

        self._inst.write(':SYSTem:LOCal')
    
    def setRemote(self):
        """Set the power supply to REMOTE mode where it is controlled via VISA
        """

        self._inst.write(':SYSTem:REMote')
    
    def setRemoteLock(self):
        """Set the power supply to REMOTE Lock mode where it is
           controlled via VISA & front panel is locked out
        """

        self._inst.write(':SYSTem:RWLock ON')
    
    def isOutputOn(self, channel):
        """Return true if the output of channel is ON, else false
        
           channel - number of the channel starting at 1
        """

        str = ':OUTPut:STATe? {}'.format(self._chStr(channel))
        ret = self._inst.query(str)
        return self._onORoff(ret)
    
    def outputOn(self, channel):
        """Turn on the output for channel
        
           channel - number of the channel starting at 1
        """

        str = ':OUTPut:STATe {},ON'.format(self._chStr(channel))
        self._inst.write(str)
    
    def outputOff(self, channel):
        """Turn off the output for channel
        
           channel - number of the channel starting at 1
        """

        str = ':OUTPut:STATe {},OFF'.format(self._chStr(channel))
        self._inst.write(str)
    
    def setVoltage(self, channel, voltage):
        """Set the voltage value for the channel
        
           channel - number of the channel starting at 1
           voltage - desired voltage value as a floating point number
        """

        str = ':SOURce{}:VOLTage {}'.format(self._chanStr(channel), voltage)
        self._inst.write(str)

        
    def setCurrent(self, channel, current):
        """Set the current value for the channel
        
           channel - number of the channel starting at 1
           current - desired current value as a floating point number
        """

        str = ':SOURce{}:CURRent {}'.format(self._chanStr(channel), current)
        self._inst.write(str)

        
    def queryVoltage(self, channel):
        """Return what voltage set value is (not the measured voltage,
        but the set voltage)
        
        channel - number of the channel starting at 1
        """

        str = ':SOURce{}:VOLTage?'.format(self._chanStr(channel))
        ret = self._inst.query(str)
        return float(ret)
    
    def queryCurrent(self, channel):
        """Return what current set value is (not the measured current,
        but the set current)
        
        channel - number of the channel starting at 1
        """

        str = ':SOURce{}:CURRent?'.format(self._chanStr(channel))
        ret = self._inst.query(str)
        return float(ret)
    
    def measureVoltage(self, channel):
        """Read and return a voltage measurement from channel
        
           channel - number of the channel starting at 1
        """

        val = self._inst.query(':MEAS:VOLT? ' + self._chStr(channel))
        return float(val)
    
    def measureCurrent(self, channel):
        """Read and return a current measurement from channel
        
           channel - number of the channel starting at 1
        """

        val = self._inst.query(':MEAS:CURRent? ' + self._chStr(channel))
        return float(val)
    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Access and control a Rigol DP832A power supply')
    parser.add_argument('chan', nargs='?', type=int, help='Channel to access/control', default=1)
    args = parser.parse_args()

    resource = environ.get('DP832A_IP', 'TCPIP0::172.16.2.13::INSTR')
    rigol = RigolDP832A(resource)
    rigol.open()

    ## set Remote Lock On
    #rigol.setRemoteLock()
    
    if not rigol.isOutputOn(args.chan):
        rigol.outputOn(args.chan)
        # give a second for power supply to enable its output
        sleep(1.0)
        
    print('Ch. {} Settings: {:6.4f} V  {:6.4f} A'.
              format(args.chan, rigol.queryVoltage(args.chan),
                         rigol.queryCurrent(args.chan)))
        
    #print(rigol.idn())
    print('{:6.4f} V'.format(rigol.measureVoltage(args.chan)))
    print('{:6.4f} A'.format(rigol.measureCurrent(args.chan)))

    rigol.setVoltage(args.chan, 2.7)
    sleep(1.0)

    print('{:6.4f} V'.format(rigol.measureVoltage(args.chan)))
    print('{:6.4f} A'.format(rigol.measureCurrent(args.chan)))

    rigol.setVoltage(args.chan, 2.3)
    sleep(1.0)

    print('{:6.4f} V'.format(rigol.measureVoltage(args.chan)))
    print('{:6.4f} A'.format(rigol.measureCurrent(args.chan)))

    ## turn off the channel
    rigol.outputOff(args.chan)

    ## return to LOCAL mode
    rigol.setLocal()
    
    rigol.close()
