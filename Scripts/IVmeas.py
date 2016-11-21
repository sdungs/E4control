#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import time
import sys
sys.path.append("./../Devices/")
#possible devices for IV measurements:
from ISEG import ISEG
from K2410 import K2410
from K487 import K487

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import sem

parser=argparse.ArgumentParser()
parser.add_argument("v_min",help="min voltage (V)",type=float)
parser.add_argument("v_max",help="max voltage (V)",type=float)
parser.add_argument("output",help="output file")
parser.add_argument("-I","--I_lim",help="current limit (uA)",type=float,default=3)
parser.add_argument("-s","--v_steps",help="number of volt steps",type=int,default=1)
parser.add_argument("-d","--device",default="K2410")
parser.add_argument("-ḱ","--kind",default="serial")
parser.add_argument("-a","--adress",default="flexnut01")
parser.add_argument("-p","--port",default="1002")
parser.add_argument("-c","--channel",type=int,default=1)
parser.add_argument("-n","--ndaqs",type=int,default=10)
args=parser.parse_args()

print("IV measurement settings:")
if args.device == "ISEG": print("Device: ISEG")
elif args.device == "K2410": print("Device: K2410")
elif args.device == "K487": print("Device: K487")
else: sys.exit("Unknown device")
print("Connection: "+args.kind+"  "+args.adress+"  "+args.port)
print("v_min: %.2f V"%args.v_min)
print("v_max: %.2f V"%args.v_max)
print("I_lim: %.2f uA"%args.I_lim)
print("v_steps: %i"% args.v_steps)
print("ndaqs: %i" % args.ndaqs)
q = raw_input("Settings correct? (y/n)")
if q == "yes": pass
elif q == "y": pass
else: sys.exit("Measurement aborted!")

outputname = args.output.split("/")[-1]
if not os.path.isdir(args.output): os.mkdir(args.output)
os.chdir(args.output)

if args.device == "ISEG":
    port = int(args.port)
    d = ISEG(args.kind,args.adress,port)
elif args.device == "K2410":
    port = int(args.port)
    d = K2410(args.kind,args.adress,port)
elif args.device == "K487": d = K487(args.kind,args.adress,args.port)

d.initialize(args.channel)
d.setCurrentLimit(args.I_lim/1E6,args.channel)
d.setVoltage(0,args.channel)
d.enableOutput(True,args.channel)

Us = []
Imeans = []
Irms = []
Is = []
Ns = []

plt.ion()

fig = plt.figure(figsize=(8,8))
ax1 = plt.subplot2grid((3,2),(0,0), colspan=2, rowspan=2)
ax2 = plt.subplot2grid((3,2), (2, 0), colspan=2)

#fig, (ax1, ax2) = plt.subplots(2,1, figsize=(8,6))
ax1.errorbar(Us, Imeans, yerr=Irms, fmt="o")
ax1.set_xlabel(r"$U $ $ [\mathrm{V}]$")
ax1.set_ylabel(r"$I_{mean} $ $ [\mathrm{uA}]$")
ax1.set_title(r"IV curve")
#ax1.set_xlim(args.v_min,args.v_max)

ax2.plot(Ns,Is,"o")
ax2.set_xlabel(r"$No.$")
ax2.set_ylabel(r"$I $ $ [\mathrm{uA}]$")
ax2.set_title(r"Voltage steps")
#ax2.set_xlim(-0.5,args.ndaqs-1+0.5)

plt.tight_layout()

fig.canvas.draw()

print("Start measurement")
for i in xrange(args.v_steps):
    voltage = args.v_min + (args.v_max-args.v_min)/(args.v_steps-1)*i
    print "Set voltage: %.2f V" % voltage
    d.rampVoltage(voltage,args.channel)
    time.sleep(1)
    Is = []
    Ns = []

    for j in xrange(args.ndaqs):
        current = d.getCurrent(args.channel)*1E6
        print "Get current: %.2f uA" % (current)
        Is.append(current)
        Ns.append(j+1)
        ax2.clear()
        ax2.set_title(r"Voltage step : %0.2f V"%voltage)
        ax2.set_xlabel(r"$No.$")
        ax2.set_ylabel(r"$I $ $ [\mathrm{uA}]$")
        ax2.plot(Ns,Is,"r--o")
        plt.draw()
        plt.tight_layout()
        pass
    Us.append(voltage)
    Imeans.append(np.mean(Is))
    Irms.append(sem(Is))
    ax1.errorbar(Us, Imeans, yerr=Irms, fmt="g--o")
    plt.draw()
    plt.tight_layout()
    pass

print("Open and fill txt file")
fw = open("%s.txt"%outputname, "w")
print("write txt file")
for i in range(len(Us)):
    fw.write(str(Us[i])+"\t"+str(Imeans[i])+"\t"+str(Irms[i])+"\n")

print("Show and save IV curve plot")
plt.close("all")
plt.errorbar(Us, Imeans, yerr=Irms, fmt="o")
plt.grid()
plt.title(r"IV curve: %s"%outputname)
plt.xlabel(r"$U $ $ [\mathrm{V}]$")
plt.ylabel(r"$I_{mean} $ $ [\mathrm{uA}]$")
plt.xlim(min(Us)-5,max(Us)+5)
plt.tight_layout()
plt.savefig("%s.pdf"%outputname)

print("Ramp down voltage")
d.rampVoltage(0,args.channel)

print("Close files and devices")
d.enableOutput(False)
d.close()
fw.close()

raw_input()