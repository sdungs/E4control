# -*- coding: utf-8 -*-
from time import sleep
from .device import Device


class MOTH(Device):

    def __init__(self, connection_type, host, port):
        super(MOTH, self).__init__(connection_type=connection_type, host=host, port=port)
        sleep(2)

    def userCmd(self, cmd):
        print('user cmd: %s' % cmd)
        return self.ask(cmd)

    def initialize(self):
        pass

    def getEnvTemperature(self):
        return(self.ask('?T'))

    def getEnvHumidity(self):
        return(self.ask('?H'))

    def getNtcTemperature(self):
        return(self.ask('?N'))

    def getDewPoint(self):
        return(self.ask('?D'))

    def output(self, show=True):
        pass

    def interaction(self):
        print('Nothing to do...')
