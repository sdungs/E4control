# -*- coding: utf-8 -*-

from .device import Device
from time import sleep


class TENMA72_13330(Device):
    __bOutputCh1 = None
    __bOutputCh2 = None

    def __init__(self, connection_type, host, port):
        super(TENMA72_13330, self).__init__(connection_type=connection_type, host=host, port=port)
        self.trm = '\n'
        self.initialize()

    def __checkChannel(self, iChannel):
        sChannel = str(iChannel)
        if sChannel in ('1','2'):
            return sChannel
        else:
            raise ValueError('Please use a valid channel format (\'1\' or \'2\').')

    def initialize(self):
        pass

    def getStatus(self):
        # Returns the POWER SUPPLY status.
        # Contents 8 bits in the following format
        # Bit Item Description
        # 0     CH1 0=CC mode, 1=CV mode
        # 1     CH2 0=CC mode, 1=CV mode
        # 2, 3  Tracking 00=Independent, 01=Tracking series, 10=Tracking parallel
        # 4     OVP 0 OFF,1 ON
        # 5     OCP 0 OFF,1 ON
        # 6     CH1 0 CH1 OFF, 1 CH1 ON
        # 7     CH2 0 CH1 OFF, 1 CH1 ON
        self.write('STATUS?')
        sStatus = self.com.recv_from_socket(32)
        return '{:08b}'.format(sStatus[0])

    def setOutput(self, bEnable, iChannel):
        sChannel = self.__checkChannel(iChannel)
        self.write('OUT{}:{:d}'.format(sChannel, bEnable))
        if sChannel == '1':
            self.__bOutputCh1 = bEnable
        elif sChannel == '2':
            self.__bOutputCh2 = bEnable

    def getOutput(self, iChannel):
        sChannel = self.__checkChannel(iChannel)
        sStatus = self.getStatus()
        if sChannel == '1':
            return sStatus[1]
        elif sChannel == '2':
            return sStatus[0]


    def setVoltage(self, fValue, iChannel):
        sChannel = self.__checkChannel(iChannel)
        self.write('VSET{}:{:.2f}'.format(sChannel, fValue))

    def getSetVoltage(self, iChannel):
        sChannel = self.__checkChannel(iChannel)
        sSetVoltage = self.ask('VSET{}?'.format(sChannel))
        return float(sSetVoltage)

    def getVoltage(self, iChannel):
        sChannel = self.__checkChannel(iChannel)
        sVoltage = self.ask('VOUT{}?'.format(sChannel))
        return float(sVoltage)

    def setCurrent(self, fValue, iChannel):
        self.write('ISET{}:{:.3f}'.format(iChannel, fValue))
        pass

    def getSetCurrent(self, iChannel):
        sChannel = self.__checkChannel(iChannel)
        return float(self.ask('ISET{}?'.format(sChannel)))

    def getCurrent(self, iChannel):
        sChannel = self.__checkChannel(iChannel)
        sCurrent = self.ask('IOUT{}?'.format(sChannel))
        return float(sCurrent)


    def getIP(self):
        return self.ask(':SYST:IPAD?')

    def getPort(self):
        return self.ask(':SYST:PORT?')

    def setDHCP(self, bEnable):
        self.write(':SYST:DHCP {:d}'.format(bEnable))

    def getDHCP(self):
        return self.ask(':SYST:DHCP?')

    def getDeviceInfo(self):
        devinfo = []
        self.write(':SYST:DEVINFO?')
        for i in range(0,7):
            devinfo.append(self.read())
        return devinfo



    def output(self, show=True):
        if show:
            self.printOutput('TENMA72-13330:')
            # if self.connection_type == 'lan_udp':
            #     self.printOutput('If the script freezes at this point, it is likely that the udp connection has hung. In this case, please restart.')
        sStatus = self.getStatus()
        sStatusCh1 = sStatus[1]
        sStatusCh2 = sStatus[0]
        if int(sStatusCh1):
            sStatusCh1 = '\033[32m ON  \033[0m'
            self.__bOutputCh1 = True
        else:
            sStatusCh1 = '\033[31m OFF \033[0m'
            self.__bOutputCh1 = False
        if int(sStatusCh2):
            sStatusCh2 = '\033[32m ON  \033[0m'
            self.__bOutputCh2 = True
        else:
            sStatusCh2 = '\033[31m OFF \033[0m'
            self.__bOutputCh2 = False

        fVoltageCh1 = self.getVoltage(1)
        fVoltageCh2 = self.getVoltage(2)
        fSetVoltageCh1 = self.getSetVoltage(1)
        fSetVoltageCh2 = self.getSetVoltage(2)
        fCurrentCh1 = self.getCurrent(1)
        fCurrentCh2 = self.getCurrent(2)
        fLimitCh1 = self.getSetCurrent(1)
        fLimitCh2 = self.getSetCurrent(2)

        if show:
            # if self.connection_type == 'lan_udp':
            #     self.printOutput('Yay, not frozen!')
            # self.printOutput('TENMA72-13330:')
            self.printOutput('          \t {:10} \t {:10}'.format('Channel 1','Channel 2'))
            self.printOutput('Output:   \t {:18} \t {:18}'.format(sStatusCh1,sStatusCh2))
            self.printOutput('Voltage:  \t {:6.7} V  \t {:6.7} V '.format(fVoltageCh1,fVoltageCh2))
            self.printOutput('Set Voltage: \t {:6.7} V  \t {:6.7} V '.format(fSetVoltageCh1,fSetVoltageCh2))
            self.printOutput('Current:  \t {:6.8} A \t {:6.8} A'.format(fCurrentCh1,fCurrentCh2))
            self.printOutput('Limit:    \t {:6.8} A \t {:6.8} A'.format(fLimitCh1,fLimitCh2))
        sValues = [str(fVoltageCh1), str(fCurrentCh1), str(fVoltageCh2), str(fCurrentCh2)]
        sHeader = ['U1[V]', 'I1[A]', 'U2[V]', 'I2[A]']
        return([sHeader, sValues])

    def interaction(self, gui=False):
        if gui:
            device_dict = {
			'channel': 5,
			'toogleOutput': True,
			'setVoltage': True,
			'setCurrentLimit': True,
			}
            return device_dict
        else:
            print(
                'TENMA72-13330 selected. Possible actions:\n'
                '0: Continue dcs mode without any changes\n'
                '1: Set voltage\n'
                '2: Set current limit\n'
                '3: Toggle channel output\n'
                )

            x = input('Number? \n')
            while not (x in ['0','1','2','3','4','5']):
                x = input('Possible Inputs: 0, 1, 2, 3, 5! \n')
            if x == '0':
                return
            else:
                sChannel = input('Which channel? \n')
                while not (sChannel in ['1','2']):
                    sChannel = input('Possible Channels: 1 or 2! \n')

            if x == '1':
                sV = input('Please enter new voltage (in V) for channel {}.\n'.format(sChannel))
                self.setVoltage(float(sV), sChannel)
            elif x == '2':
                sI = input('Please enter new current limit (in A) for channel {}.\n'.format(sChannel))
                self.setCurrent(float(sI), sChannel)
            elif x == '3':
                if sChannel == '1':
                    bOutput = self.__bOutputCh1
                elif sChannel == '2':
                    bOutput = self.__bOutputCh2
                if bOutput:
                    self.setOutput(False, sChannel)
                else:
                    self.setOutput(True, sChannel)
