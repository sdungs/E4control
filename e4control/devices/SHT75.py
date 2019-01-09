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

    def getHumidity(self, channels=1):
        data = self.getValues(channels)
        return data[1::2]

    def close(self):
        self.write('CLOSE')
        pass


# How to create a rsa-keypair to log on without password:
# ssh-keygen
# ssh-copy-id user@host
