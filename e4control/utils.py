# -*- coding: utf-8 -*-

import os
import sys


from .devices import (
    HMP4040,
    HP4284A,
    ISEG,
    JULABO,
    K487,
    K196,
    K2000,
    K2410,
    SB22,
    TSX3510P,
    LU114,
)


def read_config(configfile):
    devices = {"S": [], "T": [], "H": [], "P": [], "L": [], "C": [], "V": []}
    for line in open(configfile):
        m = line.replace("\n", "")
        n = m.split(" ")
        x = n[0]
        model = n[1]
        connection_type = n[2]
        host = n[3]
        port = n[4]
        channel = n[5]
        if (x == "S"):
            devices["S"].append([model, connection_type, host, port, channel])
        elif (x == "T"):
            devices["T"].append([model, connection_type, host, port, channel])
        elif (x == "H"):
            devices["H"].append([model, connection_type, host, port, channel])
        elif (x == "P"):
            devices["P"].append([model, connection_type, host, port, channel])
        elif (x == "L"):
            devices["L"].append([model, connection_type, host, port, channel])
        elif (x == "C"):
            devices["C"].append([model, connection_type, host, port, channel])
        elif (x == "V"):
            devices["V"].append([model, connection_type, host, port, channel])
        else:
            sys.exit("Unknown parameter while reading configfile!")
    return(devices)


def settings_query(device_list, v_min=None, v_max=None, v_steps=None, I_lim=None, ndaqs=None, delay=None, lcr_freq=None, lcr_volt=None, lcr_aper=None, lcr_mode=None):
    print("------------------------------------------------")
    print("Measurement settings:")
    print("------------------------------------------------")
    if device_list["S"]:
        print("Source device(s):")
        for i in device_list["S"]:
            print(i)
    if device_list["T"]:
        print("Temperature device(s):")
        for i in device_list["T"]:
            print(i)
    if device_list["H"]:
        print("Humidity device(s):")
        for i in device_list["H"]:
            print(i)
    if device_list["P"]:
        print("Power device(s):")
        for i in device_list["P"]:
            print(i)
    if device_list["L"]:
        print("LCR device(s):")
        for i in device_list["L"]:
            print(i)
    if device_list["C"]:
        print("Cooling System:")
        for i in device_list["C"]:
            print(i)
    if device_list["V"]:
        print("Volt meter:")
        for i in device_list["V"]:
            print(i)

    print("------------------------------------------------")
    if v_min:
        print("v_min: %.2f V" % v_min)
    if v_max:
        print("v_max: %.2f V" % v_max)
    if v_steps:
        print("v_steps: %i" % v_steps)
    if I_lim:
        print("I_lim: %.2f uA" % I_lim)
    if ndaqs:
        print("ndaqs: %i" % ndaqs)
    if delay:
        print("delay: %i" % delay)
    if lcr_freq:
        print("lcr_freq: %.1f" % lcr_freq)
    if lcr_volt:
        print("lcr_volt: %f" % lcr_volt)
    if lcr_aper:
        print("lcr_aper: %s" % str(lcr_aper))
    if lcr_mode:
        print("lcr_mode: %s" % lcr_mode)
    print("------------------------------------------------")
    q = input("Settings correct? (y/n)")
    if q == "yes":
        pass
    elif q == "y":
        pass
    else:
        sys.exit("Measurement aborted!")
    pass


def device_connection(values):
    d = []
    ch = []
    for k in values:
        if k[0] == "HMP4040":
            d.append(HMP4040(k[1], k[2], int(k[3])))
        elif k[0] == "HP4284A":
            d.append(HP4284A(k[1], k[2], int(k[3])))
        elif k[0] == "ISEG":
            d.append(ISEG(k[1], k[2], int(k[3])))
        elif k[0] == "JULABO":
            d.append(JULABO(k[1], k[2], int(k[3])))
        elif k[0] == "K487":
            d.append(K487(k[1], k[2], int(k[3])))
        elif k[0] == "K196":
            d.append(K196(k[1], k[2], int(k[3])))
        elif k[0] == "K2000":
            d.append(K2000(k[1], k[2], int(k[3])))
        elif k[0] == "K2410":
            d.append(K2410(k[1], k[2], int(k[3])))
        elif k[0] == "SB22":
            d.append(SB22(k[1], k[2], int(k[3])))
        elif k[0] == "TSX3510P":
            d.append(TSX3510P(k[1], k[2], int(k[3])))
        else:
            sys.exit("Unknown Device: %s" % k[0])
        ch.append(int(k[4]))
    return(d, ch)


