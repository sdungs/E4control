# -*- coding: utf-8 -*-

from time import sleep

from .device import Device
import warnings


class K2614(Device):

    def __init__(self, connection_type, host, port):
        super(K2614, self).__init__(
            connection_type=connection_type, host=host, port=port)
        self.trm = '\n'
        self.rampSpeed_step = 10
        self.rampSpeed_delay = 1  # s

    def initialize(self, iChannel='all'):
        """
        Initialize the device with a standard setting.

        Parameters
        ----------
        iChannel: str or int, optional
            Channel where the voltage range should be set.
        """
        if iChannel == 'all':
            self.setVoltageRange('AUTO', 1)
            self.setVoltageRange('AUTO', 2)
        else:
            self.setVoltageRange('AUTO', iChannel)

    def convert_iChannel(self, iChannel):
        """
        The channel is usually passed as a int, which differs from
        the sma-style.
        This function converts a 1 to an a and a 2 to an b.

        Parameters
        ----------
        iChannel: str or int
            Channel number for conversion.
        """
        one = [1, '1', 'one']
        two = [2, '2', 'two']
        if iChannel in one:
            iChannel = 'a'
        elif iChannel in two:
            iChannel = 'b'
        return iChannel

    def setCurrentAutoRange(self, iChannel):
        """
        Set the current auto range of a given channel.

        Parameters
        ----------
        iChannel: str or int
            Channel where the current auto range should be performed.
        """
        iChannel = self.convert_iChannel(iChannel)
        self.write(f'smu{iChannel}.source.autorangei = smu{iChannel}.AUTORANGE_ON')

    def setVoltageRange(self, sRange, iChannel):
        """
        Set the voltage range of a given Channel.

        Parameters
        ----------
        sRange : float
             Value of the voltage range.
        iChannel: str or int
            Channel where the voltage range should be set.
        """
        iChannel = self.convert_iChannel(iChannel)
        if isinstance(sRange, int):
            self.write(f'smu{iChannel}.source.rangev = {sRange}')
        elif sRange == 'AUTO':
            self.write(f'smu{iChannel}.source.autorangev = smu{iChannel}.AUTORANGE_ON')
        else:
            print('Unknown Range')

    def setCurrentLimit(self, fIlim, iChannel):
        """
        Set the current limit of a given Channel.

        Parameters
        ----------
        fIlim : float
             Value of the current limit.
        iChannel: str or int
            Channel where the current limit should be set.
        """
        iChannel = self.convert_iChannel(iChannel)
        self.write(f'smu{iChannel}.source.limiti = {fIlim}')

    def setVoltageLimit(self, fVlim, iChannel):
        """
        Set the voltage limit of a given Channel.

        Parameters
        ----------
        fVlim : float
             Value of the voltage limit.
        iChannel: str or int
            Channel where the voltage limit should be set.
        """
        iChannel = self.convert_iChannel(iChannel)
        self.write(f'smu{iChannel}.source.limitv = {fVlim}')

    def setVoltage(self, fVset, iChannel):
        """
         Set the output voltage of a given Channel.

         Parameters
         ----------
         fVset : float
              Value of the voltage.
         iChannel: str or int
             Channel where the voltage should be set.
         """
        iChannel = self.convert_iChannel(iChannel)
        self.write(f'smu{iChannel}.source.levelv = {fVset}')

    def setOutput(self, bEnable, iChannel):
        """
         Set the output current of a given Channel.

         Parameters
         ----------
         bEnable : bool
              Boolen to enable or disable the output of a given channel.
         iChannel: str or int
             Channel where the output should be set.
         """
        iChannel = self.convert_iChannel(iChannel)
        if bEnable:
            self.write(f'smu{iChannel}.source.output = smu{iChannel}.OUTPUT_ON')
        else:
            self.write(f'smu{iChannel}.source.output = smu{iChannel}.OUTPUT_OFF')

    def getOutput(self, iChannel):
        """
        Get the output state of a given channel.

        Parameters
        ----------
        iChannel : str or int
            Channel where the output state is queried from.

        Returns
        -------
        bool str
            Current output state of a given channel
        """
        iChannel = self.convert_iChannel(iChannel)
        bPower = float(self.ask(f'print(smu{iChannel}.source.output)'))
        if bPower == 0:
            return False
        if bPower == 1:
            return True

    def getVoltage(self, iChannel):
        """
        Get the voltage of a given channel.

        Parameters
        ----------
        iChannel : str or int
            Channel where the voltage is queried from.

        Returns
        -------
        sValues : float
            Voltage of a given channel.
        """
        iChannel = self.convert_iChannel(iChannel)
        sValue = self.ask(f'print(smu{iChannel}.source.levelv)')
        return float(sValue)

    def getCurrent(self, iChannel):
        """
        Get the current of a given channel.

        Parameters
        ----------
        iChannel : str or int
            Channel where the voltage is queried from.

        Returns
        -------
        sValues : float
            Current of a given channel.
        """
        iChannel = self.convert_iChannel(iChannel)
        sValue = self.ask(f'print(smu{iChannel}.source.leveli)')
        return float(sValue)

    def getCurrentLimit(self, iChannel):
        """
        Get the current limit of a given channel.

        Parameters
        ----------
        iChannel : str or int
            Channel where the current limit is queried from.

        Returns
        -------
        float
            Current limit of a given channel.
        """
        iChannel = self.convert_iChannel(iChannel)
        sCurrLim = self.ask(f'print(smu{iChannel}.source.limiti)')
        return float(sCurrLim)

    def getVoltageLimit(self, iChannel):
        """
        Get the voltage limit of a given channel.

        Parameters
        ----------
        iChannel : str or int
            Channel where the voltage limit is queried from.

        Returns
        -------
        float
            Voltage limit of a given channel.
        """
        iChannel = self.convert_iChannel(iChannel)
        sVoltLim = self.ask(f'print(smu{iChannel}.source.rangev)')
        return float(sVoltLim)

    def setRampSpeed(self, iRampSpeed, iDelay):
        """
        Set the voltage ramp speed of a given channel.

        Parameters
        ----------
        iRampSpeed : int, class variable
            Speed the voltage can ramp in V per ramp step.
        iDelay : int, class variable
            Ramp delay in seconds.
        """
        if iRampSpeed < 1 or iRampSpeed > 255:
            print('Set RampSpeed size is out of range!')
        else:
            self.rampSpeed_step = iRampSpeed
        if iDelay < 0:
            print('No negativ Delay is possible!')
        else:
            self.rampSpeed_delay = iDelay

    def getRampSpeed(self):
        """
        Set the voltage ramp speed of a given channel.

        Returns
        -------
        int
            Ramp speed step.
        int
            Ramp speed delay.
        """
        return([int(self.rampSpeed_step), int(self.rampSpeed_delay)])

    def rampVoltage(self, fVnew, iChannel):
        """
        Ramp the voltage of a given channel.

        Parameters
        ----------
        fVnew : float
            Voltage the device should ramp to.
        iChannel : str or int
            Channel where the voltage limit is queried from.
        """
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
        """
        Reset the device to its factory standard values.
        """
        self.write('reset()')

    def output(self, show=True):
        """
        Print the devices output. Used by the dcs script.

        Parameters
        ----------
        show : bool, optional
            Parameter to configure if the output is printed.

        Returns
        -------
        tuple (list[str], list[str])
            The first part of the tuple is a list with the names of the output features.
            The second part of the tuple are the corresponding valies.
        """
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
            self.printOutput('Agilent3646A:')
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
        """
        Trigger an interaction with the device.
        This function is used by the dcs and the gui_dcs script.

        Parameters
        ----------
        gui : bool
            Parameter to turn on the gui function.
            Only used for the gui_dcs script.
        """
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
