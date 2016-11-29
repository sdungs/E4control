#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vxi11 #for gpib
import pylink #for serial and lan
from pylink import TCPLink
#import pyUSB (for USB connection)

class DEVICE:
    com = None
    trm = "\r\n"
    kind = None
    adress = None
    port = None

    def __init__(self,kind,adress,port):
        self.kind = kind
        self.adress = adress
        self.port = port

        if (kind == "serial"):
            self.com = TCPLink(adress, port)
            pass
        elif (kind == "lan"):
            self.com = TCPLink(adress, port)
            pass
        elif (kind == "gpib"):
            sPort="gpib0,%i"%port
            self.com = vxi11.Instrument(adress, sPort)
            pass
        pass

    def open(self):
        self.com.open()
        pass

    def close(self):
        self.com.close()
        pass

    def reconnect(self):
        self.close()
        self.open()
        pass

    def read(self):
        s = ""
        try:
            s = self.com.read()
            s = s.replace("\r","")
            s = s.replace("\n","")
            return s
        except:
            print("Timeout while reading!")
            pass
        return s

    def write(self,cmd):
        cmd = cmd + self.trm
        try:
            self.com.write(cmd)
        except:
            self.reconnect()
            try:
                self.com.write(cmd)
            except:
                print("Timeout while writeing")
        pass

    def ask(self,cmd):
        self.write(cmd)
        return self.read()
