#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
parser.add_argument("-I","--I_lim",help="current limit (uA)",type=float,default=3)
parser.add_argument("-s","--v_steps",help="number of volt steps",type=int,default=1)
parser.add_argument("-n","--ndaqs",type=int,default=10)
args=parser.parse_args()

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
if devices["H"]:
    humidity, humidity_channel = sh.device_connection(devices["V"])
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

#create outputfile
fw = sh.new_txt_file(args.output)
header = ["time","no.","U[V]","I[uA]"]
for t in temperature:
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
for t in temperature:
    Ts.append([])
Hs = []
for h in humidity:
    Hs.append([])
Vs = []
for v in Vmeter:
    Vs.append([])
softLimit = False

#live plot
plt.ion()
fig = plt.figure(figsize=(8,8))
ax1 = plt.subplot2grid((3,2),(0,0), colspan=2, rowspan=2)
ax2 = plt.subplot2grid((3,2), (2, 0), colspan=2)
ax1.errorbar(Us, Imeans, yerr=Irms, fmt="o")
ax1.set_xlabel(r"$U $ $ [\mathrm{V}]$")
ax1.set_ylabel(r"$I_{mean} $ $ [\mathrm{uA}]$")
ax1.set_title(r"IV curve")
ax2.plot(Ns,Is,"o")
ax2.set_xlabel(r"$No.$")
ax2.set_ylabel(r"$I $ $ [\mathrm{uA}]$")
ax2.set_title(r"Voltage steps")
plt.tight_layout()
fig.canvas.draw()

#start measurement
for i in xrange(args.v_steps):
    voltage = args.v_min + (args.v_max-args.v_min)/(args.v_steps-1)*i
    print "Set voltage: %.2f V" % voltage
    d.rampVoltage(voltage,ch)
    time.sleep(1)
    Is = []
    Ns = []
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
        n = 0
        for t in temperature:
            values.append(t.getTempPT1000(temperature_channel[n]))
            n += 1
        n = 0
        for h in humidity:
            values.append(h.getVoltage(humidity_channel[n]))
            n += 1
        n = 0
        for v in Vmeter:
            values.append(v.getVoltage(Vmeter_channel[n]))
            n += 1
        sh.write_line(fw, values)

        Ns.append(j+1)
        ax2.clear()
        ax2.set_title(r"Voltage step : %0.2f V"%voltage)
        ax2.set_xlabel(r"$No.$")
        ax2.set_ylabel(r"$I $ $ [\mathrm{uA}]$")
        ax2.plot(Ns,Is,"r--o")
        plt.draw()
        plt.tight_layout()
        pass
    if softLimit: break
    Us.append(voltage)
    Imeans.append(np.mean(Is))
    Irms.append(sem(Is))
    ax1.errorbar(Us, Imeans, yerr=Irms, fmt="g--o")
    plt.draw()
    plt.tight_layout()
    pass


#ramp down voltage
d.rampVoltage(0,ch)
d.enableOutput(False)

#short data version
fwshort = sh.new_txt_file("%s_short"%args.output)
header = ["U[V]","Imean[uA]","Irms[uA]"]
sh.write_line(fwshort,header)
for i in range(len(Us)):
    sh.write_line(fwshort,[Us[i],Imeans[i],Irms[i]])

#show and save curve
plt.close("all")
plt.errorbar(Us, Imeans, yerr=Irms, fmt="o")
plt.grid()
plt.title(r"IV curve: %s"%(args.output.split("/")[-1]))
plt.xlabel(r"$U $ $ [\mathrm{V}]$")
plt.ylabel(r"$I_{mean} $ $ [\mathrm{uA}]$")
plt.xlim(min(Us)-5,max(Us)+5)
plt.tight_layout()
plt.savefig("%s.pdf"%args.output)

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
