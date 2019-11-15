# -*- coding: utf-8 -*-

from time import sleep

from .device import Device


class ISEG(Device):
    __fVmax = None
    __fImax = None
    softwareRampSpeed_step = 20
    softwareRampSpeed_delay = 1  # [s]

    def __init__(self, connection_type, host, port):
        super(ISEG, self).__init__(connection_type=connection_type, host=host, port=port)
        self.setRampSpeed(100, 1)
        self.setRampSpeed(100, 2)

    def userCmd(self, cmd):
        print('user cmd: %s' % cmd)
        return self.ask(cmd)

    def initialize(self, iChannel=-1):
        s = self.ask('#').split(';')
        self.__fVmax = float(s[2][:-1])
        self.__fImax = float(s[3][:-2])*1E-3

    def setOutput(self, bEnable, iChannel=-1):
        pass

    def getVoltage(self, iChannel):
        sV = self.ask('U%i' % iChannel)
        sV = sV.replace('U%i' % iChannel, '')
        fV = float(sV[:-3])*10**float(sV[-3:])
        return fV

    def getCurrent(self, iChannel):
        sI = self.ask('I%i' % iChannel)
        sI = sI.replace('I%i' % iChannel, '')
        fI = float(sI[:-3])*10**float(sI[-3:])
        return fI

    def setCurrentLimit(self, iChannel):
        # just manual setting possible
        pass

    def setVoltageLimit(self, iChannel):
        # just manual setting possible
        pass

    def getVoltageLimit(self, iChannel):
        if self.__fVmax == None:
            self.initialize()
        sVoltLim = self.ask('M%i' % iChannel)
        sVoltLim = sVoltLim.replace('M%i' % iChannel, '')
        return float(sVoltLim)/100*self.__fVmax # in % of Vout_max

    def getCurrentLimit(self, iChannel):
        if self.__fImax == None:
            self.initialize()
        sCurrentLim = self.ask('N%i' % iChannel)
        sCurrentLim = sCurrentLim.replace('N%i' % iChannel, '')
        return float(sCurrentLim)/100*self.__fImax # in % of Iout_max


    def getSetVoltage(self, iChannel):
        sV = self.ask('D%i' % iChannel)
        sV = sV.replace('D%i' % iChannel, '')
        fV = float(sV[:-3])*10**float(sV[-3:])
        return fV

    def getRampSpeed(self, iChannel):
        sRamp = self.ask('V%i' % iChannel)
        sRamp = sRamp.replace('V%i' % iChannel, '')
        return int(sRamp)

    def setVoltage(self, fValue, iChannel):
        self.ask('D%i=%.1f' % (iChannel, abs(fValue)))
        self.startRampU(iChannel)

    def setRampSpeed(self, iRampSpeed, iChannel):
        if iRampSpeed < 1 or iRampSpeed > 255:
            print('Set RampSpeed is out of range!')
        else:
            self.ask('V%i=%i' % (iChannel, iRampSpeed))

    def setSoftwareRampSpeed(self, iRampSpeed, iDelay):
        if iRampSpeed < 1 or iRampSpeed > 255:
            print('Set RampSpeed size is out of range!')
        else:
            self.softwareRampSpeed_step = iRampSpeed
        if iDelay < 0:
            print('No negativ Delay is possible!')
        else:
            self.softwareRampSpeed_delay = iDelay

    def getSoftwareRampSpeed(self):
        return([int(self.softwareRampSpeed_step), int(self.softwareRampSpeed_delay)])

    def rampVoltage(self, fVnew, iChannel):
        fVnew = abs(fVnew)
        V = self.getVoltage(iChannel)
        V = round(V, 4)
        if abs(fVnew-abs(V)) <= self.softwareRampSpeed_step:
            self.setVoltage(fVnew, iChannel)
            print('Voltage reached: %.2f V' % fVnew)
        else:
            self.setVoltage(abs(V)+self.softwareRampSpeed_step*(fVnew-abs(V))/abs(fVnew-abs(V)), iChannel)
            print('Ramp Voltage: %.2f V' % (abs(V)+self.softwareRampSpeed_step*(fVnew-abs(V))/abs(fVnew-abs(V))))
            sleep(self.softwareRampSpeed_delay)
            self.rampVoltage(fVnew, iChannel)

    def getStatus(self, iChannel):
        s = self.ask('S%i' % iChannel)
        s = s.replace('S%i=' % iChannel, '=')
        return s

    def startRampU(self, iChannel):
        sRamp = self.ask('G%i' % iChannel)
        sRamp = sRamp.replace('G%i' % iChannel, '')
        print(sRamp)

    def output(self, show=True):
        if self.__fVmax==None or self.__fImax==None:
            self.initialize()
        fLimit1 = self.getCurrentLimit(1) * 1E6
        fLimit2 = self.getCurrentLimit(2) * 1E6
        fVoltage1 = self.getVoltage(1)
        fVoltage2 = self.getVoltage(2)
        fCurrent1 = self.getCurrent(1) * 1E6
        fCurrent2 = self.getCurrent(2) * 1E6

        if show:
            self.printOutput('ISEG:')
            self.printOutput('          \t {:10} \t {:10}'.format('Channel 1','Channel 2'))
            self.printOutput('Voltage:  \t {:6.5} V  \t {:6.5} V '.format(fVoltage1,fVoltage2))
            self.printOutput('Current:  \t {:6.5} uA \t {:6.5} uA'.format(fCurrent1,fCurrent2))
            # I found no posiblitiy to check wich limit range is active :(
            self.printOutput('Limit (range uA): {:5.0f} uA \t {:6.0f} uA'.format(fLimit1/self.__fImax*100E-6,fLimit2/self.__fImax*100E-6))
            self.printOutput('Limit (range mA): {:5.0f} uA \t {:6.0f} uA'.format(fLimit1,fLimit2))
        return([['Ilim1[uA]', 'U1[V]', 'I1[uA]', 'Ilim2[uA]', 'U2[V]', 'I2[uA]'], [str(fLimit1), str(fVoltage1), str(fCurrent1), str(fLimit2), str(fVoltage2), str(fCurrent2)]])

    def interaction(self):
        print(
            'ISEG selected.'
            )
        sChannel = input('Which channel? \n')
        while not (sChannel in ['1','2']):
            sChannel = input('Possible Channels: 1 or 2! \n')
        iChannel = int(sChannel)
        print(
            'Possible actions:\n'
            '0: Continue dcs mode without any changes\n'
            '1: Set voltage\n'
            '2: Get status (try this if you have fixed your limit issues and still get "S{}=ERR" when ramping voltages)'.format(sChannel)
            )
        x = input('Number? \n')
        while not (x in ['0','1','2']):
            x = input('Possible Inputs: 0, 1, 2! \n')
        if x == '0':
            pass
        elif x == '1':
            fV = input('Please enter new Voltage (in V) for Channel {}.\n'.format(sChannel))
            self.rampVoltage(float(fV), iChannel)
        elif x == '2':
            print('ISEG status: "{}"'.format(self.getStatus(iChannel)))
