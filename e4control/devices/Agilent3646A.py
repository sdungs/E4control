# -*- coding: utf-8 -*-

from time import sleep

from .device import Device
import warnings


class Agilent3646A(Device):

    def __init__(self, connection_type, host, port):
        super(Agilent3646A, self).__init__(
            connection_type=connection_type, host=host, port=port)
        self.trm = '\n'
        self.rampSpeed_step = 10
        self.rampSpeed_delay = 1  # s

    def initialize(self):
        """
        Initialize the device with a standard setting.
        """
        self.write(':SYST:REM')
        self.setVoltageRange('MAX', 1)
        self.setVoltageRange('MAX', 2)

    def setVoltageRange(self, sRange, iChannel):
        """
        Set the voltage range of a given Channel.

        Parameters
        ----------
        sRange : str
            Available voltage ranges (MAX, MIN, AUTO).
        iChannel: str or int
            Channel where the voltage range should be set.
        """
        self.write(f':INST:SEL OUT{iChannel}')
        if sRange == 'MAX':
            self.write(':VOLT:RANG HIGH')
        elif sRange == 'MIN':
            self.write(':VOLT:RANG LOW')
        elif sRange == 'AUTO':
            self.write(':VOLT:RANG:AUTO ON')
        else:
            print('Unknown Range')

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
        self.write(f':INST:SEL OUT{iChannel}')
        self.write(f':VOLT:PROT {fVlim}')

    def setCurrent(self, fIset, iChannel):
        """
        Set the output current of a given Channel.

        Parameters
        ----------
        fIset : float
             Value of the current.
        iChannel: str or int
            Channel where the current should be set.
        """
        self.write(f':INST:SEL OUT{iChannel}')
        self.write(f':CURR {fIset}')

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
        self.write(f':INST:SEL OUT{iChannel}')
        self.write(f':VOLT {fVset}')

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
        self.write(f':INST:SEL OUT{iChannel}')
        if bEnable:
            self.write(':OUTPUT ON')
        else:
            self.write(':OUTPUT OFF')

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
        self.write(f':INST:SEL OUT{iChannel}')
        return self.ask(':OUTPUT?')

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
        self.write(f':INST:SEL OUT{iChannel}')
        sValues = self.ask(':VOLT?')
        return float(sValues)

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
        self.write(f':INST:SEL OUT{iChannel}')
        sValues = self.ask(':CURR?')
        return float(sValues)

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
        self.write(f':INST:SEL OUT{iChannel}')
        return float(self.ask(':VOLT:PROT?'))

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
        return ([int(self.rampSpeed_step), int(self.rampSpeed_delay)])

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

    def reset(self):
        """
        Reset the device to its factory standard values.
        """
        self.write('*RST')

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
            The second part of the tuple are the corresponding values.
        """
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

        return ([['Output_CH1', 'Output_CH2', 'U_CH1[V]', 'I_CH1[uA]', 'U_CH2[V]', 'I_CH2[uA]'],
                 [str(bPower_CH1), str(bPower_CH2), str(fVoltage_CH1), str(fCurrent_CH1), str(fVoltage_CH2),
                  str(fCurrent_CH2)]])

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
            while not (x in ['0', '1', '2', '3', ]):
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
                self.setCurrent(float(fI) / 1E6, iChannel)
