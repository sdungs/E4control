# -*- coding: utf-8 -*-

from .device import Device


class TTI2(Device):

    def __init__(self, connection_type, host, port):
        super(TTI2, self).__init__(connection_type=connection_type, host=host, port=port)

    def userCmd(self, cmd):
        print('user cmd: %s' % cmd)
        return self.ask(cmd)

    def initialize(self):
        pass

    def setVoltageLimit(self, iOutput, fValue):
        self.write('OVP%i %f' % (iOutput, fValue))

    def getVoltageLimit(self, iOutput):
        sOVP = self.ask('OVP%i?' % iOutput)
        return float(sOVP)

    def setCurrentLimit(self, iOutput, fValue):
        self.write('OCP%i %f' % (iOutput, fValue))

    def getCurrentLimit(self, iOutput):
        sOCP = self.ask('OCP%i?' % iOutput)
        return float(sOCP)

    def setVoltage(self, iOutput, fValue):
        self.write('V%i %0.2f' % (iOutput, fValue))

    def setCurrent(self, iOutput, fValue):
        self.write('I%i %0.3f' % (iOutput, fValue))

    def getVoltage(self, iOutput):
        sV = self.ask('V%iO?' % iOutput)
        return float(sV[:sV.find('V')])

    def getVoltageSet(self, iOutput):
        sV = self.ask('V%i?' % iOutput)
        return float(sV[3:])

    def getCurrent(self, iOutput):
        sI = self.ask('I%iO?' % iOutput)
        return float(sI[:sI.find('A')])

    def getCurrentSet(self, iOutput):
        sI = self.ask('I%i?' % iOutput)
        return float(sI[3:])

    def setOutput(self, bEnable, iChannel):
        if bValue:
            self.write('OP{:d} 1'.format(iChannel))
        else:
            self.write('OP{:d} 0'.format(iChannel))

    def getOutput(self, iChannel):
        iEO = self.ask('OP{}?'.format(iChannel))
        return int(iEO)

    def output(self, show=True):
        bPower = []
        fVoltage = []
        fCurrent = []
        sValues = []
        if show:
            self.printOutput('TTI2:')
        i = 1
        while i <= 2:
            a = self.getOutput(i)
            b = self.getVoltage(i)
            c = self.getCurrent(i)
            d = self.getVoltageSet(i)
            e = self.getCurrentSet(i)
            bPower.append(a)
            fVoltage.append(b)
            fCurrent.append(c)
            if show:
                if a == 1:
                    self.printOutput('CH {}: \t \033[32m ON \033[0m'.format(i))
                else:
                    self.printOutput('CH {}: \t \033[31m OFF \033[0m'.format(i))
                self.printOutput('Voltage: {:0.2f}V \t Set = {:0.2f}V'.format(b, d))
                self.printOutput('Current: {:0.3f}A \t Set = {:0.3f}A'.format(c, e))
            sValues.append(str(a))
            sValues.append(str(b))
            sValues.append(str(c))
            i += 1
        sHeader = ['CH1', 'U1[V]', 'I1[A]', 'CH2', 'U2[V]', 'I2[A]']
        return ([sHeader, sValues])

    def interaction(self, dui=False):
        if gui:
            device_dict = {
                'toogleOutput': True,
                'setVoltage': True,
                'setCurrent': True,
            }
            return device_dict
        else:
            sChannel = input('Choose channel! \n')
            while sChannel != '1' and sChannel != '2':
                sChannel = input('Possible Channels: 1 or 2! \n')
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
                self.setVoltage(iChannel, float(sVoltage))
            elif x == '3':
                sCurrent = input('Please enter new Current in A for CH {}\n'.format(iChannel))
                self.setCurrent(iChannel, float(sCurrent))
