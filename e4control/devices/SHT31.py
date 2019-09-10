# -*- coding: utf-8 -*-

##############################################################################################################
# IMPORTANT NOTICE:                                                                                          #
# This class for a single Sensirion SHT3x is supposed to be running on the same Raspberry Pi                 #
# to which the SHT3x is connected to via i2c. To achieve a remote read-out temperature/humidity-sensor use   #
# the SHT75 class.                                                                                           #
##############################################################################################################

from .device import Device
import time
import smbus
import numpy as np


class SHT31(Device):
    ADDR = 0x44
    SS = 0x2C
    HIGH = 0x06
    READ = 0x00
    bus = smbus.SMBus(1)

    def __init__(self):
        self.initialize()

    def initialize(self):
        self.bus.write_i2c_block_data(self.ADDR, self.SS, [self.HIGH])
        time.sleep(0.2)

    def getValues(self):
        self.bus.write_i2c_block_data(self.ADDR, self.SS, [self.HIGH])
        time.sleep(0.1)
        rawData = self.bus.read_i2c_block_data(self.ADDR, self.READ, 6)
        t_data = rawData[0] << 8 | rawData[1]
        h_data = rawData[3] << 8 | rawData[4]
        # returns array with [temperature, humidity]
        return [round(-45.0 + 175.0 * np.float(t_data) / 65535.0, 2), round(100.0 * np.float(h_data) / 65535.0, 2)]

    def getTemperature(self):
        return self.getValues()[0]

    def getHumidity(self):
        return self.getValues()[1]

    def output(self, show=True):
        header = ['T1[°C]', 'H1[%]']
        values = self.getValues()
        if show:
            self.printOutput('SHT3x:')
            self.printOutput('sensor 1:\tT: {} °C\tRH: {} %'.format(values[0], values[1]))
        return([header, [str(i) for i in values]])

    def interaction(self):
        print('For this device there is nothing to do...')
