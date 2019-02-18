# -*- coding: utf-8 -*-

from .device import Device
from PyCRC.CRCCCITT import CRCCCITT
import time

class TEC1123(Device):

    def __init__(self, connection_type, host, port, baudrate=57600):
        super(TEC1123, self).__init__(connection_type=connection_type, host=host, port=port, baudrate=*baudrate)