def check_limits(device, channel, V_lim=None, I_lim=None, P_lim=None):
    if V_lim:
        V_hard = device.getVoltageLimit(channel)
        print("V_lim: %.1f V" % V_lim)
        print("V_lim hardware %.1f V" % V_hard)
        if (V_hard <= V_lim):
            sys.exit("Hardware Limit is lower than Software Limit!")
    if I_lim:
        I_hard = device.getCurrentLimit(channel) * 1E6
        print("I_lim: %.2f uA" % I_lim)
        print("I_lim hardware %.2f uA" % I_hard)
        if (I_hard <= I_lim):
            sys.exit("Hardware Limit is lower than Software Limit!")
    if P_lim:
        P_hard = device.getPowerLimit(channel)
        print("P_lim: %.1f W" % P_lim)
        print("P_lim hardware %.1f W" % P_hard)
        if (P_hard <= P_lim):
            sys.exit("Hardware Limit is lower than Software Limit!")


def new_txt_file(output):
    fw = open("%s.txt" % output, "w")
    return(fw)


def close_txt_file(outputfile):
    outputfile.close()


def write_line(txtfile, values):
    for i in range(len(values)):
        if i == max(range(len(values))):
            txtfile.write(str(values[i]) + "\n")
        else:
            txtfile.write(str(values[i]) + "\t")
    txtfile.flush()
    pass


def create_plot(filename, kind, x, y, xerr=None, yerr=None, save=True, show=True):
    if (kind == "IV"):
        pass
    elif(kind == "CV"):
        pass
    elif(kind == "IT"):
        pass
    else:
        pass


def check_outputname(output):
    outputname = output.split("/")[-1]
    checktxtfile = (output + "/" + outputname + ".txt")
    if os.path.isfile(checktxtfile):
        print("Outputname: " + outputname)
        n = input("File already exists! Overwrite? (y/n)")
        if n == "yes":
            return(output)
        elif n == "y":
            return(output)
        else:
            newoutput = output + "_X"
            name = check_outputname(newoutput)
            return(name)
    print("Outputname: " + outputname)
    return(output)


def read_testbeamDCS_config(configfile):
    devices = []
    for line in open(configfile):
        m = line.replace("\n", "")
        n = m.split(" ")
        x = n[0]
        model = n[1]
        connection_type = n[2]
        host = n[3]
        port = n[4]
        devices.append([x, model, connection_type, host, port])
    return(devices)


def show_testbeamDCS_device_list(devices):
    for i in devices:
        print(i)
    q = input("Correct devices? (y/n)")
    if q == "yes" or q == "y":
        pass
    else:
        sys.exit("Aborted!")


def connect_testbeamDCS_devices(devices):
    d = []
    for k in devices:
        if k[1] == "HMP4040":
            x = HMP4040(k[2], k[3], int(k[4]))
            x.initialize()
            d.append(x)
        elif k[1] == "HP4284A":
            x = HP4284A(k[2], k[3], int(k[4]))
            x.initialize()
            d.append(x)
        elif k[1] == "ISEG":
            x = ISEG(k[2], k[3], int(k[4]))
            x.initialize()
            d.append(x)
        elif k[1] == "JULABO":
            x = JULABO(k[2], k[3], int(k[4]))
            x.initialize()
            d.append(x)
        elif k[1] == "K487":
            x = K487(k[2], k[3], int(k[4]))
            x.initialize()
            d.append(x)
        elif k[1] == "K196":
            x = K196(k[2], k[3], int(k[4]))
            x.initialize(k[0])
            d.append(x)
        elif k[1] == "K2000":
            x = K2000(k[2], k[3], int(k[4]))
            x.initialize(k[0])
            d.append(x)
        elif k[1] == "K2410":
            x = K2410(k[2], k[3], int(k[4]))
            x.initialize()
            d.append(x)
        elif k[1] == "SB22":
            x = SB22(k[2], k[3], int(k[4]))
            x.initialize()
            d.append(x)
        elif k[1] == "TSX3510P":
            x = TSX3510P(k[2], k[3], int(k[4]))
            x.initialize()
            d.append(x)
        else:
            sys.exit("Unknown Device: %s" % k[1])
    return(d)
