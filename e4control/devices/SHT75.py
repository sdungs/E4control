# -*- coding: utf-8 -*-

from socket import socket
from .device import Device
from subprocess import call


class SHT75(Device):

    def __init__(self, connection_type, host, port):
        # this requires to run bash on the host, not dash (RasPi default!)
        # and screen has to be installed on the server-side / RasPi
        # remember to make the StartServer.sh executable!
        super(SHT75, self).__init__(connection_type=connection_type, host=host, port=port)
        userAtHost = 'labuser@{}'.format(self.host)
        call(["ssh", userAtHost, " ~/software/E4control/e4control/devices/StartServer.sh"])
        self.trm = ''

    def initialize(self):
        pass

    def userCmd(self, cmd):
        data = cmd.encode('utf-8')
        data = self.ask(cmd)
        return data.decode('utf-8')

    def getValues(self, channels=0):  # Each channel equals one sensor, thus touple of (Temperature, Humidity). 0 equals each channel
        if channels == 0:
            data = self.ask('READ')
        else:
            data = self.ask('READ{}'.format(channels))
        data = data.split(',')
        return [float(i) for i in data]

    def getTemperature(self, channels=0):
        data = self.getValues(channels)
        return data[::2]

    def getHumidity(self, channels=0):
        data = self.getValues(channels)
        return data[1::2]

    def close(self):
        self.write('CLOSE')
        pass

    def output(self, show=True):
        header = ['T1[°C]','H1[%]','T2[°C]','H2[%]']
        values = self.getValues()
        if show:
            print('SHT75:')
            print('sensor 1:\tT: {} °C\tRH: {} %'.format(values[0],values[1]))
            print('sensor 2:\tT: {} °C\tRH: {} %'.format(values[2],values[3]))

        return([header, [str(i) for i in values]])

    def interaction(self):
        print('For this device there is nothing to do...')


# How to create a rsa-keypair to log on without password:
# ssh-keygen
# ssh-copy-id user@host
