#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import script_header as sh
import argparse
import time
import signal

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import sem

parser=argparse.ArgumentParser()
parser.add_argument("v_min",help="min voltage (V)",type=float)
parser.add_argument("v_max",help="max voltage (V)",type=float)
parser.add_argument("output",help="output file")
parser.add_argument("config",help="config file")
parser.add_argument("-I","--I_lim",help="current limit (uA)",type=float,default=3)
parser.add_argument("-s","--v_steps",help="number of volt steps",type=int,default=1)
parser.add_argument("-n","--ndaqs",type=int,default=10)
args=parser.parse_args()

#signal handler
cont = True
def signal_handler(signal, frame):
    print("Measurement stopped!")
    global cont
    cont = False
    return
signal.signal(signal.SIGINT, signal_handler)

#read configfile
devices = sh.read_config(args.config)

#create setting query
sh.settings_query(devices, v_min = args.v_min, v_max = args.v_max, v_steps = args.v_steps, I_lim = args.I_lim, ndaqs = args.ndaqs)

#connection
source, source_channel = sh.device_connection(devices["S"])
temperature = []
temperature_channel = []
humidity = []
humidity_channel = []
Vmeter = []
Vmeter_channel = []
if devices["T"]:
    temperature, temperature_channel = sh.device_connection(devices["T"])
if devices["H"]:
    humidity, humidity_channel = sh.device_connection(devices["H"])
if devices["V"]:
    Vmeter, Vmeter_channel = sh.device_connection(devices["V"])

#set active source
d = source[0]
ch = source_channel[0]

#initialize
d.initialize(ch)
d.setVoltage(0,ch)
d.enableOutput(True,ch)
for t in temperature:
    t.initialize("T")
for h in humidity:
    h.initialize("H")
for v in Vmeter:
    v.initialize("V")

#Check Current limit
sh.check_limits(d,ch, I_lim = args.I_lim)

#create directory
argsoutput = sh.check_outputname(args.output)
if not os.path.isdir(argsoutput): os.mkdir(argsoutput)
os.chdir(argsoutput)

#create outputfile
outputname = argsoutput.split("/")[-1]
fw = sh.new_txt_file(outputname)
header = ["time","no.","U[V]","I[uA]"]
for n in range(len(temperature)):
    if temperature_channel[n] == 50:
        header.append("T[C]")
        header.append("T[C]")
        header.append("T[C]")
        header.append("T[C]")
        header.append("T[C]")
    else:
        header.append("T[C]")
for h in humidity:
    header.append("H[V]")
for v in Vmeter:
    header.append("V[V]")
sh.write_line(fw,header)

#create value arrays
Us = []
Imeans = []
Irms = []
Is = []
Ns = []
Ts = []
Hs = []
Vs = []

softLimit = False

#start measurement
i = 1
while i <= args.v_steps and cont:
    voltage = args.v_min + (args.v_max-args.v_min)/(args.v_steps-1)*i
    print "Set voltage: %.2f V" % voltage
    d.rampVoltage(voltage,ch)
    time.sleep(1)
    Is = []
    Ns = []
    Ts = []
    Hs = []
    Vs = []
    for n in range(len(temperature)):
        if temperature_channel[n] == 50:
            ts = t.getTempPT1000all()
            Ts.append(ts[0])
            Ts.append(ts[1])
            Ts.append(ts[2])
            Ts.append(ts[3])
            Ts.append(ts[4])
        else:
            Ts.append(t.getTempPT1000(temperature_channel[n]))

    for n in range(len(humidity)):
        Hs.append(h.getVoltage(humidity_channel[n]))

    for n in range(len(Vmeter)):
        Vs.append(v.getVoltage(Vmeter_channel[n]))

    for j in xrange(args.ndaqs):
        getVoltage = d.getVoltage(ch)
        print "Get voltage: %.2f V" % (getVoltage)
        current = d.getCurrent(ch)*1E6
        print "Get current: %.2f uA" % (current)
        if (abs(current) > args.I_lim):
            print("Software Limit reached!")
            softLimit = True
            break
        Is.append(current)
        timestamp = time.time()

        values = []
        values = [timestamp,i,getVoltage,current]
        for t in Ts:
            values.append(t)
        for h in Hs:
            values.append(h)
        for v in Vs:
            values.append(v)
        sh.write_line(fw, values)
        pass
    if softLimit: break
    Us.append(voltage)
    Imeans.append(np.mean(Is))
    Irms.append(sem(Is))
    pass
    i+=1


#ramp down voltage
d.rampVoltage(0,ch)
d.enableOutput(False)

#short data version
fwshort = sh.new_txt_file("%s_short"%outputname)
header = ["U[V]","Imean[uA]","Irms[uA]"]
sh.write_line(fwshort,header)
for i in range(len(Us)):
    sh.write_line(fwshort,[Us[i],Imeans[i],Irms[i]])


#close files
for s in source:
    s.close()
for t in temperature:
    t.close()
for h in humidity:
    h.close()
for v in Vmeter:
    v.close()
sh.close_txt_file(fw)
sh.close_txt_file(fwshort)



raw_input()
