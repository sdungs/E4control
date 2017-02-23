#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import sys

sys.path.append("./../Devices/")
from DEVICE import DEVICE
from HMP4040 import HMP4040
from HP4284A import HP4284A
from ISEG import ISEG
from JULABO import JULABO
from K487 import K487
from K196 import K196
from K2000 import K2000
from K2410 import K2410
from SB22 import SB22
from TSX3510P import TSX3510P

def read_config(configfile):
    devices = {"S":[] , "T":[] , "H":[] , "P":[] , "L":[] , "C":[]}
    for line in open(configfile):
        m = line.replace("\n","")
        n = m.split(" ")
        x = n[0]
        device = n[1]
        kind = n[2]
        adress = n[3]
        port = n[4]
        channel = n[5]
        if (x == "S"):
            devices["S"].append([device,kind,adress,port,channel])
        elif (x == "T"):
            devices["T"].append([device,kind,adress,port,channel])
        elif (x == "H"):
            devices["H"].append([device,kind,adress,port,channel])
        elif (x == "P"):
            devices["P"].append([device,kind,adress,port,channel])
        elif (x == "L"):
            devices["L"].append([device,kind,adress,port,channel])
        elif (x == "C"):
            devices["C"].append([device,kind,adress,port,channel])
        else: sys.exit("Unknown parameter while reading configfile!")
    return(devices)

def settings_query(device_list, v_min = None, v_max = None, v_steps = None, I_lim = None, ndaqs = None):
    print("------------------------------------------------")
    print("Measurement settings:")
    print("------------------------------------------------")
    if device_list["S"]:
        print("Source device(s):")
        for i in device_list["S"]: print i
    if device_list["T"]:
        print("Temperature device(s):")
        for i in device_list["T"]: print i
    if device_list["H"]:
        print("Humidity device(s):")
        for i in device_list["H"]: print i
    if device_list["P"]:
        print("Power device(s):")
        for i in device_list["P"]: print i
    if device_list["L"]:
        print("LCR device(s):")
        for i in device_list["L"]: print i
    if device_list["C"]:
        print("Cooling System:")
        for i in device_list["C"]: print i
    print("------------------------------------------------")
    if v_min:
        print("v_min: %.2f V" %v_min)
    if v_max:
        print("v_max: %.2f V" %v_max)
    if v_steps:
       print("v_steps: %i" %v_steps)
    if I_lim:
        print("I_lim: %.2f uA" %I_lim)
    if ndaqs:
        print("ndaqs: %i" %ndaqs)
    print("------------------------------------------------")
    q = raw_input("Settings correct? (y/n)")
    if q == "yes": pass
    elif q == "y": pass
    else: sys.exit("Measurement aborted!")
    pass

def device_connection(values):
    d = []
    ch = []
    for k in values:
        if k[0] == "HMP4040":
            d.append(HMP4040(k[1],k[2],int(k[3])))
        elif k[0] == "HP4284A":
            d.append(HP4284A(k[1],k[2],int(k[3])))
        elif k[0] == "ISEG":
            d.append(ISEG(k[1],k[2],int(k[3])))
        elif k[0] == "JULABO":
            d.append(JULABO(k[1],k[2],int(k[3])))
        elif k[0] == "K487":
            d.append(K487(k[1],k[2],int(k[3])))
        elif k[0] == "K196":
            d.append(K196(k[1],k[2],int(k[3])))
        elif k[0] == "K2000":
            d.append(K2000(k[1],k[2],int(k[3])))
        elif k[0] == "K2410":
            d.append(K2410(k[1],k[2],int(k[3])))
        elif k[0] == "SB22":
            d.append(SB22(k[1],k[2],int(k[3])))
        elif k[0] == "TSX3510P":
            d.append(TSX3510P(k[1],k[2],int(k[3])))
        else: sys.exit("Unknown Device: %s"%k[0])
        ch.append(int(k[4]))
        pass
    return(d,ch)

def check_limits(device, channel, V_lim = None, I_lim= None, P_lim = None):
    if V_lim:
        V_hard = device.getVoltageLimit(channel)
        print("V_lim: %.1f V"%V_lim)
        print("V_lim hardware %.1f V"%V_hard)
        if (V_hard <= V_lim): sys.exit("Hardware Limit is lower than Software Limit!")
    if I_lim:
        I_hard = device.getCurrentLimit(channel) * 1E6
        print("I_lim: %.2f uA"%I_lim)
        print("I_lim hardware %.2f uA"%I_hard)
        if (I_hard <= I_lim): sys.exit("Hardware Limit is lower than Software Limit!")
    if P_lim:
        P_hard = device.getPowerLimit(channel)
        print("P_lim: %.1f W"%P_lim)
        print("P_lim hardware %.1f W"%P_hard)
        if (P_hard <= P_lim): sys.exit("Hardware Limit is lower than Software Limit!")

def new_txt_file(output):
    fw = open("%s.txt"%output, "w", buffering=1)
    return(fw)

def close_txt_file(outputfile):
    outputfile.close()

def write_line(txtfile, values):
    for i in values:
        txtfile.write(str(i) + "\t")
    txtfile.write("\n")
    #txtfile.flush()
    pass

def create_plot(filename,kind,x,y, xerr = None, yerr = None, save = True, show = True):
    if (kind=="IV"):
        pass
    elif(kind=="CV"):
        pass
    elif(kind=="IT"):
        pass
    else:
       pass


#class live_plot:
#    title = None
#    x_label = None
#    y_label = None
#    x_lim = None
#    y_lim = None
#    grid = False
#    def __init__():
#        pass
#    def open():
#        pass
#    def update():
#        pass
#    def close():
#        pass
#    pass
