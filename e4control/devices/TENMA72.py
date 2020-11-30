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
        sleep(0.3)
        return self.read()

    def userCmd(self, cmd):
        return self.ask(cmd)

    def initialize(self):
        self.outputEnabled = self.getOutput()

    def setOutput(self, bValue, iChannel=-1):
        self.write('OUT{:d}'.format(bValue))
        self.outputEnabled = bValue
        pass

    def getOutput(self, secondAttempt=False, iChannel=-1):
        answ = self.ask('STATUS?')
        if answ == 'Q':
            self.outputEnabled = True
        elif answ == '\x10':
            self.outputEnabled = False
        elif answ == 'P':
            self.outputEnabled = True
            sleep(0.2)
            curr = self.getCurrent()
            print('Current Limit reached! In constant current mode with I = {:.2f} A'.format(curr))
        elif not answ:
            if secondAttempt:
                return None
            print('Output-mode unknown! Asking again.') # known bug that the status query needs a second attempt.
            self.getOutput(True)
        return self.outputEnabled

    def reachedCurrentLimit(self, iChannel=-1):
        answ = self.ask('STATUS?')
        if not answ:
            self.reachedCurrentLimit()
        elif answ == 'P':
            return True
        elif answ == 'Q' or '\x10':
            return False

    def enableOCP(self, bValue, iChannel=-1):
        self.write('OCP{:d}'.format(bValue))
        # if OCP is active, the output will disabled in case the current limit is reached
        pass

    def getSetCurrent(self, iChannel=-1):
        return float(self.ask('ISET1?'))

    def getCurrent(self, iChannel=-1):
        return float(self.ask('IOUT1?'))

    def measCurrent(self, iChannel=-1):
        return float(self.ask('IOUT1?'))

    def setCurrent(self, fValue, iChannel=-1):
        self.write('ISET1:{:.3f}'.format(fValue))
        pass

    def setVoltage(self, fValue, iChannel=-1):
        self.write('VSET1:{:.2f}'.format(fValue))
        pass

    def getSetVoltage(self, iChannel=-1):
        return float(self.ask('VSET1?'))

    def getVoltage(self, iChannel=-1):
        return float(self.ask('VOUT1?'))

    def measVoltage(self, iChannel=-1):
        return float(self.ask('VOUT1?'))

    def output(self, show=True):
        bOutput = bool(self.outputEnabled)
        fVoltage = self.measVoltage()
        sleep(0.2)
        fCurrent = self.measCurrent()
        sValues = []
        if show:
            self.printOutput('TENMA72-xxxx:')
            if bOutput:
                self.printOutput('Output: \t \033[32m ON \033[0m')
                bReachedCurrLimit = self.reachedCurrentLimit()
            else:
                self.printOutput('Output: \t \033[31m OFF \033[0m')
                bReachedCurrLimit = False
            if bReachedCurrLimit:
                self.printOutput('Voltage = \033[31m{:0.2f} V\033[0m \t Current = \033[31m{:0.3f} A\033[0m'.format(fVoltage, fCurrent))
            else:
                self.printOutput('Voltage = {:0.32} V \t Current = {:0.3f} A'.format(fVoltage, fCurrent))
        sValues = [str(bOutput), str(fVoltage), str(fCurrent)]
        sHeader = ['Output', 'U[V]', 'I[A]']
        return([sHeader, sValues])

    def interaction(self, gui=False):
        if gui:
            device_dict = {
			'channel': 4,
			'toogleOutput': True,
			'setVoltage': True,
			'setCurrent': True,
			'enableOCP': True,
			}
            return device_dict
        else:
            print('1: enable Output')
            print('2: set Voltage')
            print('3: set Current')
            print('4: enable OCP')
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
                sV = input('Please enter new Voltage in V\n')
                self.setVoltage(float(sV))
            elif x == '3':
                sI = input('Please enter new Current in A\n')
                self.setCurrent(float(sI))
            elif x == '4':
                bOCP = input('Please enter ON or OFF! \n')
                if bOCP == 'ON' or bOCP == 'on' or bOCP == '1':
                    self.enableOCP(True)
                elif bOCP == 'OFF' or bOCP == 'off' or bOCP == '0':
                    self.enableOCP(False)
                else:
                    pass
