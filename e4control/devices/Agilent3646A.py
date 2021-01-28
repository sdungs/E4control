# -*- coding: utf-8 -*-

from time import sleep

from .device import Device
import warnings


class Agilent3646A(Device):
    rampSpeed_step = 10
    rampSpeed_delay = 1  # s

    def __init__(self, connection_type, host, port):
        super(Agilent3646A, self).__init__(
            connection_type=connection_type, host=host, port=port)

    def initialize(self):
    	self.write('SYST:REM')
    	self.setVoltageRange('MAX', 1)
    	self.setVoltageRange('MAX', 2)
    	pass

    def setVoltageRange(self, sRange, iChannel):
        self.write(f'INST OUT{iChannel}')
        if sRange == 'MAX':
            self.write('VOLT:RANG MAX')
        elif sRange == 'MIN':
            self.write('VOLT:RANG MIN')
        elif sRange == 'AUTO':
            self.write('VOLT:RANG:AUTO ON')
        else:
            print('Unknown Range')

    def setVoltageLimit(self, fVlim, iChannel):
        self.write(f'INST OUT{iChannel}')
        self.write(f'VOL :PROT {fVlim}')

    def setCurrent(self, fIset, iChannel):
        self.write(f'INST OUT{iChannel}')
        self.write( 'CURR {fIset}')

    def setVoltage(self, fVset, iChannel):
        self.write(f'INST OUT{iChannel}')
        self.write( 'VOLT {fVset}')

    def setOutput(self, bEnable, iChannel):
        self.write(f'INST OUT{iChannel}')
        if bEnable:
            self.write('OUTPUT ON')
        else:
            self.write('OUTPUT OFF')

    def getOutput(self, iChannel):
        self.write(f'INST OUT{iChannel}')
        return self.ask('OUTPUT?')

    def getVoltage(self, iChannel):
        self.write(f'INST OUT{iChannel}')
        sValues = self.ask('VOLT?')
        if ',' not in sValues:
            sValues = self.ask('VOLT?')
            if ',' not in sValues:
                return 'error'
        return float(sValues.split(',')[0])

    def getCurrent(self, iChannel):
        self.write(f'INST OUT{iChannel}')
        sValues = self.ask('CURR?')
        return float(sValues.split(',')[1])

    def getVoltageLimit(self, iChannel):
        self.write(f'INST OUT{iChannel}')
        return float(self.ask('VOLT:PROT?'))

    def setRampSpeed(self, iRampSpeed, iDelay):
        if iRampSpeed < 1 or iRampSpeed > 255:
            print('Set RampSpeed size is out of range!')
        else:
            self.rampSpeed_step = iRampSpeed
        if iDelay < 0:
            print('No negativ Delay is possible!')
        else:
            self.rampSpeed_delay = iDelay

    def getRampSpeed(self):
        return([int(self.rampSpeed_step), int(self.rampSpeed_delay)])

    def rampVoltage(self, fVnew, iChannel):
        V = self.getVoltage(iChannel)
        V = round(V, 4)
        if abs(fVnew - V) <= self.rampSpeed_step:
            self.setVoltage(fVnew, iChannel)
            print('Voltage reached: %.2f V' % fVnew)
        else:
            self.setVoltage(V + self.rampSpeed_step *
                            (fVnew - V) / abs(fVnew - V))
            print('Ramp Voltage: %.2f V' %
                  (V + self.rampSpeed_step * (fVnew - V) / abs(fVnew - V)))
            sleep(self.rampSpeed_delay)
            self.rampVoltage(fVnew, iChannel)
            pass

    def reset(self):
        self.write('*RST')

    def output(self, show=True):
        bPower_CH1 = self.getOutput(1)
        bPower_CH2 = self.getOutput(2)

        if bPower_CH1 == '1':
            fVoltage_CH1 = self.getVoltage(1)
            fCurrent_CH1 = self.getCurrent(1) * 1E6
        else:
            fVoltage_CH1 = 0
            fCurrent_CH1 = 0

        if bPower_CH2 == '2':
            fVoltage_CH2 = self.getVoltage(2)
            fCurrent_CH2 = self.getCurrent(2) * 1E6
        else:
            fVoltage_CH2 = 0
            fCurrent_CH2 = 0

        if show:
            self.printOutput('Agilent3646A:')
            if bPower_CH1 == '1':
                self.printOutput('Output CH1 \033[32m ON \033[0m')
                self.printOutput('Voltage = %0.1f V' % fVoltage_CH1)
                self.printOutput('Current = %0.3f uA' % fCurrent_CH1)
            else:
                self.printOutput('Output CH1 \033[31m OFF \033[0m')
                self.printOutput('Voltage = ---- V')
                self.printOutput('Current = ---- uA')
            if bPower_CH2 == '1':
                self.printOutput('Output CH2 \033[32m ON \033[0m')
                self.printOutput('Voltage = %0.1f V' % fVoltage_CH2)
                self.printOutput('Current = %0.3f uA' % fCurrent_CH2)
            else:
                self.printOutput('Output CH2 \033[31m OFF \033[0m')
                self.printOutput('Voltage = ---- V')
                self.printOutput('Current = ---- uA')

        return([['Output_CH1', 'Output_CH2', 'U_CH1[V]', 'I_CH1[uA]', 'U_CH2[V]', 'I_CH2[uA]'], [str(bPower_CH1), str(bPower_CH2), str(fVoltage_CH1), str(fCurrent_CH1), str(fVoltage_CH2), str(fCurrent_CH2)]])

    def interaction(self, gui=False):
        if gui:
            device_dict = {
            'channel': 2,
			'toogleOutput': True,
			'rampVoltage': True,
			'setCurrent': True,
			}
            return device_dict
        else:
            print(
                'Select a channel!'
                )
            iChannel = input('Possible inputs: 1 or 2\n')
            while not iChannel in ['1', '2']:
                iChannel = input('Possible Inputs: 1 or 2! \n')
            print(f'Channel {iChannel} choosen.')
            print(
                '0: Continue dcs mode without any changes\n'
                '1: Toggle output\n'
                '2: Set voltage (enables the output if its off)\n'
                '3: Set currrent'
                )

            x = input('Number? \n')
            while not (x in ['0','1','2','3',]):
                x = input('Possible Inputs: 0, 1, 2 or 3! \n')

            if x == '0':
                pass
            elif x == '1':
                if self.getOutput(iChannel) == '1':
                    self.rampVoltage(0, iChannel)
                    self.setOutput(False, iChannel)
                else:
                    self.setOutput(True, iChannel)
            elif x == '2':
                fV = input('Please enter new Voltage in V \n')
                if not self.getOutput(iChannel) == '1':
                    print('Enabled output. Now ramping...')
                    self.setOutput(True, iChannel)
                self.rampVoltage(float(fV), iChannel)
            elif x == '3':
                fI = input('Please enter new current limit in uA \n')
                self.setCurrent(float(fI)/1E6, iChannel)
