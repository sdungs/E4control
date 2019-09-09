# -*- coding: utf-8 -*-

from .device import Device
from subprocess import call
from time import sleep


class SHT75(Device):

    def __init__(self, connection_type, host, port):
        # this requires to run bash on the host, not dash (RasPi default!)
        # and screen has to be installed on the server-side / RasPi
        # remember to make the StartServer.sh executable!
        super(SHT75, self).__init__(connection_type=connection_type, host=host, port=port)
        userAtHost = 'labuser@{}'.format(self.host)
        call(["ssh", userAtHost, " ~/software/E4control/e4control/devices/StartServer.sh"])
        sleep(0.4) # This is to give the RasPi some time to start up properply
        self.trm = ''

        # How to create a rsa-keypair to log on without password:
        # ssh-keygen
        # ssh-copy-id user@host

    def initialize(self, sMode='H'):
        pass

    def userCmd(self, cmd):
        data = cmd.encode('utf-8')
        data = self.ask(cmd)
        return data.decode('utf-8')

    def getValues(self, channels=0):  # Each channel equals one sensor, thus touple of (Temperature, Humidity). 0 equals each channel
        sleep(0.5)
        if channels == 0:
            data = self.ask('READ')
        else:
            data = self.ask('READ{}'.format(channels))
        data = data.split(',')
        return [float(i) for i in data]

    def getTemperature(self, channels=0):
        data = self.getValues(channels)
        data = data[::2]
        if len(data) == 1:
            return data[0]
        else:
            return data

    def getHumidity(self, channels=0):
        data = self.getValues(channels)
        data = data[1::2]
        if len(data) == 1:
            return data[0]
        else:
            return data

    def close(self):
        self.write('CLOSE')

    def output(self, show=True):
        header = ['T1[°C]', 'H1[%]', 'T2[°C]', 'H2[%]']
        values = self.getValues()
        if show:
            self.printOutput('SHT75:')
            self.printOutput('Sensor 1:\tT: {} °C\tRH: {} %'.format(values[0],values[1]))
            self.printOutput('Sensor 2:\tT: {} °C\tRH: {} %'.format(values[2],values[3]))
        return([header, [str(i) for i in values]])

    def interaction(self):
        print('For this device there is nothing to do...')
