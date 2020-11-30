# -*- coding: utf-8 -*-

from .device import Device


class HMP4040(Device):

    def __init__(self, connection_type, host, port):
        super(HMP4040, self).__init__(connection_type=connection_type, host=host, port=port)

    def userCmd(self, cmd):
        print('user cmd: {}'.format(cmd))
        return self.ask(cmd)

    def initialize(self):
        pass

    #Global power (=OUTPUT button on PS)
    def enablePower(self, bValue, iChannel):
        self.write('OUTP:GEN {0:d}'.format(bValue))

    def getEnablePower(self):
        return self.ask('OUTP:GEN?')

    #Output for individual channels
    def setOutput(self, bEnable, iChannel):
        self.write('INST OUT{}'.format(iChannel))
        self.write('OUTP {:d}'.format(bEnable))

    def getOutput(self, iChannel):
        self.write('INST OUT{}'.format(iChannel))
        return self.ask('OUTP?')

    def enableOutput(self, iChannel):
        self.setOutput(True, iChannel)

    def disableOutput(self, iChannel):
        self.setOutput(False, iChannel)

    #Over voltage protection
    def setVoltageLimit(self, fValue, iChannel):
        self.write('INST OUT{}'.format(iChannel))
        self.write('VOLT:PROT {}'.format(fValue))

    def getVoltageLimit(self, iChannel):
        self.write('INST OUT {}'.format(iChannel))
        return float(self.ask('VOLT:PROT?'))

    #Nominal voltage to apply
    def setVoltage(self, fValue, iChannel):
        self.write('INST OUT{}'.format(iChannel))
        self.write('VOLT {}'.format(fValue))

    def getVoltage(self, iChannel):
        self.write('INST OUT{}'.format(iChannel))
        return float(self.ask('VOLT?'))

    def measVoltage(self, iChannel):
        self.write('INST OUT{}'.format(iChannel))
        return float(self.ask('MEAS:VOLT?'))

    #Current (limit)
    def setCurrent(self, fValue, iChannel):
        self.write('INST OUT{}'.format(iChannel))
        self.write('CURR {}'.format(fValue))

    def getCurrent(self, iChannel):
        self.write('INST OUT{}'.format(iChannel))
        return float(self.ask('CURR?'))

    def measCurrent(self, iChannel):
        self.write('INST OUT{}'.format(iChannel))
        return float(self.ask('MEAS:CURR?'))


    def output(self, show=True):
        bPower = []
        fVoltage = []
        fCurrent = []
        sValues = []
        if show:
            self.printOutput('HMP4040:')
        i = 1
        while i <= 4:
            a = self.getEnableOutput(i)
            b = self.measVoltage(i)
            c = self.measCurrent(i)
            bPower.append(a)
            fVoltage.append(b)
            fCurrent.append(c)
            if show:
                if a == '1':
                    self.printOutput('CH {}: \t \033[32m ON \033[0m'.format(i))
                else:
                    self.printOutput('CH {}: \t \033[31m OFF \033[0m'.format(i))
                self.printOutput('Voltage = {:0.1f}V \t Current = {:0.3f}A'.format(b,c))
            sValues.append(str(a))
            sValues.append(str(b))
            sValues.append(str(c))
            i += 1
        sHeader = ['CH1', 'U1[V]', 'I1[A]', 'CH2', 'U2[V]', 'I2[A]', 'CH3', 'U3[V]', 'I3[A]', 'CH4', 'U4[V]', 'I4[A]']
        return([sHeader, sValues])

    def interaction(self, gui=False):
        if gui:
            device_dict = {
            'channel': 4,
            'toogleOutput': True,
            'setVoltage': True,
            'setCurrent': True,
            }
            return device_dict
        else:
            sChannel = input('Choose channel! \n')
            while not sChannel in ['1', '2', '3', '4']:
                sChannel = input('Possible Channels: 1,2,3 or 4! \n')
            iChannel = int(sChannel)
            print('1: enable Output')
            print('2: set Voltage')
            print('3: set Current')
            x = input('Number? \n')
            while x != '1' and x != '2' and x != '3':
                x = input('Possible Inputs: 1,2 or 3! \n')
            if x == '1':
                bO = input('Please enter ON or OFF! \n')
                if bO == 'ON' or bO == 'on' or bO == '1':
                    self.setOutput(True, iChannel)
                elif bO == 'OFF' or bO == 'off' or bO == '0':
                    self.setOutput(False, iChannel)
                else:
                    pass
            elif x == '2':
                sVoltage = input('Please enter new Voltage in V for CH {}\n'.format(iChannel))
                self.setVoltage(float(sVoltage), iChannel)
            elif x == '3':
                sCurrent = input('Please enter new Current in A for CH {}\n'.format(iChannel))
                self.setCurrent(float(sCurrent), iChannel)
