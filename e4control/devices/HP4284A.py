# -*- coding: utf-8 -*-

from .device import Device


class HP4284A(Device):
    mode = None

    def __init__(self, connection_type, host, port):
        super(HP4284A, self).__init__(connection_type=connection_type, host=host, port=port)
        self.mode = self.getMeasurementMode()

    def userCmd(self, cmd):
        print('user cmd: %s' % cmd)
        return self.ask(cmd)

    def initialize(self):
        # self.write('*RST')
        self.write(':DISP:PAGE MEAS')
        self.write(':FUNC:IMP:RANG:AUTO ON')
        self.write(':BIAS:STAT OFF')
        self.write(':BIAS:VOLT 0')
        self.write(':TRIG:DEL MIN')
        self.write(':INIT:CONT ON')
        self.write(':FORM ASC')
        self.write(':MEM:DIM DBUF,1')
        self.write(':FUNC:DEV1:MODE OFF')
        self.write(':FUNC:DEV2:MODE OFF')
        self.write(':MEM:CLE DBUF')
        self.write(':CORR:LENG 1')
        self.write(':AMPL:ALC ON')
        self.setFrequency(10000)
        self.setVoltage(0.050)
        self.setMeasurementMode('CPRP')
        self.setTriggerMode('BUS')
        self.setIntegrationTimeAndAveragingRate('LONG', 1)

    def getValues(self):  # general function for all measurement modes
        sV = self.ask('*TRG').split(',')
        fC = float(sV[0])
        fR = float(sV[1])
        return [fC, fR]

    def getR(self):  # specific function to get resistance if suitable mode
        if 'R' and not ('Y' or 'Z') in self.mode:
            fV = self.getValues()
            return fV[1]
        else:
            print('Cannot get resistance. Wrong measurement mode? Mode is {}'.format(self.mode))
            pass

    def getC(self):  # sepcific function to get capacitance if in suitable mode
        if self.mode[0] is 'C':
            fV = self.getValues()
            return fV[0]
        else:
            print('Cannot get capacitance. Wrong measurement mode? Mode is {}'.format(self.mode))
            pass

    def setFrequency(self, fFreq):
        self.write(':FREQ %f' % fFreq)

    def getFrequency(self):
        return float(self.ask(':FREQ?'))

    def setOpenCorrection(self, bOC):
        if bOC:
            self.write(':CORR:OPEN:STAT ON')
        else:
            self.write(':CORR:OPEN:STAT OFF')

    def setLoadCorrection(self, bLC):
        if bLC:
            self.write(':CORR:LOAD:STAT ON')
        else:
            self.write(':CORR:LOAD:STAT OFF')

    def setShortCorrection(self, bSC):
        if bSC:
            self.write(':CORR:SHOR:STAT ON')
        else:
            self.write(':CORR:SHOR:STAT OFF')

    def setMeasurementMode(self, sMode):
        if sMode in ['CPD', 'CPQ', 'CPG', 'CPRP', 'CSD', 'CSQ', 'CSRS',  # capacitance related modes
                     'LPQ', 'LPD', 'LPRP', 'LSD', 'LSQ', 'LSRS',         # inductance related modes
                     'RX', 'ZTD', 'ZTR', 'GB', 'YTD', 'YTR']:            # impedance /addmitance related modes
            self.write(':FUNC:IMP {}'.format(sMode))
            self.mode = sMode
        else:
            print(f'Setting measurement mode failed! Unkown mode.')

    def getMeasurementMode(self):
        return(self.ask(':FUNC:IMP?'))

    def setTriggerMode(self, sMode):
        if (sMode == 'INT'):
            self.write(':TRIG:SOUR INT')
        elif (sMode == 'EXT'):
            self.write(':TRIG:SOUR EXT')
        elif (sMode == 'BUS'):
            self.write(':TRIG:SOUR BUS')
        elif (sMode == 'HOLD'):
            self.write(':TRIG:SOUR HOLD')
        else:
            print('Setting trigger mode failed!')

    def setVoltage(self, fVolt):
        self.write(':VOLT %f V' % fVolt)

    def getVoltage(self):
        return(self.ask(':VOLT?'))

    def setIntegrationTimeAndAveragingRate(self, sType, iAR):
        if (sType == 'SHOR'):
            self.write(':APER SHOR,%i' % iAR)
        elif (sType == 'MED'):
            self.write(':APER MED,%i' % iAR)
        elif (sType == 'LONG'):
            self.write(':APER LONG,%i' % iAR)
        else:
            print('Setting ITAR failed!')

    def getIntegrationTimeAndAveragingRate(self):
        return(self.ask(':APER?'))

    def reset(self):
        self.write('*RST')

    def output(self, show=True):
        self.printOutput('HP4284A:')
        self.printOutput('no output')
        return([[], []])

    def interaction(self, gui=False):
        if gui:
            device_dict = {
                'pass': True,
            }
            return device_dict
        else:
            print('Nothing to do...')

