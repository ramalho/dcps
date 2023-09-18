#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Emmanuel Blot <emmanuel.blot@free.fr>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Neotion nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL NEOTION BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from binascii import hexlify
from dataclasses import dataclass
import argparse

import PowerTestBoard
import BK9115
import Keithley6500
import RigolDL3000

import numpy as np
import csv

from sys import modules, stdout, exit
import logging
from os import environ, path
from datetime import datetime
from time import sleep


#@@@#ftdi_url = 'ftdi://ftdi:4232h/1'
ftdi_url_const = 'ftdi://ftdi:4232:FTK1RRYC/1'


def handleFilename(fname, ext, unique=True, timestamp=True):

    # If extension exists in fname, strip it and add it back later
    # after handle versioning
    ext = '.' + ext                       # don't pass in extension with leading '.'
    if (fname.endswith(ext)):
        fname = fname[:-len(ext)]

    # Make sure filename has no path components, nor ends in a '/'
    if (fname.endswith('/')):
        fname = fname[:-1]
        
    pn = fname.split('/')
    fname = pn[-1]
        
    # Assemble full pathname so files go to ~/Downloads    if (len(pp) > 1):
    pn = environ['HOME'] + "/Downloads"
    fn = pn + "/" + fname

    if (timestamp):
        # add timestamp suffix
        fn = fn + '-' + datetime.now().strftime("%Y%0m%0d-%0H%0M%0S")

    suffix = ''
    if (unique):
        # If given filename exists, try to find a unique one
        num = 0
        while(path.isfile(fn + suffix + ext)):
            num += 1
            suffix = "-{}".format(num)

    fn += suffix + ext

    #@@@#print("handleFilename(): Filename '{}'".format(fn))
    
    return fn

