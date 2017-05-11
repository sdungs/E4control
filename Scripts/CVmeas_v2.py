#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import script_header as sh
import argparse
import time

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import sem

parser=argparse.ArgumentParser()
parser.add_argument("v_min",help="min voltage (V)",type=float)
parser.add_argument("v_max",help="max voltage (V)",type=float)
parser.add_argument("output",help="output file")
parser.add_argument("config",help="config file")
parser.add_argument("-s","--v_steps",help="number of volt steps",type=int,default=1)
parser.add_argument("-n","--ndaqs",type=int,default=5)
parser.add_argument("-d","--delay",type=int,default=10)
args=parser.parse_args()

#read configfile
devices = sh.read_config(args.config)

#create setting query
sh.settings_query(devices, v_min = args.v_min, v_max = args.v_max, v_steps = args.v_steps, ndaqs = args.ndaqs)

#connection
source, source_channel = sh.device_connection(devices["S"])
lcr, lcr_channel = sh.device_connection(devices["L"])
temperature = []
temperature_channel = []
humidity = []
humidity_channel = []
if devices["T"]:
    temperature, temperature_channel = sh.device_connection(devices["T"])
if devices["H"]:
    humidity, humidity_channel = sh.device_connection(devices["H"])

#set active source
d = source[0]
ch = source_channel[0]
l = lcr[0]
lch = lcr_channel[0]

#initialize
d.initialize(ch)
d.setVoltage(0,ch)
d.enableOutput(True,ch)
l.initialize()
for t in temperature:
    t.initialize("T")
for h in humidity:
    h.initialize("H")

#create directory
argsoutput = sh.check_outputname(args.output)
if not os.path.isdir(argsoutput): os.mkdir(argsoutput)
os.chdir(argsoutput)

#create outputfile
outputname = argsoutput.split("/")[-1]
fw = sh.new_txt_file(outputname)
header = ["time","no.","U[V]","C[pF]","Rlcr"]
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
sh.write_line(fw,header)

#create value arrays
Us = []
Cmeans = []
Crms = []
Cs = []
Ns = []
Ts = []
Hs = []

#live plot
plt.ion()
fig = plt.figure(figsize=(8,8))
ax1 = plt.subplot2grid((3,2),(0,0), colspan=2, rowspan=2)
ax2 = plt.subplot2grid((3,2), (2, 0), colspan=2)
ax1.errorbar(Us, Cmeans, yerr=Crms, fmt="o")
ax1.set_xlabel(r"$U $ $ [\mathrm{V}]$")
ax1.set_ylabel(r"$C_{mean} $ $ [\mathrm{pF}]$")
ax1.set_title(r"CV curve")
ax2.plot(Ns,Cs,"o")
ax2.set_xlabel(r"$No.$")
ax2.set_ylabel(r"$C $ $ [\mathrm{pF}]$")
ax2.set_title(r"Voltage steps")
plt.tight_layout()
fig.canvas.draw()

#start measurement
for i in xrange(args.v_steps):
    voltage = args.v_min + (args.v_max-args.v_min)/(args.v_steps-1)*i
    print "Set voltage: %.2f V" % voltage
    d.rampVoltage(voltage,ch)
    time.sleep(args.delay)
    Cs = []
    Ns = []
    Ts = []
    Hs = []
    for n in range(len(temperature)):
        if temperature_channel[n] == 50:
            ts = temperature[n].getTempPT1000all()
            Ts.append(ts[0])
            Ts.append(ts[1])
            Ts.append(ts[2])
            Ts.append(ts[3])
            Ts.append(ts[4])
        else:
            Ts.append(temperature[n].getTempPT1000(temperature_channel[n]))

    for n in range(len(humidity)):
        Hs.append(humidity[n].getVoltage(humidity_channel[n]))

    for j in xrange(args.ndaqs):
        getVoltage = d.getVoltage(ch)
        print "Get voltage: %.2f V" % (getVoltage)

        Lvalues = l.getValues()
        capacity = Lvalues[0] * 1E12
        print "Get capacity: %.2f pF" % (capacity)
        resis = Lvalues[1]
        Cs.append(capacity)
        timestamp = time.time()

        values = []
        values = [timestamp,i,getVoltage,capacity,resis]
        for t in Ts:
            values.append(t)
        for h in Hs:
            values.append(h)
        sh.write_line(fw, values)

        Ns.append(j+1)
        ax2.clear()
        ax2.set_title(r"Voltage step : %0.2f V"%voltage)
        ax2.set_xlabel(r"$No.$")
        ax2.set_ylabel(r"$C $ $ [\mathrm{pF}]$")
        ax2.plot(Ns,Cs,"r--o")
        plt.draw()
        plt.tight_layout()
        pass
    Us.append(voltage)
    Cmeans.append(np.mean(Cs))
    Crms.append(sem(Cs))
    ax1.errorbar(Us, Cmeans, yerr=Crms, fmt="g--o")
    plt.draw()
    plt.tight_layout()
    pass


#ramp down voltage
d.rampVoltage(0,ch)
d.enableOutput(False)

#short data version
fwshort = sh.new_txt_file("%s_short"%outputname)
header = ["U[V]","Cmean[pF]","Crms[pF]"]
sh.write_line(fwshort,header)
for i in range(len(Us)):
    sh.write_line(fwshort,[Us[i],Cmeans[i],Crms[i]])

#show and save curve
plt.close("all")
c1 = 1/Cmeans**2
plt.plot(Us, c1,"o")
plt.grid()
plt.title(r"CV curve: %s"%outputname)
plt.xlabel(r"$U $ $ [\mathrm{V}]$")
plt.ylabel(r"$1/C_{mean}^2 $ $ [\mathrm{pF}]$")
plt.xlim(min(Us)-5,max(Us)+5)
plt.tight_layout()
plt.savefig("%s.pdf"%outputname)

#close files
for s in source:
    s.close()
for dl in lcr:
    dl.close()
for t in temperature:
    t.close()
for h in humidity:
    h.close()
for v in Vmeter:
    v.close()
sh.close_txt_file(fw)
sh.close_txt_file(fwshort)

raw_input()
