#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import time
import sys
import ROOT
import array
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import sem
sys.path.append("./../Devices/")
#possible devices for CV measurements:
from ISEG import ISEG
from K2410 import K2410
from K487 import K487
from HP4284A import HP4284A
from K196 import K196
from K2000 import K2000

parser=argparse.ArgumentParser()
parser.add_argument("config",help="config file")
parser.add_argument("v_min",help="min voltage (V)",type=float)
parser.add_argument("v_max",help="max voltage (V)",type=float)
parser.add_argument("output",help="output file")
parser.add_argument("-s","--v_steps",help="number of volt steps",type=int,default=1)
parser.add_argument("-n","--ndaqs",type=int,default=10)
args=parser.parse_args()

L_device = None
L_kind = None
L_adress = None
L_port = None
L_channel = None
S_device = None
S_kind = None
S_adress = None
S_port = None
S_channel = None
T_active = False
T_device = None
T_kind = None
T_adress = None
T_port = None
T_channel = None

print("Read config file")

for line in open(args.config):
    m = line.replace("\n","")
    n = m.split("\t")
    if (n[0] == "S"):
        S_device = n[1]
        S_kind = n[2]
        S_adress = n[3]
        S_port = n[4]
        S_port = int(n[4])
        S_channel = n[5]
    elif (n[0] == "L"):
        L_device = n[1]
        L_kind = n[2]
        L_adress = n[3]
        L_port = n[4]
        L_port = int(n[4])
        L_channel = n[5]
    elif (n[0] == "T"):
        T_active = True
        T_device = n[1]
        T_kind = n[2]
        T_adress = n[3]
        T_port = n[4]
        T_port = int(n[4])
        T_channel = n[5]
    else: print("Unknown Device!")

print("CV measurement settings:")
print("L: "+L_device+"  "+L_kind+"  "+L_adress+"  "+str(L_port)+"  "+L_channel)
print("S: "+S_device+"  "+S_kind+"  "+S_adress+"  "+str(S_port)+"  "+S_channel)
if T_active:
    print("T: "+T_device+"  "+T_kind+"  "+T_adress+"  "+str(T_port)+"  "+T_channel)
else: print("No temperature device")
print("v_min: %.2f V"%args.v_min)
print("v_max: %.2f V"%args.v_max)
print("v_steps: %i"% args.v_steps)
print("ndaqs: %i" % args.ndaqs)
q = raw_input("Settings correct? (y/n)")
if q == "yes": pass
elif q == "y": pass
else: sys.exit("Measurement aborted!")

if L_device == "HP4284A":
    Ldv = HP4284A(L_kind,L_adress,L_port)
    print("L ist")
else: sys.exit("LCR Device is not correct")

if S_device == "ISEG":
    Sdv = ISEG(S_kind,S_adress,S_port)
elif S_device == "K2410":
    Sdv = K2410(S_kind,S_adress,S_port)
    print("S ist")
elif S_device == "K487":
    Sdv = K487(S_kind,S_adress,S_port)
else: sys.exit("Source Device is not correct")

if T_active:
    if T_device == "K2000":
        Tdv = K2000(T_kind,T_adress,T_port)
    elif T_device == "K196":
        Tdv = K196(T_kind,T_adress,T_port)
    else: sys.exit("Temperature Device is not correct")

print("Create directory")
outputname = args.output.split("/")[-1]
if not os.path.isdir(args.output): os.mkdir(args.output)
os.chdir(args.output)

print("Open ROOT file allocate Tree")
fwroot = ROOT.TFile("%s.root"%outputname,"RECREATE")
ntuple = ROOT.TTree("CV","")
timestamps = array.array("L",(0,))
measurepoints = array.array("I",(0,))
voltages = array.array("f",(0,))
currents = array.array("f",(0,))
capacities = array.array("f",(0,))
resistance = array.array("f",(0,))
ntuple.Branch("timestamps", timestamps, "timestamps/i")
ntuple.Branch("measurepoints", measurepoints, "measurepoints/i")
ntuple.Branch("voltages", voltages, "voltages/F")
ntuple.Branch("currents", currents, "currents/F")
ntuple.Branch("capacities", capacities, "capacities/F")
ntuple.Branch("resistance", resistance, "resistance/F")
if T_active:
    temperatures = array.array("f",(0,))
    ntuple.Branch("temperatures", temperatures, "temperatures/F")

Sdv.initialize(S_channel)
Ldv.initialize()
if T_active:
    Tdv.initialize("T4W")
Sdv.setVoltage(0,S_channel)
Sdv.enableOutput(True,S_channel)

Us = []
Is = []
Cmeans = []
Crms = []
Cs = []
Rs = []
Ts = []
Ns = []

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

print("Start measurement")
for i in xrange(args.v_steps):
    voltage = args.v_min + (args.v_max-args.v_min)/(args.v_steps-1)*i
    print "Set voltage: %.2f V" % voltage
    Sdv.rampVoltage(voltage,S_channel)
    time.sleep(1)
    Cs = []
    Ns = []
    for j in xrange(args.ndaqs):
        getVoltage = Sdv.getVoltage(S_channel)
        print "Get voltage: %.2f V" % (getVoltage)
        Lvalues = Ldv.getValues()
        capacity = Lvalues[1]
        print "Get capacity: %.2f pF" % (capacity)
        current = Sdv.getCurrent(S_channel)
        resis = Lvalues[0]
        Cs.append(capacity)
        voltages[0]=getVoltage
        currents[0]=current
        capacities[0]=capacity
        resistance[0]=resis
        measurepoints[0]=i
        timestamps[0]=int(time.time())
        if T_active:
            temperature = Tdv.getTempPT1000(T_channel)
            temperatures[0]=temperature
        ntuple.Fill()

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

print("Open and fill txt file")
fwtxt = open("%s.txt"%outputname, "w")
for i in range(len(Us)):
    fwtxt.write(str(Us[i])+"\t"+str(Cmeans[i])+"\t"+str(Crms[i])+"\n")

print("Ramp down voltage")
Sdv.rampVoltage(0,S_channel)

print("Show and save CV curve plot")
plt.close("all")
plt.errorbar(Us, Cmeans, yerr=Crms, fmt="o")
plt.grid()
plt.title(r"CV curve: %s"%outputname)
plt.xlabel(r"$U $ $ [\mathrm{V}]$")
plt.ylabel(r"$C_{mean} $ $ [\mathrm{pF}]$")
plt.xlim(min(Us)-5,max(Us)+5)
plt.tight_layout()
plt.savefig("%s.pdf"%outputname)

print("Close files and devices")
Sdv.enableOutput(False)
Sdv.close()
Ldv.close()
if T_active: Tdv.close()

fwtxt.close()
ntuple.Write()
fwroot.Close()

raw_input()
