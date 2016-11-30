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
#possible devices for IV measurements:
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
parser.add_argument("-I","--I_lim",help="current limit (uA)",type=float,default=3)
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
print("I_lim: %.2f uA"%args.I_lim)
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
