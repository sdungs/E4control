# -*- coding: utf-8 -*-

import os
import sys
import readline
import json
import time

from .devices import (
    HMP4040,
    HP4284A,
    ISEG,
    SHR,
    JULABO,
    K196,
    K487,
    K2000,
    K2410,
    SB22,
    TSX3510P,
    LU114,
    SHT75,
    HUBER,
    TENMA72,
    TTI2,
)

from e4control import __version__


# have an input with a prefilled text
def rlinput(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


def print_welcome():
    print(
        'This is e4control, v{}.\n'
        'If you are not familiar with this version, please check the log (via "git log") for recent changes.'
        ''.format(__version__)
        )


def read_config(configfile):
    devices = {"S": [], "T": [], "H": [], "P": [], "L": [], "C": [], "V": [], "I": []}
    for line in open(configfile):
        if line[0] == '#':
            continue
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
        elif (x == "I"):
            devices["I"].append([model, connection_type, host, port, channel])

        else:
            sys.exit("Unknown parameter while reading configfile!")
    return(devices)


def settings_query(device_list, **kwargs):
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
    if device_list["I"]:
        print("Ampere meter:")
        for i in device_list["I"]:
            print(i)

    print("------------------------------------------------")
    # Order is preserved only with Python >= 3.6 -> https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-pep468
    for key, value in kwargs.items():
        if any(x in key for x in ('v_min', 'v_max')):
            print('{0}: {1:.1f} V'.format(key, value))
        elif 'I_lim' in key:
            print('{0}: {1:.1f} uA'.format(key, value))
        else:
            print('{0}: {1}'.format(key, value))
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
        elif k[0] == "ISEG_SHR":
            d.append(SHR(k[1], k[2], int(k[3])))
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
        elif k[0] == 'LU114':
            d.append(LU114(k[1], k[2], int(k[3])))
        elif k[0] == 'SHT75':
            d.append(SHT75(k[1], k[2], int(k[3])))
        elif k[0] == 'HUBER':
            d.append(HUBER(k[1], k[2], int(k[3])))
        elif k[0] == 'TENMA72':
            d.append(TENMA72(k[1], k[2], int(k[3])))
        elif k[0] == 'TTI2':
            d.append(TTI2(k[1], k[2], int(k[3])))
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
        I_hard = device.getCurrentLimit(channel)
        print('I_lim software: {:.2f} uA'.format(I_lim * 1e6))
        print('I_lim hardware: {:.2f} uA'.format(I_hard * 1e6))
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


def load_data_from_json(file, default_data):
    try:
        data = json.load(open(file, 'r'))
        if data.keys() == default_data.keys():
            return data
        else:
            print('Corrupted data loaded from file. Restoring default data.')
            return default_data
    except:
        print('No data could be loaded from file. Restoring default data.')
        return default_data


def initialize_db(meas_type, args):
    json_file = '../objs_{}.json'.format(meas_type.lower())
    db_input = load_data_from_json(json_file, {'db_operator':'operator', 'db_sensorID':'sensorID', 'db_sensorComment':'"none"', 'db_tempChannel':'2', 'db_temperature':'20.0', 'db_humChannel':'1', 'db_humidity':'40.0'})

    print('Please provide input for the pixel database file.')
    db_input['db_operator'] = rlinput('operator: ', db_input['db_operator'])
    db_input['db_sensorID'] = rlinput('sensor ID: ', db_input['db_sensorID'])
    db_input['db_sensorComment'] = rlinput('sensor comment: ', db_input['db_sensorComment'])
    db_input['db_tempChannel'] = rlinput('channel for the temperature data: ', db_input['db_tempChannel'])
    db_input['db_humChannel'] = rlinput('channel for the humidity data: ', db_input['db_humChannel'])
    db_input['db_temperature'] = rlinput('operating temperature [°C]: ', db_input['db_temperature'])
    db_input['db_humidity'] = rlinput('operating humidity [%]: ', db_input['db_humidity'])

    db_date = time.localtime(time.time())
    db_date = '{:4d}-{:02d}-{:02d}_{:02d}:{:02d}'.format(db_date[0], db_date[1], db_date[2], db_date[3], db_date[4])

    db_file = new_txt_file('{}_{}_1'.format(db_input['db_sensorID'], meas_type))
    write_line(db_file, [db_input['db_sensorID'], meas_type])  # 'serial number'
    write_line(db_file, [db_input['db_sensorComment']])   # 'comment or local device name'
    write_line(db_file, ['TUDO', db_input['db_operator'], db_date])   # 'group', 'operator', 'date + time'
    if meas_type == 'IV':
        write_line(db_file, [(args.v_max-args.v_min) / (args.v_steps-1), args.delay, args.ndaqs, args.I_lim/1e6])   # 'voltage step', 'delay between steps (in s)', 'measurements per step', 'compliance (in A)'
    elif meas_type == 'It':
        write_line(db_file, [args.voltage[0], args.delay, args.ndaqs, 1e-5])   # 'constant voltage', 'delay between steps (in s)', 'measurements per step', 'compliance (in A)'
    elif meas_type == 'CV':
        write_line(db_file, [(args.v_max-args.v_min) / (args.v_steps-1), args.delay, args.ndaqs, args.frequency])   # 'voltage step', 'delay between steps (in s)', 'measurements per step', 'frequecy (in Hz)'
    write_line(db_file, [db_input['db_temperature'], db_input['db_humidity']])   # 'temperature (in °C)', 'humidity (in %)', at start of measurement
    if meas_type == 'IV' or meas_type == 'It':
        write_line(db_file, ['t/s', 'U/V', 'Iavg/uA', 'Istd/uA', 'T/C', 'RH/%']) # 'time', 'U', 'average of all I's', 'std deviation of all I's', temperature, relative humidity
    elif meas_type == 'CV':
        write_line(db_file, ['t/s', 'U/V', 'Cavg/pF', 'Cstd/pF', 'T/C', 'RH/%']) # 'time', 'U', 'average of all C's', 'std deviation of all C's', temperature, relative humidity

    json.dump(db_input, open(json_file, 'w'))

    db_input['db_tempChannel'] = int(db_input['db_tempChannel']) - 1
    db_input['db_humChannel'] = int(db_input['db_humChannel']) - 1

    return db_file, db_input


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


def read_dcs_config(configfile):
    devices = []
    for line in open(configfile):
        if line[0] == '#':
            continue
        m = line.replace("\n", "")
        n = m.split(" ")
        x = n[0]
        model = n[1]
        connection_type = n[2]
        host = n[3]
        port = n[4]
        devices.append([x, model, connection_type, host, port])
    return(devices)


def show_dcs_device_list(devices):
    for i in devices:
        print(i)
    q = input("Correct devices? (y/n)")
    if q == "yes" or q == "y":
        pass
    else:
        sys.exit("Aborted!")


def connect_dcs_devices(devices):
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
        elif k[1] == "ISEG_SHR":
            x = SHR(k[2], k[3], int(k[4]))
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
        elif k[1] == "LU114":
            x = LU114(k[2], k[3], int(k[4]))
            x.initialize()
            d.append(x)
        elif k[1] == "SHT75":
            x = SHT75(k[2], k[3], int(k[4]))
            x.initialize()
            d.append(x)
        elif k[1] == "HUBER":
            x = HUBER(k[2], k[3], int(k[4]))
            x.initialize()
            d.append(x)
        elif k[1] == 'TENMA72':
            x = TENMA72(k[2], k[3], int(k[4]))
        elif k[1] == "TTI2":
            x = TTI2(k[2], k[3], k[4])
            x.initialize()
            d.append(x)
        else:
            sys.exit("Unknown Device: %s" % k[1])
    return(d)
