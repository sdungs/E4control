#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import time
import sys
import ROOT
import array
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

if (args.kind == "gpib"):
    port = args.port
else: port = int(args.port)

if args.device == "ISEG":
    d = ISEG(args.kind,args.adress,port)
elif args.device == "K2410":
    d = K2410(args.kind,args.adress,port)
elif args.device == "K487": d = K487(args.kind,args.adress,port)

print("Create directory")
outputname = args.output.split("/")[-1]
if not os.path.isdir(args.output): os.mkdir(args.output)
os.chdir(args.output)

print("Open ROOT file allocate Tree")
fwroot = ROOT.TFile("%s.root"%outputname,"RECREATE")
ntuple = ROOT.TTree("IV","")
timestamps = array.array("L",(0,))
measurepoints = array.array("I",(0,))
voltages = array.array("f",(0,))
currents = array.array("f",(0,))
ntuple.Branch("timestamps", timestamps, "timestamps/i")
ntuple.Branch("measurepoints", measurepoints, "measurepoints/i")
ntuple.Branch("voltages",   voltages,   "voltages/F")
ntuple.Branch("currents",   currents,   "currents/F")

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

print("Start measurement")
for i in xrange(args.v_steps):
    voltage = args.v_min + (args.v_max-args.v_min)/(args.v_steps-1)*i
    print "Set voltage: %.2f V" % voltage
    d.rampVoltage(voltage,args.channel)
    time.sleep(1)
    Is = []
    Ns = []
    for j in xrange(args.ndaqs):
        getVoltage = d.getVoltage(args.channel)
        print "Get voltage: %.2f V" % (getVoltage)
        current = d.getCurrent(args.channel)*1E6
        print "Get current: %.2f uA" % (current)
        Is.append(current)
        voltages[0]=getVoltage
        currents[0]=current
        measurepoints[0]=i
        timestamps[0]=int(time.time())
        ntuple.Fill()

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
fwtxt = open("%s.txt"%outputname, "w")
for i in range(len(Us)):
    fwtxt.write(str(Us[i])+"\t"+str(Imeans[i])+"\t"+str(Irms[i])+"\n")

print("Ramp down voltage")
d.rampVoltage(0,args.channel)

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

print("Close files and devices")
d.enableOutput(False)
d.close()
fwtxt.close()
ntuple.Write()
fwroot.Close()

raw_input()
