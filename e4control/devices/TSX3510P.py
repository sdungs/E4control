# -*- coding: utf-8 -*-

from .device import Device


class TSX3510P(Device):

    def __init__(self, connection_type, host, port):
        super(TSX3510P, self).__init__(connection_type=connection_type, host=host, port=port)

    def userCmd(self, cmd):
        print('user cmd: %s' % cmd)
        return self.ask(cmd)

    def initialize(self):
        pass

    def setVoltageLimit(self, fValue):
        self.write('OVP %f' % fValue)

    def getVoltageLimit(self):
        sOVP = self.ask('OVP?')
        return float(sOVP[4:])

    def setVoltage(self, fValue):
        self.write('V %0.2f' % fValue)

    def setCurrent(self, fValue):
        self.write('I %0.2f' % fValue)

    def getVoltage(self):
        sV = self.ask('VO?')
        return float(sV[:sV.find('V')])

    def getVoltageSet(self):
        sV = self.ask('V?')
        return float(sV[2:])

    def getCurrent(self):
        sI = self.ask('IO?')
        return float(sI[:sI.find('A')])

    def getCurrentSet(self):
        sI = self.ask('I?')
        return float(sI[2:])

    def getPower(self):
        sP = self.ask('POWER?')
        return float(sP[:sP.find('W')])

    def setOutput(self, bValue, iChannel=-1):
        if bValue:
            self.write('OP 1')
        else:
            self.write('OP 0')

    def output(self, show=True):
        #self.setOutput(False)
        bOutput = None
        fVlim = self.getVoltageLimit()
        fVoltage = self.getVoltage()
        fCurrent = self.getCurrent()
        fPower = self.getPower()
        if show:
            print('TSX3510P:')
            if bOutput == '1':
                print('Output' + '\t' + '\033[32m ON \033[0m')
            else:
                print('Output' + '\t' + '\033[31m OFF \033[0m')
            print('Voltage = %0.1fV' % fVoltage + '\t' + 'Current = %0.3fA' % fCurrent)
            print('OVP = %0.1fV' % fVlim + '\t' + 'Power = %0.1fW' % fPower)
        values = [str(bOutput), str(fVlim), str(fVoltage), str(fCurrent), str(fPower)]
        header = ['Output', 'OVP[V]', 'U[V]', 'I[A]', 'P[W]']
        return([header, values])

    def interaction(self):
        print('1: enable Output')
        print('2: set OVP')
        print('3: set Voltage')
        print('4: set Current')
        x = input('Number? \n')
        while x != '1' and x != '2' and x != '3' and x != '4':
            x = input('Possible Inputs: 1,2,3 or 4! \n')
        if x == '1':
            bO = input('Please enter ON or OFF! \n')
            if bO == 'ON' or bO == 'on' or bO == '1':
                self.setOutput(True)
            elif bO == 'OFF' or bO == 'off' or bO == '0':
                self.setOutput(False)
            else:
                pass
        elif x == '2':
            sOVP = input('Please enter new OVP in V\n')
            self.setVoltageLimit(float(sOVP))
        elif x == '3':
            sV = input('Please enter new Voltage in V\n')
            self.setVoltage(float(sV))
        elif x == '4':
            sI = input('Please enter new Current in A\n')
            self.setCurrent(float(sI))
