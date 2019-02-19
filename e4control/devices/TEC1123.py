# -*- coding: utf-8 -*-

from .device import Device
from PyCRC.CRCCCITT import CRCCCITT
import time


class TEC1123(Device):
    self.trm = '\r'

    def __init__(self, connection_type, host, port, baudrate=57600, timeout=1):
        super(TEC1123, self).__init__(connection_type=connection_type, host=host, port=port, baudrate=baudrate, timeout=timeout)

    def compose(self, part=False):
        """
        Returns the frame as bytes, the return-value can be directly send via serial.
        :param part: bool
        :return: bytes
        """
        # first part
        frame = self._SOURCE + "{:02X}".format(self.ADDRESS) + "{:04X}".format(self.SEQUENCE)
        # payload can be str or float or int
        for p in self.PAYLOAD:
            if type(p) is str:
                frame += p
            elif type(p) is int:
                frame += "{:08X}".format(p)
            elif type(p) is float:
                # frame += hex(unpack('<I', pack('<f', p))[0])[2:].upper()  # please do not ask
                # if p = 0 CRC fails, e.g. !01000400000000 composes to b'!0100040' / missing zero padding
                frame += '{:08X}'.format(unpack('<I', pack('<f', p))[0])  # still do not aks
        # if we only want a partial frame, return here
        if part:
            return frame.encode()
        # add checksum
        if self.CRC is None:
            self.crc()
        frame += "{:04X}".format(self.CRC)
        # add end of line (carriage return)
        frame += self._EOL
        return frame.encode()

    PARAMETERS = [
        # Device Identification
        {"id": 104, "name": "Device Status", "format": "INT32"},
        {"id": 108, "name": "Save Data to Flash", "format": "INT32"},
        {"id": 109, "name": "Flash Status", "format": "INT32"},  # 0 = Enabled, 1 = Disabled
        # Temperature Measurement
        {"id": 1000, "name": "Object Temperature", "format": "FLOAT32"},
        {"id": 1001, "name": "Sink Temperature", "format": "FLOAT32"},
        {"id": 1010, "name": "Target Object Temperature", "format": "FLOAT32"},
        {"id": 1011, "name": "Ramp Object Temperature", "format": "FLOAT32"},
        {"id": 1020, "name": "Actual Output Current", "format": "FLOAT32"},
        {"id": 1021, "name": "Actual Output Voltage", "format": "FLOAT32"},
        # Object TEmperature Stability Detection
        {"id": 1200, "name": "Temperature is Stable", "format": "INT32"},
        # Output Stage Control
        {"id": 2010, "name": "Status", "format": "INT32"},
        {"id": 2030, "name": "Current Limitation", "format": "FLOAT32"},
        {"id": 2031, "name": "Voltage Limitation", "format": "FLOAT32"},
        {"id": 2032, "name": "Current Error Threshold", "format": "FLOAT32"},
        {"id": 2033, "name": "Voltage Error Threshold", "format": "FLOAT32"},
        {"id": 2040, "name": "General Operating Mode", "format": "INT32"},  # 0 = Independent, 1 = Parallel, Individual loads
        {"id": 2051, "name": "Device Address", "format": "INT32"},
        # Temperature Control and Settings
        {"id": 3000, "name": "Target Object Temp (Set)", "format": "FLOAT32"},
        {"id": 3003, "name": "Coarse Temp Ramp", "format": "FLOAT32"},
        {"id": 3010, "name": "Kp", "format": "FLOAT32"},
        {"id": 3011, "name": "Ti", "format": "FLOAT32"},
        {"id": 3012, "name": "Td", "format": "FLOAT32"},
        # Peltier Characteristics
        {"id": 3020, "name": "Mode", "format": "INT32"},  # 0 = Peltier, Full Control
        {"id": 3030, "name": "Maximal Current Imax", "format": "FLOAT32"},
        {"id": 3033, "name": "Delta Temperature max", "format": "FLOAT32"},
        {"id": 3034, "name": "Positive Current is", "format": "INT32"},  # 0 = Cooling, 1 = Heating
        # Object Temperature Measument Limit
        {"id": 4034, "name": "Object Sensor Type", "format": "INT32"},  # 0 = Unknown, 1 = Pt101, 2 = Pt1000
        # Auto Tuning
        {"id": 51000, "name": "Auto Tuning Start", "format": "INT32"},  # Write 1 to start the process
        {"id": 51001, "name": "Auto Tuning Cancel", "format": "INT32"},  # Write 1 to cancel process
        {"id": 51002, "name": "Thermal Model Speed", "format": "INT32"},  # 0 = Fast Model, 1 = Slow Model
        {"id": 51014, "name": "PID Parameter Kp", "format": "FLOAT32"},  # read-only
        {"id": 51015, "name": "PID Parameter Ti", "format": "FLOAT32"},  # read-only
        {"id": 51016, "name": "PID Parameter Td", "format": "FLOAT32"},  # read-only
        {"id": 51017, "name": "Corase Temp Remp", "format": "FLOAT32"},  # read-only, returns recommended value for target coarse temp
        {"id": 51020, "name": "Tuning Status", "format": "INT32"},  # read-only, 0 = Idle, 1 = Ramping to Target, 2 = Preparing, 3 = Acquiring data, 4 = Success, 10 = Error
        {"id": 51021, "name": "Tuning Process (%)", "format": "FLOAT32"},  # read-only,
        {"id": 6310, "name": "Delay till Restart", "format": "FLOAT32"},  # error state auto restart delay, ins [s]
    ]


ERRORS = [
    {"code": 1, "symbol": "EER_CMD_NOT_AVAILABLE", "description": "Command not available"},
    {"code": 2, "symbol": "EER_DEVICE_BUSY", "description": "Device is busy"},
    {"code": 3, "symbol": "ERR_GENERAL_COM", "description": "General communication error"},
    {"code": 4, "symbol": "EER_FORMAT", "description": "Format error"},
    {"code": 5, "symbol": "EER_PAR_NOT_AVAILABLE", "description": "Parameter is not available"},
    {"code": 6, "symbol": "EER_PAR_NOT_WRITABLE", "description": "Parameter is read only"},
    {"code": 7, "symbol": "EER_PAR_OUT_OF_RANGE", "description": "Value is out of range"},
    {"code": 8, "symbol": "EER_PAR_INST_NOT_AVAILABLE", "description": "Parameter is read only"},
]
