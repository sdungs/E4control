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
    def enablePower(self, bValue):
        self.write('OUTP:GEN {}'.format(bValue))

    def getEnablePower(self):
        return self.ask('OUTP:GEN?')

    #Output for individual channels
    def enableOutput(self, iOutput, bValue):
        self.write('INST OUT {}'.format(iOutput))
        self.write('OUTP {}'.format(bValue))

    def getEnableOutput(self, iOutput):
        self.write('INST OUT {}'.format(iOutput))
        return self.ask('OUTP?')

    #Over voltage protection
    def setVoltageLimit(self, iOutput, fValue):
        self.write('INST OUT {}'.format(iOutput))
        self.write('VOLT:PROT {}'.format(fValue))

    def getVoltageLimit(self, iOutput):
        self.write('INST OUT {}'.format(iOutput))
        return float(self.ask('VOLT:PROT?'))

    #Nominal voltage to apply
    def setVoltage(self, iOutput, fValue):
        self.write('INST OUT {}'.format(iOutput))
        self.write('VOLT {}'.format(fValue))

    def getVoltage(self, iOutput):
        self.write('INST OUT {}'.format(iOutput))
        return float(self.ask('VOLT?'))

    def measVoltage(self, iOutput):
        self.write('INST OUT {}'.format(iOutput))
        return float(self.ask('MEAS:VOLT?'))

    #Current (limit)
    def setCurrent(self, iOutput, fValue):
        self.write('INST OUT {}'.format(iOutput))
        self.write('CURR {}'.format(fValue))

    def getCurrent(self, iOutput):
        self.write('INST OUT {}'.format(iOutput))
        return float(self.ask('CURR?'))

    def measCurrent(self, iOutput):
        self.write('INST OUT {}'.format(iOutput))
        return float(self.ask('MEAS:CURR?'))


    def output(self, show=True):
        bPower = []
        fVoltage = []
        fCurrent = []
        sValues = []
        if show:
            print('HMP4040:')
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
                    print('CH {}: \t \033[32m ON \033[0m'.format(i))
                else:
                    print('CH {}: \t \033[31m OFF \033[0m'.format(i))
                print('Voltage = {:0.1f}V \t Current = {:0.3f}A'.format(b,c))
            sValues.append(str(a))
            sValues.append(str(b))
            sValues.append(str(c))
            i += 1
        sHeader = ['CH1', 'U1[V]', 'I1[A]', 'CH2', 'U2[V]', 'I2[A]', 'CH3', 'U3[V]', 'I3[A]', 'CH4', 'U4[V]', 'I4[A]']
        return([sHeader, sValues])

    def interaction(self):
        sChannel = input('Choose channel! \n')
        while sChannel != '1' and sChannel != '2' and sChannel != '3' and sChannel != '4':
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
            if bO == 'ON' or bO == 'on':
                self.enableOutput(iChannel, True)
            elif bO == 'OFF' or bO == 'off':
                self.enableOutput(iChannel, False)
            else:
                pass
        elif x == '2':
            sVoltage = input('Please enter new Voltage in V for CH {}\n'.format(iChannel))
            self.setVoltage(iChannel, float(sVoltage))
        elif x == '3':
            sCurrent = input('Please enter new Current in A for CH {}\n'.format(iChannel))
            self.setCurrent(iChannel, float(sCurrent))
