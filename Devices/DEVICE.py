#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vxi11 #for gpib
import pylink #for serial and lan
from pylink import TCPLink
#import pyUSB (for USB connection)

class DEVICE:
    com = None
    trm = "\r\n"

    def __init__(self,kind,adress,port):
        if (kind == "serial"):
            self.com = TCPLink(adress, port)
            pass
        elif (kind == "lan"):
            self.com = TCPLink(adress, port)
            pass
        elif (kind == "gpib"):
            self.com = vxi11.Instrument(adress, port)
            pass
        pass

    def open(self):
        self.com.open()
        pass

    def close(self):
        self.com.close()
        pass

    def read(self):
        s = ""
        try:
            s = self.com.read()
            if self.verbose: print("DEVICE::read : %s" % s)
            return s
        except:
            if self.verbose: print("DEVICE::read : TIMEOUT")
            pass
        return s

    def write(self,cmd):
        cmd = cmd + self.trm
        self.com.write(cmd)
        if self.verbose: print("DEVICE::write : %s" %cmd)
        pass

    def ask(self,cmd):
        self.write(cmd)
        return self.read()
