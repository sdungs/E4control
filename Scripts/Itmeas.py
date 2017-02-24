#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import signal
import argparse

sys.path.append("./../Devices/")
from DEVICE import DEVICE
from K196 import K196
from K2410 import K2410

#arg parser
parser=argparse.ArgumentParser()
parser.add_argument("output",help="output file")
parser.add_argument("-v","--voltage",type=float,default=-300)
parser.add_argument("-d","--delay",type=int,default=60)
parser.add_argument("-n","--ndaqs",type=int,default=5)
args=parser.parse_args()

#signal handler
cont = True
def signal_handler(signal, frame):
    print("Measurement stopped!")
    global cont
    cont = False
    return

signal.signal(signal.SIGINT, signal_handler)

#devices
s = K2410("serial","serial01",1002)
s.initialize(-1)
s.setVoltage(0,-1)
s.enableOutput(True,-1)
t = K196("gpib", "gpib03", 9)
t.initialize("T")

#ramp to const bias voltage
s.rampVoltage(args.voltage,-1)

#open txt file
fw = open("%s.txt" %args.output,"w")
fw.write("t[s] \t U[V] \t I[uA] \t T[C] \n")
fw.flush()

while cont:
    for j in xrange(args.ndaqs):
        timestamp = time.time()
        voltage = s.getVoltage(-1)
        current = s.getCurrent(-1)
        temperature = t.getTempPT1000(-1)
        print("%f \t %f \t %f \t %f \n"%(timestamp, voltage, current, temperature))
        fw.write("%f \t %f \t %f \t %f \n"%(timestamp, voltage, current, temperature))
        fw.flush()
    time.sleep(args.delay)

#ramp down bias voltage
s.rampVoltage(0,-1)
s.enableOutput(False)

#close
fw.close
s.close()
t.close()
