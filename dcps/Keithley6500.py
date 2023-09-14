#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# Copyright (c) 2018, 2021, 2023, Stephen Goadhouse <sgoadhouse@virginia.edu>
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
#  Control a Keithley DMM6500 Digital Multimeter (DMM) with PyVISA
#-------------------------------------------------------------------------------

# For future Python3 compatibility:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

try:
    from . import SCPI
except:
    from SCPI import SCPI
    
from time import sleep
import pyvisa as visa


class Keithley6500(SCPI):
    """Basic class for controlling and accessing a Keithley/Tektronix DMM6500 digital multimeter"""

    ## Dictionary to translate SCPI commands for this device
    _xlateCmdTbl = {
        #@@@#'setLocal':                      ':TRIG:CONT REST\r\nLOGOUT',
    }

    def __init__(self, resource, wait=0.01, verbosity=0, **kwargs):
        """Init the class with the instruments resource string

        resource - resource string or VISA descriptor, like TCPIP0::172.16.2.13::INSTR
        wait     - float that gives the default number of seconds to wait after sending each command
        verbosity - verbosity output - set to 0 for no debug output
        kwargs    - other named options to pass when PyVISA open() like open_timeout=2.0
        """
        self._functions = { 'VoltageDC':   'VOLT',
                            'VoltageAC':   'VOLT:AC',
                            'CurrentDC':   'CURR',
                            'CurrentAC':   'CURR:AC',
                            'Resistance2W':'RES',
                            'Resistance4W':'FRES',
                            'Diode':       'DIODe',
                            'Capacitance': 'CAP',
                            'Temperature': 'TEMP',
                            'Continuity':  'CONT',
                            'Frequency':   'FREQ',
                            'Period':      'PERiod',
                            'VoltageRatio':'VOLT:RATio',
                           }
        # default measurement function if not supplied as parameter into the method
        self._functionStr = None
        
        super(Keithley6500, self).__init__(resource, max_chan=1, wait=wait, cmd_prefix=':', verbosity = verbosity, read_termination = '\n', **kwargs)

    def setLocal(self):
        """Set the instrument to LOCAL mode where front panel keys
        work again. Also restore Continuous reading mode.

        """
        self._instWrite('TRIG:CONT REST')
        sleep(0.01)
        self._instQuery('-LOGOUT')

    def setRemote(self):
        """Set the instrument to REMOTE mode where it is controlled via VISA
        """

        # NOTE: Unsupported command by this device. However, with any
        # command sent to the DMM6500, it automatically goes into
        # REMOTE mode. Instead of raising an exception and breaking
        # any scripts, simply return quietly.
        pass
    
    def setRemoteLock(self):
        """Set the instrument to REMOTE Lock mode where it is
           controlled via VISA & front panel is locked out
        """
        # NOTE: Unsupported command by this device. However, with any
        # command sent to the DMM6500, it automatically goes into
        # REMOTE mode. Instead of raising an exception and breaking
        # any scripts, simply return quietly.
        #
        # Truth be told, there is a SYSTEM:ACCESS command which has
        # various options and could be used here but for simplicity,
        # ignore that for now.
        pass
        
    def beeperOn(self):
        """Enable the system beeper for the instrument"""
        # NOTE: Unsupported command by this device. However,
        # instead of raising an exception and breaking any scripts,
        # simply return quietly.
        pass
        
    def beeperOff(self):
        """Disable the system beeper for the instrument"""
        # NOTE: Unsupported command by this device. However,
        # instead of raising an exception and breaking any scripts,
        # simply return quietly.
        pass
        
    def isOutputOn(self, channel=None):
        """Return true if the output of channel is ON, else false
        
           channel - number of the channel starting at 1
        """
        # NOTE: Unsupported command by this device. However,
        # instead of raising an exception and breaking any scripts,
        # simply return False as there is NO output for the DMM6500.
        return False

    def outputOn(self, channel=None, wait=None):
        """Turn on the output for channel
        
           wait    - number of seconds to wait after sending command
           channel - number of the channel starting at 1
        """
        # NOTE: Unsupported command by this device. However,
        # instead of raising an exception and breaking any scripts,
        # simply return quietly.
        pass
        
    def outputOff(self, channel=None, wait=None):
        """Turn off the output for channel
        
           channel - number of the channel starting at 1
        """
        # NOTE: Unsupported command by this device. However,
        # instead of raising an exception and breaking any scripts,
        # simply return quietly.
        pass

    def outputOnAll(self, wait=None):
        """Turn on the output for ALL channels
        
        """
        # NOTE: Unsupported command by this device. However,
        # instead of raising an exception and breaking any scripts,
        # simply return quietly.
        pass

    def outputOffAll(self, wait=None):
        """Turn off the output for ALL channels
        
        """
        # NOTE: Unsupported command by this device. However,
        # instead of raising an exception and breaking any scripts,
        # simply return quietly.
        pass

    def isInputOn(self, channel=None):
        """Return true if the input of channel is ON, else false
        
           channel - number of the channel starting at 1
        """
        # NOTE: Unsupported command by this device. However,
        # instead of raising an exception and breaking any scripts,
        # simply return True as the "INPUT" is always On for the DMM6500.
        return True

    def inputOn(self, channel=None, wait=None):
        """Turn on the input for channel
        
           wait    - number of seconds to wait after sending command
           channel - number of the channel starting at 1
        """
        # NOTE: Unsupported command by this device. However,
        # instead of raising an exception and breaking any scripts,
        # simply return quietly.
        pass

    def inputOff(self, channel=None, wait=None):
        """Turn off the input for channel
        
           channel - number of the channel starting at 1
        """
        # NOTE: Unsupported command by this device. However,
        # instead of raising an exception and breaking any scripts,
        # simply return quietly.
        pass

    def inputOnAll(self, wait=None):
        """Turn on the input for ALL channels
        
        """
        # NOTE: Unsupported command by this device. However,
        # instead of raising an exception and breaking any scripts,
        # simply return quietly.
        pass

    def inputOffAll(self, wait=None):
        """Turn off the input for ALL channels
        
        """
        # NOTE: Unsupported command by this device. However,
        # instead of raising an exception and breaking any scripts,
        # simply return quietly.
        pass

        
    ###################################################################
    # Commands Specific to DMM6500
    ###################################################################

    def displayMessageOn(self, top=True):
        """Enable Display Message
           NOTE: using same format as from Keithley622x.py but this one works a little differently
        
           top     - True if enabling the Top message, else enable Bottom message
        """

        ## top is ignored
        ## swipe screen to show User text
        self._instWrite('DISPlay:SCReen SWIPE_USER')

    def displayMessageOff(self, top=True):
        """Disable Display Message
           NOTE: using same format as from Keithley622x.py but this one works a little differently
        
           top     - True if disabling the Top message, else disable Bottom message
        """

        ## top is ignored
        ## first clear out user message and then ...
        ## swipe screen to show HOME - does not have a display disable as Keithley622x does
        self._instWrite('DISPlay:CLE')
        self._instWrite('DISPlay:SCReen HOME')

            
    def setDisplayMessage(self, message, top=True):
        """Set the Message for Display. Use displayMessageOn() or
           displayMessageOff() to enable or disable message, respectively.
        
           message - message to set
           top     - True if setting the Top message, else set Bottom message

        """

        if (top):
            # Maximum of 20 characters for top message
            if (len(message) > 20):
                message = message[:20]
            self._instWrite('DISP:USER1:TEXT "{}"'.format(message))
        else:
            # Maximum of 32 characters for bottom message
            if (len(message) > 32):
                message = message[:32]
            self._instWrite('DISP:USER2:TEXT "{}"'.format(message))

    def setMeasureFunction(self, function, channel=None, wait=None):
        """Set the Measure Function for channel

           function   - a key from self._functions{} that selects the measurement function
           channel    - number of the channel starting at 1
           wait       - number of seconds to wait after sending command

           NOTE: Error raised if function is unknown
        """

        # Lookup function command string
        functionCmdStr = self._functions.get(function)
        if not functionCmdStr:
            raise ValueError('setMeasureFunction(): "{}" is an unknown function.'.format(function))

        # function must be valid, so save it for future use
        self._functionStr = function
        
        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel

        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait

        str = 'SENS{}:FUNC:ON "{}"'.format(self.channel, functionCmdStr)            

        self._instWrite(str)

    def setAutoZero(self, on, function=None, channel=None, wait=None):
        """Enable or Disable the AutoZero mode for the function

           on         - set to True to Enable AutoZero or False to Disable AutoZero
           function   - a key from self._functions{} to select the measurement function or None for default
           channel    - number of the channel starting at 1
           wait       - number of seconds to wait after sending command
        """

        if (function is None):
            # Use the, hopefully previously set, self._functionStr
            functionStr = self._functionStr
        else:
            # Else, use the passed in function string
            functionStr = function

        # Lookup function
        functionCmdStr = self._functions.get(functionStr)
        if not functionCmdStr:
            raise ValueError('setAutoZero(): "{}" is an unknown function.'.format(functionStr))

        ## Not all Functions support setting AutoZero so raise
        ## ValueError() if trying to set AutoZero for one of those.
        allowedFunctions = ['VOLT','CURR','RES','FRES','DIODe','TEMP','VOLT:RATio',]
        if (functionCmdStr not in allowedFunctions):
            raise ValueError('setAutoZero(): Changing AutoZero is not valid for function "{}".'.format(functionStr))
            
        
        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel

        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait

        str = 'SENS{}:{}:AZERo:STATe {}'.format(self.channel, functionCmdStr, self._bool2onORoff(on))
        #@@@#print('AutoZero State String: {}'.format(str))

        self._instWrite(str)

        sleep(wait)             # give some time for device to respond
        
        
    def autoZeroOnce(self, channel=None, wait=None):
        """Issue an AutoZero command to be performed once. Oddly, it takes no function name.

           channel    - number of the channel starting at 1
           wait       - number of seconds to wait after sending command
        """
        
        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel

        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait

        str = 'SENS{}:AZERo:ONCE'.format(self.channel)
        print('AutoZero Once String: {}'.format(str))

        self._instWrite(str)

        sleep(wait)             # give some time for device to respond

        self._waitCmd()         # make sure command is complete in instrument

        
    def setRelativeOffset(self, offset=None, function=None, channel=None, wait=None):
        """Set the Relative Offset for the Function

           offset     - floating point value to set as relative offset or, if None, have instrument acquire it
                        offset can also be "DEF" for default, "MAX" for maximum or "MIN" for minimum
           function   - a key from self._functions{} to select the measurement function or None for default
           channel    - number of the channel starting at 1
           wait       - number of seconds to wait after sending command
        """

        if (function is None):
            # Use the, hopefully previously set, self._functionStr
            functionStr = self._functionStr
        else:
            # Else, use the passed in function string
            functionStr = function

        # Lookup function
        functionCmdStr = self._functions.get(functionStr)
        if not functionCmdStr:
            raise ValueError('setAutoZero(): "{}" is an unknown function.'.format(functionStr))

                    
        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel

        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait

        if (offset is None):
            ## Have the instrument acquire the relative offset
            str = 'SENS{}:{}:REL:ACQuire'.format(self.channel, functionCmdStr)
        else:
            str = 'SENS{}:{}:REL {}'.format(self.channel, functionCmdStr, offset)

        #@@@#print('Relative Offset String: {}'.format(str))

        self._instWrite(str)

        sleep(wait)             # give some time for device to respond
        
        
    def queryRelativeOffset(self, function=None, channel=None, wait=None):
        """Query the Relative Offset for the Function

           function   - a key from self._functions{} to select the measurement function or None for default
           channel    - number of the channel starting at 1
           wait       - number of seconds to wait after sending command
        """

        if (function is None):
            # Use the, hopefully previously set, self._functionStr
            functionStr = self._functionStr
        else:
            # Else, use the passed in function string
            functionStr = function

        # Lookup function
        functionCmdStr = self._functions.get(functionStr)
        if not functionCmdStr:
            raise ValueError('setAutoZero(): "{}" is an unknown function.'.format(functionStr))

                    
        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel

        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait


        str = 'SENS{}:{}:REL?'.format(self.channel, functionCmdStr)

        #@@@#print('Relative Offset Query String: {}'.format(str))

        offset = self._instQuery(str)

        sleep(wait)             # give some time for device to respond

        return float(offset)
    
    def setRelativeOffsetState(self, on, function=None, channel=None, wait=None):
        """Set the Relative Offset State for the Function

           on         - set to True to Enable use of Relative Offset or False to Disable it
           function   - a key from self._functions{} to select the measurement function or None for default
           channel    - number of the channel starting at 1
           wait       - number of seconds to wait after sending command
        """

        if (function is None):
            # Use the, hopefully previously set, self._functionStr
            functionStr = self._functionStr
        else:
            # Else, use the passed in function string
            functionStr = function

        # Lookup function
        functionCmdStr = self._functions.get(functionStr)
        if not functionCmdStr:
            raise ValueError('setAutoZero(): "{}" is an unknown function.'.format(functionStr))

                    
        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel

        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait

        str = 'SENS{}:{}:REL:STATe {}'.format(self.channel, functionCmdStr, self._bool2onORoff(on))

        #@@@#print('Relative Offset State String: {}'.format(str))

        self._instWrite(str)

        sleep(wait)             # give some time for device to respond

        
    def measureResistance(self, channel=None):
        """Read and return a resistance measurement from channel
        
           channel - number of the channel starting at 1
        """

        self.setMeasureFunction(function="Resistance2W",channel=channel)

        val = self._instQuery('READ?')        
        return float(val)
        
    def measureVoltage(self, channel=None):
        """Read and return a DC Voltage measurement from channel
        
           channel - number of the channel starting at 1
        """

        self.setMeasureFunction(function="VoltageDC",channel=channel)

        #@@@#vals = self._instQuery('READ?').split(',')
        val = self._instQuery('READ?')
        #@@@#print('Value: "{}" / {}'.format(val,float(val)))
        return float(val)
        
    def measureCurrent(self, channel=None):
        """Read and return a DC Current measurement from channel
        
           channel - number of the channel starting at 1
        """

        self.setMeasureFunction(function="CurrentDC",channel=channel)

        val = self._instQuery('READ?')
        return float(val)
        
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Access and control a Keithley DMM6500 digital multimeter')
    parser.add_argument('chan', nargs='?', type=int, help='Channel to access/control (starts at 1)', default=1)
    args = parser.parse_args()

    from time import sleep
    from os import environ
    resource = environ.get('DMM6500_VISA', 'TCPIP0::172.16.2.13::INSTR')
    dmm = Keithley6500(resource)
    dmm.open()

    print(dmm.idn())
    
    ## set Remote Lock On
    dmm.setRemoteLock()
    
    dmm.beeperOff()

    # Set display messages
    dmm.setDisplayMessage('Bottom Message', top=False)
    dmm.setDisplayMessage('Top Message', top=True)

    # Enable messages
    dmm.displayMessageOn()
    sleep(2.0)

    dmm.setDisplayMessage('New Top Message', top=True)
    dmm.setDisplayMessage('New Bottom Message', top=False)
    sleep(2.0)
    
    # Disable messages
    dmm.displayMessageOff()
    
    if not dmm.isInputOn(args.chan):
        dmm.inputOn()

    dmm.measureVoltage()
    dmm.setAutoZero(False)
    dmm.setAutoZero(False,function='CurrentDC')
    dmm.setAutoZero(True)
    dmm.setAutoZero(True,function='CurrentDC')
    #@@@#dmm.setMeasureFunction(function='CurrentAC')
    dmm.autoZeroOnce()

    dmm.setRelativeOffset()
    dmm.setRelativeOffset(0.0034567, function='CurrentDC')

    print('Relative Offsets: {:9.7g} V {:9.7g} A'.format(dmm.queryRelativeOffset(),dmm.queryRelativeOffset(function='CurrentDC')))

    dmm.setRelativeOffsetState(True)
    dmm.setRelativeOffsetState(True,function='CurrentDC')
    
    print('{:9.7g} V'.format(dmm.measureVoltage()))
    print('{:9.7g} V'.format(dmm.measureVoltage()))
    print('{:9.7g} V'.format(dmm.measureVoltage()))
    print('{:9.7g} V'.format(dmm.measureVoltage()))
    print('{:9.7g} V'.format(dmm.measureVoltage()))

    print('{:6.4g} A'.format(dmm.measureCurrent()))
    print('{:6.4g} A'.format(dmm.measureCurrent()))
    print('{:6.4g} A'.format(dmm.measureCurrent()))
    print('{:6.4g} A'.format(dmm.measureCurrent()))
    print('{:6.4g} A'.format(dmm.measureCurrent()))
    print('')
    
    dmm.setRelativeOffsetState(False,function='VoltageDC')
    dmm.setRelativeOffsetState(False)
    
    print('{:9.7g} V'.format(dmm.measureVoltage()))
    print('{:9.7g} V'.format(dmm.measureVoltage()))
    print('{:9.7g} V'.format(dmm.measureVoltage()))
    print('{:9.7g} V'.format(dmm.measureVoltage()))
    print('{:9.7g} V'.format(dmm.measureVoltage()))

    print('{:6.4g} A'.format(dmm.measureCurrent()))
    print('{:6.4g} A'.format(dmm.measureCurrent()))
    print('{:6.4g} A'.format(dmm.measureCurrent()))
    print('{:6.4g} A'.format(dmm.measureCurrent()))
    print('{:6.4g} A'.format(dmm.measureCurrent()))

    ## turn off the channel
    dmm.inputOff()

    dmm.beeperOn()

    ## return to LOCAL mode
    dmm.setLocal()
    
    dmm.close()