def dataSaveCSV(filename, rows, header=None, meta=None):
    """
    filename - base filename to store the data

    rows     - expected to be a list of columns to write and can be any number of columns
               the first set of columns should be the indepedant variables
    
    header   - a list of header strings, one for each column of data - set to None for no header

    meta     - a list of meta data for data - optional and not used by this function - only here to be like other dataSave functions

    """

    nLength = len(rows)

    #@@@#print('Writing data to CSV file "{}". Please wait...'.format(filename))

    # Save data values to CSV file.
    #
    # Open file for output. Only output x & y for simplicity. User
    # will have to copy paste the meta data printed to the
    # terminal
    #@@@#print("dataSaveCSV(): Filename '{}'".format(filename))
    myFile = open(filename, 'w')
    with myFile:
        writer = csv.writer(myFile, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
        if header is not None:
            writer.writerow(header)

        writer.writerows(rows)

    # return number of entries written
    return nLength


def dataSaveNPZ(filename, rows, header=None, meta=None):
    """
    filename - base filename to store the data

    rows     - expected to be a list of columns to write and can be any number of columns
               the first set of columns should be the indepedant variables
    
    header   - a list of header strings, one for each column of data - set to None for no header

    meta     - a list of meta data for data

    A NPZ file is an uncompressed zip file of the arrays x, y and optionally header and meta if supplied. 
    To load and use the data from python:

    import numpy as np
    header=None
    meta=None
    with np.load(filename) as data:
        rows = data['rows']
        if 'header' in data.files:
            header = data['header']
        if 'meta' in data.files:
            meta = data['meta']

    """

    nLength = len(rows)

    #@@@#print('Writing data to Numpy NPZ file "{}". Please wait...'.format(filename))

    arrays = {'rows': rows}
    if (header is not None):
        arrays['header']=header
    if (meta is not None):
        arrays['meta']=meta
    np.savez(filename, **arrays)

    # return number of entries written
    return nLength

def poweronOLD():
    """enable the power output on the BK9115 power supply.
    """

    resource = environ.get('BK9115_USB', 'USB0::INSTR')
    bkps = BK9115.BK9115(resource)
    bkps.open()

    #@@@#print(bkps.idn())

    # IMPORTANT: 9115 requires Remote to be set or else commands are ignored
    bkps.setRemote()
    
    ## set Remote Lock On
    #bkps.setRemoteLock()
    
    bkps.beeperOff()

    # BK Precision 9115 has a single channel, so force chan to be 1
    chan = 1

    bkps.outputOn()
    #print('BK9115 Values:   {:6.4f} V  {:6.4f} A'.
    #          format(bkps.measureVoltage(),
    #                 bkps.measureCurrent()))
    
    ## return to LOCAL mode
    bkps.setLocal()
    
    bkps.close()
    
def poweroffOLD():
    """Disable the BK 9115 DC power supply output.
    """

    resource = environ.get('BK9115_USB', 'USB0::INSTR')
    bkps = BK9115.BK9115(resource)
    bkps.open()

    # IMPORTANT: 9115 requires Remote to be set or else commands are ignored
    bkps.setRemote()
    
    # BK Precision 9115 has a single channel, so force chan to be 1
    chan = 1

    bkps.outputOff()
        
    ## return to LOCAL mode
    bkps.setLocal()
    
    bkps.close()

def setPowerValuesOLD(voltage,current,OVP=None,OCP=None):
    """Set the Voltage and Current values for the BK 9115 DC power supply output.

       voltage - floating point value to set voltage to
       current - floating point value to set current to
       OVP     - floating point value to set overvoltage protection to, or None to not set it
       OCP     - floating point value to set overcurrent protection to, or None to not set it
    """

    resource = environ.get('BK9115_USB', 'USB0::INSTR')
    bkps = BK9115.BK9115(resource)
    bkps.open()

    # IMPORTANT: 9115 requires Remote to be set or else commands are ignored
    bkps.setRemote()
    
    # BK Precision 9115 has a single channel, so force chan to be 1
    chan = 1

    bkps.setVoltage(voltage)
    bkps.setCurrent(current)

    if OVP is not None:
        bkps.setVoltageProtection(OVP, delay=0.010)
        bkps.voltageProtectionOn()

    if OCP is not None:
        bkps.setCurrentProtection(OCP, delay=0.010)
        bkps.currentProtectionOn()

    ## return to LOCAL mode
    bkps.setLocal()
    
    bkps.close()

    return (voltage, current)

def setPowerValues(ps, voltage,current,OVP=None,OCP=None):
    """Set the Voltage and Current values for the power supply, ps

       ps      - power supply object
       voltage - floating point value to set voltage to
       current - floating point value to set current to
       OVP     - floating point value to set overvoltage protection to, or None to not set it
       OCP     - floating point value to set overcurrent protection to, or None to not set it
    """

    ps.setVoltage(voltage)
    ps.setCurrent(current)

    if OVP is not None:
        ps.setVoltageProtection(OVP, delay=0.010)
        ps.voltageProtectionOn()

    if OCP is not None:
        ps.setCurrentProtection(OCP, delay=0.010)
        ps.currentProtectionOn()

    return measurePowerValues(ps)


def measurePowerValuesOLD():
    """Measure the Voltage and Current values from the BK 9115 DC power supply output.
    """

    resource = environ.get('BK9115_USB', 'USB0::INSTR')
    bkps = BK9115.BK9115(resource)
    bkps.open()

    # IMPORTANT: 9115 requires Remote to be set or else commands are ignored
    bkps.setRemote()
    
    # BK Precision 9115 has a single channel, so force chan to be 1
    chan = 1

    voltage = bkps.measureVoltage()
    current = bkps.measureCurrent()
    
    #@@@#print('BK9115 Values:   {:6.4f} V  {:6.4f} A'.format(voltage,current))
            
    ## return to LOCAL mode
    bkps.setLocal()
    
    bkps.close()

    return (voltage, current)

def measurePowerValues(ps):
    """Measure the Voltage and Current values from the BK 9115 DC power supply output.
    """

    voltage = ps.measureVoltage()
    current = ps.measureCurrent()
    
    #@@@#print('BK9115 Values:   {:6.4f} V  {:6.4f} A'.format(voltage,current))
            
    return (voltage, current)

def instrumentInit(instr):
    # Reset
    instr.rst(wait=0.2)
    instr.cls(wait=0.2)

    #@@@#print(instr.idn())
    
    ## set Remote Lock On
    instr.setRemoteLock()

    ## turn off the beeper
    instr.beeperOff()

def instrumentStop(instr):
    instr.inputOff()
    instr.outputOff()
    instr.beeperOn()
    #@@@#instr.printAllErrors()    
    #@@@#instr.cls()
    
    ## return to LOCAL mode
    instr.setLocal()

def rangef(start, stop, step, ndigits):
    """Return a floating point range from start to stop, INCLUSIVE, using step. The values in the returned list are rounded to ndigits digits
    """
    
    n = int(round(((stop+step)-start)/step,0))
    return [round(a,ndigits) for a in np.linspace(start,stop,n)]
    #@@@#return [round(a,ndigits) for a in np.arange(round(start,ndigits),round(stop,ndigits)+round(step,ndigits),step)]
    
def_vins = rangef(10.8,13.2,0.1,1) # 10.8V to 13.2V by 0.1V
#@@@#def_vins = rangef(11.4,11.6,0.1,1) # 11.4V to 11.6V by 0.1V @@@
        
@dataclass(frozen=True)
class DCTestParam:
    upper: float                # upper output voltage so can set a range
    max_iin: float              # maximum input current (for setting power supply)
    ovp: float                  # value to set over voltage protection on power supply
    ocp: float                  # value to set over current protection on power supply
    vins: list                  # list of floats to set VIN (input voltage) to in sequence
    vin_wait: float             # number of seconds to wait after changing the input voltage before measuring data
    loads: list                 # list of floats to set load to in sequence
    load_wait: float            # number of seconds to wait after changing load before measuring data

DCTestParams = {
    '1V8-A': DCTestParam(upper=2.0,max_iin=5.1,ovp=16.1,ocp=7.5,vins=def_vins,vin_wait=2.5,loads=[0,0.02,0.04,0.06,0.08]+rangef(0.1,3.0,0.1,1),load_wait=2.5), # load: step 0.1A for 0-3A
    #@@@#'1V8-A': DCTestParam(upper=2.0,max_iin=5.1,ovp=16.1,ocp=7.5,vins=def_vins,vin_wait=3.0,loads=rangef(1.0,1.2,0.1,1),load_wait=3.0), # load: step 0.1A for 0-3A
}

def DCTest(PS,PTB,DMM,ELOAD,circuit,trials,param):

    print("Testing DC Characteristics by varying VIN and IOUT for '{}'".format(circuit))
    
    ## Make sure power supply is off at start
    PS.outputOff()

    instrumentInit(DMM)
    instrumentInit(ELOAD)

    ## Setup DMM for use
    DMM.setMeasureFunction('VoltageDC')
    DMM.setAutoZero(True)
    DMM.setIntegrationTime(14)
    DMM.setAsciiPrecision(8)
    DMM.setMeasureRange(param.upper)   # Set Range to be constant based on upper limit output voltage
    DMM.inputOn()

    ## Setup ELOAD for use
    #
    ## Make sure Electronic Load Input is OFF
    ELOAD.inputOff()    
    ELOAD.setFunction('current')   # Constant Current
    ELOAD.setSenseState(True)      # Enable Sense inputs

    ## Set for the first VIN in the sequence. Use params for other parameters
    setPowerValues(PS,param.vins[0],param.max_iin,OVP=param.ovp,OCP=param.ocp)
    PS.outputOn()
    sleep(2)                    # give some time to settle

    # save the starting voltage and current
    #
    # NOTE: Found that this varies by +/- 1 mA over 10.8V to 13.2V
    # VIN. So it does not matter VIN when measure this. It is close
    # enough for the expected range.
    startValues = measurePowerValues(PS) # voltage, current
    
    print(' BK9115 Start Values:     {:6.4f} V  {:6.4f} A'.format(*startValues))

    # Enable power supply output and give some time to settle
    PTB.powerEnable(PTB.circuits[circuit],True)
    sleep(2)

    #@@@#input("Press Enter to continue...") 

    
    # save the baseline voltage and current
    baseValues = measurePowerValues(PS) # voltage, current
    
    print(' BK9115 Baseline Values:  {:6.4f} V  {:6.4f} A'.format(*baseValues))

    ## Main Loop
    ## - Set VIN to next in the sequence 
    ##   - Enable/Disable Input of DL3031A and Set next current load
    ##   - measure BK9115 Voltage & Current
    ##   - subtract start current to get DC circuit current (estimated)
    ##   - measure DMM9500 Voltage & DL3031A (E-Load) Current
    ##   - compute Power In / Power Out as a percentage
    ##   - Save all values to data[]

    ## data will be an array of tuples to save the data
    data = []

    ## count number of trials
    trialsDone = 0
    
    try:
        for trial in range(0,trials):
            for vin in param.vins:
                # Change VIN to next in the sequence
                setPowerValues(ps,vin,param.max_iin)
                sleep(param.vin_wait)

                for load in param.loads:
                    ## - Enable Input of DL3031A, if non-0 load, and Set next current load
                    if (load == 0):
                        ELOAD.inputOff()
                        sleep(param.load_wait)
                    else:
                        if (not ELOAD.isInputOn()):
                            # If the Input is NOT enabled, then first set the load
                            # value to make sure it is not too high from a
                            # previous test. However, have noticed that sometimes
                            # input will enable at a low current anyway and ignore
                            # what it had been set to just recently. So still set
                            # the current after enabling the input.
                            ELOAD.setCurrent(load,wait=0.2)
                            ELOAD.inputOn()
                        ELOAD.setCurrent(load,wait=param.load_wait)

                    ## - measure BK9115 Voltage & Current
                    (psVoltage, psCurrent) = measurePowerValues(PS)

                    ## - subtract start current to get DC circuit current (estimated)
                    inVoltage = psVoltage
                    inCurrent = psCurrent - startValues[1]

                    ## - measure DMM9500 Voltage & DL3031A (E-Load) Current
                    outVoltage = DMM.measureVoltage()
                    outCurrent = ELOAD.measureCurrent()

                    ## - compute Power Out / Power In as a percentage
                    outPower = (outVoltage * outCurrent)
                    inPower  = (inVoltage * inCurrent)
                    efficiency = (outPower / inPower) * 100

                    ## - Add values to data
                    data.append([trial+1, vin, load, inVoltage, inCurrent, inPower, outVoltage, outCurrent, outPower, efficiency])
                    
                    print("   Trial: {:d} VIN: {:.03f}V Load: {:.03f}A  Power: {:.03f}/{:.03f} W  Eff: {:d} %".format(trial+1, vin, load, outPower, inPower, int(efficiency)))

                    #@@@#input("Press Enter to continue...")

            ## Indicate that the trial is complete
            trialsDone += 1
            print(" Trials Completed: {}".format(trialsDone))


    except KeyboardInterrupt:
        ## Use Ctrl-C to get out of test loop so can save data and return to close instruments
        print("Saving collected data and shutting down instruments. Please Wait ...")
        
    #@@@#print(data)

    ## Disable ELOAD
    ELOAD.inputOff()
    
    ## - Save all values
    header = ["Trial","Set VIN","Set Load","VIN (V)","IIN (A)","PIN (W)","VOUT (V)","IOUT (A)","POUT (W)","Efficiency (%)"]
    meta = ['DC Test', circuit, trialsDone]
    fnbase = "DC_Test_{}_t{:02d}".format(circuit,trialsDone)
    # Use NPZ files which write in under a second instead of bulky csv files
    if False:
        fn = handleFilename(fnbase, 'csv')
        dataLen = dataSaveCSV(fn, data, header, meta)
    else:
        fn = handleFilename(fnbase, 'npz')
        dataLen = dataSaveNPZ(fn, data, header, meta)
    print("Data Output {} points to file {}".format(dataLen,fn))
    
    ## Done - so turn off electronic load, board and power
    sleep(1)
    instrumentStop(ELOAD)
    instrumentStop(DMM)

    sleep(1)
    PTB.powerEnable(PTB.circuits[circuit],False)

    sleep(1)
    instrumentStop(PS)
    
def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

if __name__ == '__main__':
    #@@@#testmod(modules[__name__])

    ps  = BK9115.BK9115(environ.get('BK9115_USB', 'USB0::INSTR'))
    ptb = PowerTestBoard.PowerTestBoard(environ.get('FTDI_DEVICE', ftdi_url_const))
    dmm = Keithley6500.Keithley6500(environ.get('DMM6500_VISA', 'TCPIP0::172.16.2.13::INSTR'))
    eload = RigolDL3000.RigolDL3000(environ.get('DL3000_VISA', 'TCPIP0::172.16.2.13::INSTR'))
            
    parser = argparse.ArgumentParser(description='Run various tests on the Power Test Board and collect data')

    # Mutuall Exclusive tests - pick one an donly one
    mutex_grp = parser.add_mutually_exclusive_group(required=True)
    mutex_grp.add_argument('-e', '--dc_efficiency',  action='store_true', help='run the DC Power Efficiency test')
    mutex_grp.add_argument('-i', '--line_regulation', action='store_true', help='run the Line Regulation test')
    mutex_grp.add_argument('-o', '--load_regulation', action='store_true', help='run the Load Regulation test')

    #@@@#parser.add_argument('-t', '--trials', action='store', type=check_positive, default=1, help='number of times to run the test')
    parser.add_argument('-t', '--trials', metavar='trials', action='store', type=int, default=1, choices=range(1,21), help='number of times to run the test')
    parser.add_argument('list_of_circuits', metavar='circuits', type=ptb.validate_circuits, nargs='*', help='a list of circuits - or all if omitted')
    
    args = parser.parse_args()

    ## Make sure power supply is off at start
    ps.open()
    instrumentInit(ps)
    ps.outputOff(channel=1)

    ## Open DMM and Eload
    dmm.open()
    eload.open()

    circuit_list = args.list_of_circuits

    # If no list given, then use all circuits
    if len(circuit_list) <= 0:
        circuit_list = ptb.circuits.keys()

    for circ in circuit_list:
        if (args.dc_efficiency or args.line_regulation or args.load_regulation):
            ## All three tests collect the same data by varying
            ## VIN and IOUT and collecting VIN, IIN, VOUT,
            ## IOUT. This is all the data needed to plot the
            ## desired results for these three tests and makes the
            ## data more robust as it is collected over these
            ## primary variables.
            DCTest(ps, ptb, dmm, eload, circ, args.trials, DCTestParams[circ])
        else:
            raise ValueError("A test was not selected with the command line arguments")

    ## Close PS, DMM and Eload
    eload.close()
    dmm.close()
    ps.close()

