# -*- coding: utf-8 -*-

from time import sleep

from .device import Device
import warnings


class K2614(Device):
    rampSpeed_step = 10
    rampSpeed_delay = 1  # s

    def __init__(self, connection_type, host, port):
        super(K2614, self).__init__(
            connection_type=connection_type, host=host, port=port)
        self.trm = '\n'

    def initialize(self, iChannel='all'):
        if iChannel == 'all':
            self.setVoltageRange('AUTO', 1)
            self.setVoltageRange('AUTO', 2)
        else:
            self.setVoltageRange('AUTO', iChannel)
        pass

    def convert_iChannel(self, iChannel):
        one = [1, '1', 'one']
        two = [2, '2', 'two']
        if iChannel in one:
            iChannel = 'a'
        elif iChannel in two:
            iChannel = 'b'
        return iChannel

    def setCurrentAutoRange(self, iChannel):
        iChannel = self.convert_iChannel(iChannel)
        self.write(f'smu{iChannel}.source.autorangei = smu{iChannel}.AUTORANGE_ON')

    def setVoltageRange(self, sRange, iChannel):
        iChannel = self.convert_iChannel(iChannel)
        if isinstance(sRange, int):
            self.write(f'smu{iChannel}.source.rangev = {sRange}')
        elif sRange == 'AUTO':
            self.write(f'smu{iChannel}.source.autorangev = smu{iChannel}.AUTORANGE_ON')
        else:
            print('Unknown Range')

    def setCurrentLimit(self, fIlim, iChannel):
        iChannel = self.convert_iChannel(iChannel)
        self.write(f'smu{iChannel}.source.limiti = {fIlim}')

    def setVoltageLimit(self, fVlim, iChannel):
        iChannel = self.convert_iChannel(iChannel)
        self.write(f'smu{iChannel}.source.limitv = {fVlim}')

    def setVoltage(self, fVset, iChannel):
        iChannel = self.convert_iChannel(iChannel)
        self.write(f'smu{iChannel}.source.levelv = {fVset}')

    def setOutput(self, bEnable, iChannel):
        iChannel = self.convert_iChannel(iChannel)
        if bEnable:
            self.write(f'smu{iChannel}.source.output = smu{iChannel}.OUTPUT_ON')
        else:
            self.write(f'smu{iChannel}.source.output = smu{iChannel}.OUTPUT_OFF')

    def getOutput(self, iChannel):
        iChannel = self.convert_iChannel(iChannel)
        bPower = float(self.ask(f'print(smu{iChannel}.source.output)'))
        if bPower == 0:
            return False
        if bPower == 1:
            return True

    def getVoltage(self, iChannel):
        iChannel = self.convert_iChannel(iChannel)
        sValue = self.ask(f'print(smu{iChannel}.measure.v())')
        return float(sValue)

    def getCurrent(self, iChannel):
        iChannel = self.convert_iChannel(iChannel)
        sValue = self.ask(f'print(smu{iChannel}.measure.i())')
        return float(sValue)

    def getCurrentLimit(self, iChannel):
        iChannel = self.convert_iChannel(iChannel)
        sCurrLim = self.ask(f'print(smu{iChannel}.source.limiti)')
        return float(sCurrLim)

    def getVoltageLimit(self, iChannel):
        iChannel = self.convert_iChannel(iChannel)
        sVoltLim = self.ask(f'print(smu{iChannel}.source.rangev)')
        return float(sVoltLim)

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
                            (fVnew - V) / abs(fVnew - V), iChannel)
            print('Ramp Voltage: %.2f V' %
                  (V + self.rampSpeed_step * (fVnew - V) / abs(fVnew - V)))
            sleep(self.rampSpeed_delay)
            self.rampVoltage(fVnew, iChannel)
            pass

    def reset(self):
        self.write('reset()')

    def output(self, show=True):
        bPower_CH1 = self.getOutput(1)
        bPower_CH2 = self.getOutput(2)
        fILimit_CH1 = self.getCurrentLimit(1) * 1E6
        fILimit_CH2 = self.getCurrentLimit(2) * 1E6


        if bPower_CH1:
            fVoltage_CH1 = self.getVoltage(1)
            fCurrent_CH1 = self.getCurrent(1) * 1E6
        else:
            fVoltage_CH1 = 0
            fCurrent_CH1 = 0

        if bPower_CH2:
            fVoltage_CH2 = self.getVoltage(2)
            fCurrent_CH2 = self.getCurrent(2) * 1E6
        else:
            fVoltage_CH2 = 0
            fCurrent_CH2 = 0

        if show:
            self.printOutput('K2614:')
            if bPower_CH1:
                self.printOutput('Output CH1 \033[32m ON \033[0m')
                self.printOutput('Currentlimit = %0.3f uA' % fILimit_CH1)
                self.printOutput('Voltage = %0.1f V' % fVoltage_CH1)
                self.printOutput('Current = %0.3f uA' % fCurrent_CH1)
            else:
                self.printOutput('Output CH1 \033[31m OFF \033[0m')
                self.printOutput('Currentlimit = %0.3f uA' % fILimit_CH1)
                self.printOutput('Voltage = ---- V')
                self.printOutput('Current = ---- uA')
            if bPower_CH2:
                self.printOutput('Output CH2 \033[32m ON \033[0m')
                self.printOutput('Currentlimit = %0.3f uA' % fILimit_CH2)
                self.printOutput('Voltage = %0.1f V' % fVoltage_CH2)
                self.printOutput('Current = %0.3f uA' % fCurrent_CH2)
            else:
                self.printOutput('Output CH2 \033[31m OFF \033[0m')
                self.printOutput('Currentlimit = %0.3f uA' % fILimit_CH2)
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
            'setCurrentLimit': True,
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
                '3: Set currentlimit'
                )

            x = input('Number? \n')
            while not (x in ['0','1','2','3']):
                x = input('Possible Inputs: 0, 1, 2 or 3! \n')

            if x == '0':
                pass
            elif x == '1':
                if self.getOutput(iChannel):
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
                fIlim = input('Please enter new current limit in uA \n')
                self.setCurrentLimit(float(fIlim)/1E6, iChannel)
