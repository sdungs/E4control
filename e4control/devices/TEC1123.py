# -*- coding: utf-8 -*-

from .device import Device
from PyCRC.CRCCCITT import CRCCCITT
import time
from struct import pack, unpack
from time import sleep


class TEC1123(Device):
    trm = '\r'.encode()
    adress = 0
    sequence = 0xE4E4
    channels = [1,2]
    Power  = []
    T_set = []

    def __init__(self, connection_type, host, port, baudrate=57600, timeout=1):
        super(TEC1123, self).__init__(connection_type=connection_type, host=host, port=port, baudrate=baudrate, timeout=timeout)
        self.getAndSetParameter()

    def read(self):
        return self.com.read_until('\r'.encode())

    def buildFrame(self, param, channel, set=False, reset=False, **kwargs):  # **kwargs for value to be set
        frame = '#' + '{:02X}{:04X}'.format(self.adress, self.sequence)
        if not set:  # read-ony operation
            payload = '?VR{:04X}{:02d}'.format(self.PARAMETERS[str(param)]['id'], channel)
        if set:
            payload = 'VS{:04X}{:02d}'.format(self.PARAMETERS[str(param)]['id'], channel)
            if self.PARAMETERS[str(param)]['format'] == 'INT32':
                payload += '{:08d}'.format(kwargs.get('value'))
            elif self.PARAMETERS[str(param)]['format'] == 'FLOAT32':
                payload += '{:08X}'.format(unpack('<I', pack('<f', kwargs.get('value')))[0])
        if reset:
            payload += 'RS'
        frame += payload
        frame += self.buildCheckSum(frame)
        return frame.encode()

    def buildCheckSum(self, frame):
        return '{:04X}'.format(CRCCCITT().calculate(input_data=frame))

    # def buildPayload(self, param, channel, set=False, **kwargs):  # **kwargs for value to be set
    #     if not set:  # read-ony operation
    #         payload = '?VR{:04X}{:02d}'.format(self.PARAMETERS[str(param)]['id'], channel)
    #     if set:
    #         payload = 'VS{:04X}{:02d}'.format(self.PARAMETERS[str(param)]['id'], channel)
    #         if self.PARAMETERS[str(param)]['format'] == 'INT32':
    #             payload += '{:08d}'.format(kwargs.get('value'))
    #         elif self.PARAMETERS[str(param)]['format'] == 'FLOAT32':
    #             payload += '{:08X}'.format(unpack('<I', pack('<f', kwargs.get('value')))[0])
    #     return payload

    def getAndSetParameter(self):
        self.getPowerStatus()
        self.getSetTemperature()
        pass

    def getPowerStatus(self):
        self.Power = []
        for i in self.channels:
            answ = self.ask(
                self.buildFrame(104, i))
            if unpack('I', pack('I', int(answ[7:15], 16)))[0] == 2:
                self.Power.append(True)
            else:
                self.Power.append(False)
        return self.Power

    def resetDevice(self):
        self.ask(self.buildFrame(104, 1, reset=True))
        sleep(1)
        self.getAndSetParameter()
        pass

    def enablePower(self, channel, sBool):
        self.ask(self.buildFrame(2010, channel, set=True, value=sBool))
        self.Power[channel - 1] = sBool

    def getTemperature(self, channel=1):
        cmd = self.buildFrame(1000, channel)
        answ = self.ask(cmd)
        return round(unpack('f', pack('I', int(answ[7:15], 16)))[0], 2)

    def getSetTemperature(self, *args):  # channelnumber as *args if only 1 should be returned
        self.T_set = []
        for i in self.channels:
            answ = self.ask(self.buildFrame(1010, i))
            self.T_set.append(round(unpack('f', pack('I', int(answ[7:15], 16)))[0], 2))
        if args:
            return self.T_set[args[0] - 1]
        else:
            return self.T_set

    def AutoTune(self, channel):
        self.ask(self.buildFrame(51000, channel, set=True, value=1))
        sleep(1)
        while self.ask(self.buildFrame(51021, channel)) < 100:
            print(self.ask(self.buildFrame(51021, channel)))
            sleep(5)

    def setTemperature(self, channel, fValue):
        self.ask(self.buildFrame(3000, channel, set=True, value=fValue))
        pass

    def getCurrent(self, channel=1):
        values = []
        for i in self.channels:
            answ = self.ask(self.buildFrame(1020, channel))
            values.append(round(unpack('f', pack('I', int(answ[7:15], 16)))[0], 2))
            return values

    def getVoltage(self, channel=1):
        values = []
        for i in self.channels:
            answ = self.ask(self.buildFrame(1021, channel))
            values.append(round(unpack('f', pack('I', int(answ[7:15], 16)))[0], 2))
            return values

    PARAMETERS = {
        # Device Identification
        '104': dict([('id', 104), ('name', 'Device Status'), ('format', 'INT32')]),
        '105': dict([('id', 105), ('name', 'Error Number'), ('format', 'INT32')]),
        '106': dict([('id', 106), ('name', 'Error Instance'), ('format', 'INT32')]),
        '107': dict([('id', 107), ('name', 'Error Parameter'), ('format', 'INT32')]),
        '108': dict([('id', 108), ('name', 'Save Data To Flash'), ('format', 'INT32')]),
        '109': dict([('id', 109), ('name', 'Flash Status'), ('format', 'INT32')]),  # 0 = Enabled, 1 = Disabled
        # Temperature Measurement
        '1000': dict([('id', 1000), ('name', 'Object Temperature'), ('format', 'FLOAT32')]),
        '1001': dict([('id', 1001), ('name', 'Sink Temperature'), ('format', 'FLOAT32')]),
        '1010': dict([('id', 1010), ('name', 'Target Object Temperature'), ('format', 'FLOAT32')]),
        '1011': dict([('id', 1011), ('name', 'Ramp Object Temperature'), ('format', 'FLOAT32')]),
        '1020': dict([('id', 1020), ('name', 'Actual Output Current'), ('format', 'FLOAT32')]),
        '1021': dict([('id', 1021), ('name', 'Actual Output Voltage'), ('format', 'FLOAT32')]),
        # Object Temperature Stability Detection
        '1200': dict([('id', 1200), ('name', 'Temperature Is Stable'), ('format', 'INT32')]),
        # Output Stage Control
        '2010': dict([('id', 2010), ('name', 'Status'), ('format', 'INT32')]),
        '2030': dict([('id', 2030), ('name', 'Current Limitation'), ('format', 'FLOAT32')]),
        '2031': dict([('id', 1001), ('name', 'Voltage Limitation'), ('format', 'FLOAT32')]),
        '2032': dict([('id', 2032), ('name', 'Current Error Threshold'), ('format', 'FLOAT32')]),
        '2033': dict([('id', 2033), ('name', 'Voltage Error Threshold'), ('format', 'FLOAT32')]),
        '2040': dict([('id', 2040), ('name', 'General Operation Mode'), ('format', 'FLOAT32')]),  # 0 = Independent, 1 = Parallel, Individual loads
        '2051': dict([('id', 2051), ('name', 'Device Address'), ('format', 'FLOAT32')]),
        # Temperature Control Settings
        '3000': dict([('id', 3000), ('name', 'Target Object Temp (set)'), ('format', 'FLOAT32')]),
        '3003': dict([('id', 3003), ('name', 'Coarse Temp Ramp'), ('format', 'FLOAT32')]),
        '3010': dict([('id', 3010), ('name', 'Kp'), ('format', 'FLOAT32')]),
        '3011': dict([('id', 3011), ('name', 'Ti'), ('format', 'FLOAT32')]),
        '3012': dict([('id', 3012), ('name', 'Td'), ('format', 'FLOAT32')]),
        # Peltier Characteristics
        '3020': dict([('id', 3020), ('name', 'Mode'), ('format', 'INT32')]),  # 0 = Peltier, Full Control
        '3030': dict([('id', 3030), ('name', 'Maximal Current Imax'), ('format', 'FLOAT32')]),
        '3033': dict([('id', 3033), ('name', 'Delta Temperature max'), ('format', 'FLOAT32')]),
        '3034': dict([('id', 3034), ('name', 'Positive Current is'), ('format', 'INT32')]),  # 0 = Cooling, 1 = Heating
        # Object Temperature Limit
        '4034': dict([('id', 4034), ('name', 'Object Sensor Type'), ('format', 'INT32')]),  # 0 = Unknown, 1 = Pt101, 2 = Pt1000
        # Auto Tuning
        '51000': dict([('id', 51000), ('name', 'Auto Tuning Start'), ('format', 'INT32')]),  # Write 1 to start the process
        '51001': dict([('id', 51001), ('name', 'Auto Tuning Cancel'), ('format', 'INT32')]),  # Write 1 to cancel process
        '51002': dict([('id', 51002), ('name', 'Thermal Mode Speed'), ('format', 'INT32')]),  # 0 = Fast Model, 1 = Slow Model
        '51014': dict([('id', 51014), ('name', 'PID Parameter Kp'), ('format', 'FLOAT32')]),  # read-only
        '51015': dict([('id', 51015), ('name', 'PID Parameter Ti'), ('format', 'FLOAT32')]),  # read-only
        '51016': dict([('id', 51016), ('name', 'PID Parameter Td'), ('format', 'FLOAT32')]),  # read-only
        # read-only, return recommended value for target coarse temp
        '51017': dict([('id', 51017), ('name', 'Coarse Temp Ramp'), ('format', 'FLOAT32')]),
        # read-only, 0 = Idle, 1 = Ramping to Target, 2 = Preparing, 3 = Acquiring data, 4 = Success, 10 = Error
        '51020': dict([('id', 51020), ('name', 'Tuning Status'), ('format', 'INT32')]),
        '51021': dict([('id', 51021), ('name', 'Tuning Status (%)'), ('format', 'FLOAT32')]),
        '6310': dict([('id', 6310), ('name', 'Delay Until Restart'), ('format', 'FLOAT32')]),  # error state auto restart delay in [s]
    }

    ERRORS = {
        '1': dict([('code', 1), ('symbol', 'ERR_CMD_NOT_AVAILABLE'), ('description', 'Command not available')]),
        '2': dict([('code', 2), ('symbol', 'ERR_DEVICE_BUSY'), ('description', 'Device is busy')]),
        '3': dict([('code', 3), ('symbol', 'ERR_GENERAL_COM'), ('description', 'General communication error')]),
        '4': dict([('code', 4), ('symbol', 'ERR_FORMAT'), ('description', 'Format error')]),
        '5': dict([('code', 5), ('symbol', 'ERR_CMD_NOT_AVAILABLE'), ('description', 'Parameter is not available')]),
        '6': dict([('code', 6), ('symbol', 'EERR_PAR_NOT_WRITABLE'), ('description', 'Parameter is read-only')]),
        '7': dict([('code', 7), ('symbol', 'ERR_PAR_OUT_OF_RANGE'), ('description', 'Value is out of range')]),
        '8': dict([('code', 8), ('symbol', 'ERR_PAR_INST_NOT_AVAILABLE'), ('description', 'Parameter is read-only')]),
    }
