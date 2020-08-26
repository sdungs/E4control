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

    def getEnvTemperature(self, iChannel):
        return(float(self.ask('?T%i' %iChannel)))

    def getEnvHumidity(self, iChannel):
        return(float(self.ask('?H%i' %iChannel)))

    def getNtcTemperature(self, iChannel):
        return(float(self.ask('?N%i' %iChannel)))

    def getDewPoint(self, iChannel):
        return(float(self.ask('?D%i' %iChannel)))

    def output(self, show=True):
        pass

    def interaction(self):
        print('Nothing to do...')
