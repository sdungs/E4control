# -*- coding: utf-8 -*-

from .device import Device
from time import sleep


class TENMA72(Device):
    outputEnabled = None

    def __init__(self, connection_type, host, port):
        super(TENMA72, self).__init__(connection_type=connection_type, host=host, port=port)
        self.trm = '\n'.encode()
        self.initialize()

    def write(self, cmd):
        self.com.write(cmd.encode())

    def read(self):
        if self.connection_type == 'usb':
            return self.com.read_all().decode()
        elif self.connection_type == 'serial':
            return self.com.read()
        else:
            pass

    def ask(self, cmd):
        self.write(cmd)
        sleep(0.1)
        return self.read()

    def userCmd(self, cmd):
        return self.ask(cmd)

    def initialize(self):
        self.outputEnabled = self.getEnableOutput()

    def enableOutput(self, bValue):
        self.write('OUT{:d}'.format(bValue))
        self.outputEnabled = bValue
        pass

    def getEnableOutput(self):
        answ = self.ask('STATUS?')
        if answ == 'Q':
            self.outputEnabled = True
        elif answ == '\x10':
            self.outputEnabled = False
        else:
            self.output = None
            print('Output-mode unknown!')
        return self.outputEnabled

    def setCurrentLimit(self, fValue, bOCP=False):
        self.write('ISET1:{:.3f}'.format(fValue))
        self.write('OCP{:d}'.format(bOCP))
        # if OCP is active, the output will disabled in case the current limit is reached
        pass

    def getSetCurrent(self):
        return float(self.ask('ISET1?'))

    def getCurrent(self):
        return float(self.ask('IOUT1?'))

    def measCurrent(self):
        return float(self.ask('IOUT1?'))

    def setCurrent(self, fValue):
        self.write('ISET1:{:.3f}'.format(fValue))
        pass

    def setVoltage(self, fValue):
        self.write('VSET1:{:.2f}'.format(fValue))
        pass

    def getSetVoltage(self):
        return float(self.ask('VSET1?'))

    def getVoltage(self):
        return float(self.ask('VOUT1?'))

    def measVoltage(self):
        return float(self.ask('VOUT1?'))

    def output(self, show=True):
        bOutput = bool(self.outputEnabled)
        fVoltage = self.measVoltage()
        fCurrent = self.measCurrent()
        sValues = []
        if show:
            self.printOutput('TENMA72-xxxx:')
            if bOutput:
                self.printOutput('Output: \t \033[32m ON \033[0m')
            else:
                self.printOutput('Output: \t \033[31m OFF \033[0m')
            self.printOutput('Voltage = {:0.2f}V \t Current = {:0.3f}A'.format(fVoltage, fCurrent))
        sValues = [str(bOutput), str(fVoltage), str(fCurrent)]
        sHeader = ['Output', 'U[V]', 'I[A]']
        return([sHeader, sValues])

    def interaction(self):
        print('1: enable Output')
        print('2: set OCP')
        print('3: set Voltage')
        print('4: set Current')
        x = input('Number? \n')
        while x != '1' and x != '2' and x != '3' and x != '4':
            x = input('Possible Inputs: 1,2,3 or 4! \n')
        if x == '1':
            bO = input('Please enter ON or OFF! \n')
            if bO == 'ON' or bO == 'on' or bO == '1':
                self.enableOutput(True)
            elif bO == 'OFF' or bO == 'off' or bO == '0':
                self.enableOutput(False)
            else:
                pass
        elif x == '2':
            sOCP = input('Please enter new OCP in A\n')
            self.setCurrentLimit(float(sOCP))
        elif x == '3':
            sV = input('Please enter new Voltage in V\n')
            self.setVoltage(float(sV))
        elif x == '4':
            sI = input('Please enter new Current in A\n')
            self.setCurrent(float(sI))
