# -*- coding: utf-8 -*-

from socket import socket
from .device import Device
from subprocess import call


class SHT75(Device):
    dv = None

    def __init__(self, connection_type, host, port):
        # this requires to run bash on the host, not dash (RasPi default!)
        # and screen has to be installed on the server-side / RasPi
        # remember to make the StartServer.sh executable!
        super(SHT75, self).__init__(connection_type=connection_type, host=host, port=port)
        userAtHost = str("labuser@%s") % (self.host)
        call(["ssh", userAtHost, " ~/software/E4control/e4control/devices/StartServer.sh"])
        self.trm = ''

    def initialize(self):
        pass

    def userCmd(self, cmd):
        data = cmd.encode('utf-8')
        data = self.ask(cmd)
        data = data.decode('utf-8')
        return data

    def getValues(self, channels=1):  # one channels equals one sensor, thus touple of (Temperature, Humidity)
        if channels == 1:
            data = self.ask('READ')
        elif channels == 2:
            data = self.ask('READ2')
        data = data.split(',')
        buffer = []
        buffer.append(float(data[0]))
        buffer.append(float(data[1]))
        if channels == 2:
            buffer.append(float(data[2]))
            buffer.append(float(data[3]))
        return buffer

    def getTemperature(self, channels=1):
        if channels == 1:
            data = self.ask('READ')
        elif channels == 2:
            data = self.ask('READ2')
        elif channels == 3:
            data = self.ask('READ3')
        data = data.split(',')
        temp = []
        temp.append(float(data[0]))
        if channels >= 2:
            temp.append(float(data[2]))
        if channels == 3:
            temp.append(float(data[4]))
        return temp

    def getHumidity(self, channels=1):
        if channels == 1:
            data = self.ask('READ')
        elif channels == 2:
            data = self.ask('READ2')
        elif channels == 3:
            data = self.ask('READ3')
            data = data.split(',')
        elif channels == 3:
            data = self.ask('READ3')
        data = data.split(',')
        hum = []
        hum.append(float(data[1]))
        if channels >= 2:
            hum.append(float(data[3]))
        if channels == 3:
            hum.append(float(data[5]))
        return hum


# How to create a rsa-keypair to log on without password:
# ssh-keygen
# ssh-copy-id user@host
