# -*- coding: utf-8 -*-

from time import sleep
import warnings

from .device import Device


class SHR(Device):
    __fVmaxCh0 = None
    __fVmaxCh1 = None

    def __init__(self, connection_type, host, port):
        super(SHR, self).__init__(connection_type=connection_type, host=host, port=port)

    def __checkChannel(self, channel):
        sChannel = str(channel)
        if sChannel in ('1','2'):
            return str(int(sChannel) - 1)
        else:
            raise ValueError('Please use a valid channel format (\'1\' or \'2\').')

    def __checkChannels(self, channel):
        if channel in ('all', -1):
            return '0-1'
        else:
            sChannel = str(channel)
            if sChannel in ('1','2'):
                return str(int(sChannel) - 1)
            elif sChannel in ('0,1','0-1'):
                return sChannel
            else:
                raise ValueError('Please use a valid channel format (\'0\',\'1\',\'0,1\',\'0-1\').')

    def __checkPolarity(self, polarity):
        if polarity in ('p','+'):
            return 'p'
        elif polarity in ('n','-'):
            return 'n'
        else:
            raise ValueError('Please use a valid polarity format (\'p\',\'+\',\'n\',\'-\').')


    def initialize(self, channel='all'):
        # Query the channel voltage nominal value
        self.__fVmaxCh0, self.__fVmaxCh1  = self.ask(':READ:VOLT:NOM? (@0,1)').split(',')
        self.__fVmaxCh0 = float(self.__fVmaxCh0[:-1])
        self.__fVmaxCh1 = float(self.__fVmaxCh1[:-1])
        # Query the module identification
        return self.ask('*IDN?')

    def reset(self, channel='all'):
        self.write('*RST') # Reset the device to save values: Set HV to 0V and turn HV off with ramp for all channels


    def setOutput(self, bEnable, channel='all'):
        sChannel = self.__checkChannels(channel)
        if bEnable:
            self.write(':VOLT ON,(@{})'.format(sChannel))
        else:
            self.write(':VOLT OFF,(@{})'.format(sChannel))

    def getOutput(self, channel='all'):
        sChannel = self.__checkChannels(channel)
        return self.ask(':READ:VOLT:ON? (@{})'.format(sChannel))

    def enableOutput(self, channel='all'):
        sChannel = self.__checkChannels(channel)
        self.setOutput(True, sChannel)

    def disableOutput(self, channel='all'):
        sChannel = self.__checkChannels(channel)
        self.setOutput(False, sChannel)


    def setPolarity(self, polarity, channel='all'):
        sPolarity = self.__checkPolarity(polarity)
        sChannel = self.__checkChannels(channel)
        return self.ask(':CONF:OUTP:POL {},(@{})'.format(sPolarity, sChannel))

    def getPolarity(self, channel='all'):
        sChannel = self.__checkChannels(channel)
        return self.ask(':CONF:OUTP:POL? (@{})'.format(sChannel))


    def setRampSpeed(self, iRampSpeed, channel):
        if iRampSpeed < 1 or iRampSpeed > 400:
            warnings.warn('RampSpeed exceeds ramp speed bounds. Please choose a value between 1 and 400 V/s')
        else:
            sChannel = self.__checkChannel(channel)
            self.write(':CONF:RAMP:VOLT {}'.format(iRampSpeed*100/2000))
            self.write(':CONF:RAMP:VOLT:UP {}, (@{})'.format(iRampSpeed, sChannel))
            self.write(':CONF:RAMP:VOLT:DO {}, (@{})'.format(iRampSpeed, sChannel))

    def getRampSpeed(self, channel):
        sChannel = self.__checkChannel(channel)
        # return self.ask(':READ:RAMP:VOLT? (@{})'.format(sChannel))
        sRamp = self.ask(':READ:RAMP:VOLT? (@{})'.format(sChannel))
        return float(sRamp[:-3])


    def setVoltage(self, fValue, channel):
        sChannel = self.__checkChannel(channel)
        if self.getPolarity(channel)=='p':
            polarity = +1
        else:
            polarity = -1
        if fValue*polarity < 0:
            warnings.warn('Set voltage and polarity have different signs.')
        self.write(':VOLT {},(@{})'.format(fValue, sChannel))

    def getSetVoltage(self, channel):
        sChannel = self.__checkChannel(channel)
        # return self.ask(':READ:VOLT? (@{})'.format(sChannel))
        sSetVoltage = self.ask(':READ:VOLT? (@{})'.format(sChannel))
        return float(sSetVoltage[:-1])

    def getVoltage(self, channel):
        sChannel = self.__checkChannel(channel)
        # return self.ask(':MEAS:VOLT? (@{})'.format(sChannel))
        sVoltage = self.ask(':MEAS:VOLT? (@{})'.format(sChannel))
        return float(sVoltage[:-1])

    def getCurrent(self, channel):
        sChannel = self.__checkChannel(channel)
        # return self.ask(':MEAS:CURR? (@{})'.format(sChannel))
        sCurrent = self.ask(':MEAS:CURR? (@{})'.format(sChannel))
        return float(sCurrent[:-1])


    def setCurrentLimit(self, channel='all'):
        warnings.warn('Only manual setting possible. Adjust the potentiometer on the rear panel.')

    def setVoltageLimit(self, channel='all'):
        warnings.warn('Only manual setting possible. Adjust the potentiometer on the rear panel.')

    def getVoltageLimit(self, channel):
        sChannel = self.__checkChannel(channel)
        # return self.ask(':READ:VOLT:LIM? (@{})'.format(sChannel))
        sVoltLim = self.ask(':READ:VOLT:LIM? (@{})'.format(sChannel))
        return float(sVoltLim[:-1])

    def getCurrentLimit(self, channel):
        sChannel = self.__checkChannel(channel)
        # return self.ask(':READ:CURR:LIM? (@{})'.format(sChannel))
        sCurrLim = self.ask(':READ:CURR:LIM? (@{})'.format(sChannel))
        return float(sCurrLim[:-1])


    def getDeviceTemperature(self):
        return self.ask(':READ:MOD:TEMP?')


    # def setRampSpeed(self, iRampSpeed, iDelay):
    #     if iRampSpeed < 1 or iRampSpeed > 255:
    #         print('Set RampSpeed size is out of range!')
    #     else:
    #         self.rampSpeed_step = iRampSpeed
    #     if iDelay < 0:
    #         print('No negativ Delay is possible!')
    #     else:
    #         self.rampSpeed_delay = iDelay

    # def getRampSpeed(self):
    #     return([int(self.rampSpeed_step), int(self.rampSpeed_delay)])

    def rampVoltage(self, fVnew, iChannel):
        self.setVoltage(fVnew, iChannel)

    # def rampVoltage(self, fVnew, iChannel):
    #     fVnew = abs(fVnew)
    #     V = self.getVoltage(iChannel)
    #     V = round(V, 4)
    #     if abs(fVnew-abs(V)) <= self.rampSpeed_step:
    #         self.setVoltage(fVnew, iChannel)
    #         print('Voltage reached: %.2f V' % fVnew)
    #     else:
    #         self.setVoltage(abs(V)+self.rampSpeed_step*(fVnew-abs(V))/abs(fVnew-abs(V)), iChannel)
    #         print('Ramp Voltage: %.2f V' % (abs(V)+self.rampSpeed_step*(fVnew-abs(V))/abs(fVnew-abs(V))))
    #         sleep(self.rampSpeed_delay)
    #         self.rampVoltage(fVnew, iChannel)

    def output(self, show=True):
        fLimitCh0 = self.getCurrentLimit(1) * 1E6
        fLimitCh1 = self.getCurrentLimit(2) * 1E6
        fVoltageCh0 = self.getVoltage(1)
        fVoltageCh1 = self.getVoltage(2)
        fCurrentCh0 = self.getCurrent(1) * 1E6
        fCurrentCh1 = self.getCurrent(2) * 1E6
        sStatus = self.getOutput('all')
        if int(sStatus[0]):
            sStatusCh0 = '\033[32m ON  \033[0m'
        else:
            sStatusCh0 = '\033[31m OFF \033[0m'
        if int(sStatus[2]):
            sStatusCh1 = '\033[32m ON  \033[0m'
        else:
            sStatusCh1 = '\033[31m OFF \033[0m'
        sPolarity = self.getPolarity('all')
        if sPolarity[0]=='p':
            sPolarityCh0 = '\033[31m positive+ \033[0m'
        else:
            sPolarityCh0 = '\033[34m negative- \033[0m'
        if sPolarity[2]=='p':
            sPolarityCh1 = '\033[31m positive+ \033[0m'
        else:
            sPolarityCh1 = '\033[34m negative- \033[0m'

        if show:
            self.printOutput('ISEG SHR:')
            # self.printOutput('CH 0:' + '\t' + 'I_lim = %.2fuA' % f1Limit)
            # self.printOutput('Voltage = %.1fV' % f1Voltage + '\t' + 'Current = %.3fuA' % f1Current)
            # self.printOutput('CH 1:' + '\t' + 'I_lim = %.2fuA' % f2Limit)
            # self.printOutput('Voltage = %.1fV' % f2Voltage + '\t' + 'Current = %.3fuA' % f2Current)
            self.printOutput('          \t {:10} \t {:10}'.format('Channel 1','Channel 2'))
            self.printOutput('Output:   \t {:18} \t {:18}'.format(sStatusCh0,sStatusCh1))
            self.printOutput('Polarity: \t {:10} \t {:10}'.format(sPolarityCh0,sPolarityCh1))
            self.printOutput('Voltage:  \t {:6.5} V  \t {:6.5} V '.format(fVoltageCh0,fVoltageCh1))
            self.printOutput('Current:  \t {:6.5} uA \t {:6.5} uA'.format(fCurrentCh0,fCurrentCh1))
            self.printOutput('Limit:    \t {:6.5} uA \t {:6.5} uA'.format(fLimitCh0,fLimitCh1))
        return([['Output1', 'Polarity1', 'Ilim1[uA]', 'U1[V]', 'I1[uA]', 'Output2', 'Polarity2', 'Ilim2[uA]', 'U2[V]', 'I2[uA]'], [str(sStatusCh0), str(sPolarityCh0), str(fLimitCh0), str(fVoltageCh0), str(fCurrentCh0), str(sStatusCh1), str(sPolarityCh1), str(fLimitCh1), str(fVoltageCh1), str(fCurrentCh1)]])

    def interaction(self, gui=False):
        if gui:
            device_dict = {
            'channel': 2,
            'toogleOutput': True,
            'setVoltage': True,
            'tooglePolarity': True,
            'rampDeviceDown': True,
            }
            return device_dict
        else:
            print(
                'ISEG SHR selected. Possible actions:\n'
                '0: Continue dcs mode without any changes\n'
                '1: Set voltage (also enables the channel output)\n'
                '2: Disable channel output\n'
                '3: Toggle polarity (channel has to be off)\n'
                '4: Display and change ramp speed\n'
                '5: Set HV to 0V and turn HV off with ramp for all channels'
                )

            x = input('Number? \n')
            while not (x in ['0','1','2','3','4','5']):
                x = input('Possible Inputs: 0, 1, 2, 3, 5! \n')
            if x == '0':
                pass
            elif x == '5':
                self.reset()
            else:
                sChannel = input('Which channel? \n')
                while not (sChannel in ['0','1']):
                    sChannel = input('Possible Channels: 0 or 1! \n')

            if x == '1':
                fV = input('Please enter new Voltage (in V) for Channel {}.\n'.format(sChannel))
                self.setVoltage(float(fV), sChannel)
                self.enableOutput(sChannel)
            elif x == '2':
                self.disableOutput(sChannel)
            elif x == '3':
                if int(self.getOutput(sChannel)):
                    warnings.warn('Channel has to be off!')
                else:
                    sPolarity = self.getPolarity(sChannel)
                    if sPolarity=='p':
                        self.setPolarity('n',sChannel)
                    else:
                        self.setPolarity('p',sChannel)
            elif x == '4':
                print('Current ramp speed for Channel {}: {} V/s'.format(sChannel, self.getRampSpeed(sChannel)))
                sRampSpeed = input('Please enter new ramp speed (in V/s) for Channel {}.\n'.format(sChannel))
                self.setRampSpeed(float(sRampSpeed),sChannel)
