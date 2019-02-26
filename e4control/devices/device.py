# -*- coding: utf-8 -*-

import sys
import vxi11
from pylink import TCPLink
import serial
from time import sleep
from .prologix import Prologix


class Device(object):
    com = None
    trm = '\r\n'
    connection_type = None
    host = None
    port = None

    def __init__(self, connection_type, host, port, **kwargs):
        # *kwargs can be used to specify baudrate other than 9600
        self.connection_type = connection_type
        self.host = host
        self.port = port

        if (connection_type == 'serial'):
            self.com = TCPLink(host, port)
        elif (connection_type == 'lan'):
            self.com = TCPLink(host, port)
        elif (connection_type == 'gpib'):
            sPort = 'gpib0,%i' % port
            self.com = vxi11.Instrument(host, sPort)
        elif (connection_type == 'gpibSerial'):
            sPort = 'COM1,488'
            # This probably will solely work with Keysight E5810B
            self.com = vxi11.Instrument(host, sPort)
        elif (connection_type == 'usb'):
            if 'baudrate' in kwargs:
                self.com = serial.Serial(host, kwargs.get('baudrate'))
            elif 'baudrate' and 'timeout' in kwargs:
                self.com = serial.Serial(host, baudrate=kwargs.get('baudrate'),
                                         timeout=kwargs.get('timeout'), write_timeout=kwargs.get('timeout'))
            else:
                self.com = serial.Serial(host, 9600)
        elif (connection_type == 'prologix'):
            self.com = Prologix(host, port)
            self.com.open()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open(self):
        self.com.open()

    def close(self):
        self.com.close()

    def reconnect(self):
        self.close()
        self.open()
        sleep(0.5)

    def read(self):
        try:
            if self.connection_type == 'usb':
                s = self.com.readline()
            else:
                s = self.com.read()
        except:
            print('First reading attempt failed, trying again...')
            try:
                if self.connection_type == 'usb':
                    s = self.com.readline()
                else:
                    s = self.com.read()
            except:
                print('Timeout while reading from device!')
                raise
        s = s.replace('\r', '')
        s = s.replace('\n', '')
        return s

    def write(self, cmd):
        cmd = cmd + self.trm
        self.com.write(cmd)
        # try:
        #     self.com.write(cmd)
        # except:
        #     self.reconnect()
        #     try:
        #         self.com.write(cmd)
        #     except:
        #         print('Timeout while writing')

    def ask(self, cmd):
        self.write(cmd)
        return self.read()

    def printOutput(self, string):
        sys.stdout.write(string + '\r\n')
