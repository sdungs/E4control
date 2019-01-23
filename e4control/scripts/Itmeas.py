#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import argparse
import time

import numpy as np
import matplotlib.pyplot as plt

from .. import utils as sh


# arg parser
parser = argparse.ArgumentParser()
parser.add_argument('voltage', help='constant voltage', type=float, nargs='+')
parser.add_argument('output', help='output file')
parser.add_argument('config', help='config file')
parser.add_argument('-n', '--ndaqs', help='number of measurement repetitions, default=3', type=int, default=3)
parser.add_argument('-d', '--delay', help='delay between the measurements, in seconds, default=60', type=int, default=60)
parser.add_argument('-p', '--noLivePlot', help='disables the livePlot', action='store_true')
parser.add_argument('-db', '--database', help='creates an additional logfile, matching the pixel database requirements', action='store_true')


def main():
    # parse arguments
    args = parser.parse_args()

    # read configfile
    devices = sh.read_config(args.config)

    # create setting query
    sh.settings_query(devices, voltage=args.voltage, ndaqs=args.ndaqs, delay=args.delay)

    # connection
    source, source_channel = sh.device_connection(devices['S'])
    temperature = []
    temperature_channel = []
    humidity = []
    humidity_channel = []
    Vmeter = []
    # Vmeter_channel = []
    if devices['T']:
        temperature, temperature_channel = sh.device_connection(devices['T'])
    if devices['H']:
        humidity, humidity_channel = sh.device_connection(devices['H'])

    # initialize
    for d in range(len(source)):
        if source_channel[d] == 12:
            source[d].initialize(source_channel[1])
            source[d].setVoltage(0, source_channel[1])
            source[d].enableOutput(True, source_channel[1])
            source[d].initialize(source_channel[2])
            source[d].setVoltage(0, source_channel[2])
            source[d].enableOutput(True, source_channel[2])
        else:
            source[d].initialize(source_channel[d])
            source[d].setVoltage(0, source_channel[d])
            source[d].enableOutput(True, source_channel[d])
    for t in temperature:
        t.initialize('T')
    for h in humidity:
        h.initialize('H')

    # create directory
    argsoutput = sh.check_outputname(args.output)
    if not os.path.isdir(argsoutput):
        os.mkdir(argsoutput)
    os.chdir(argsoutput)

    # create output file
    outputname = argsoutput.split('/')[-1]
    fw = sh.new_txt_file(outputname)
    header = ['time', 'no.']
    for d in range(len(source)):
        if source_channel[d] == 12:
            header.append('U[V]')
            header.append('I[uA]')
            header.append('U[V]')
            header.append('I[uA]')
        else:
            header.append('U[V]')
            header.append('I[uA]')
    tvalue = 0
    for n in range(len(temperature)):
        if temperature_channel[n] == 50:
            header.append('T%i[C]' % tvalue)
            tvalue += 1
            header.append('T%i[C]' % tvalue)
            tvalue += 1
            header.append('T%i[C]' % tvalue)
            tvalue += 1
            header.append('T%i[C]' % tvalue)
            tvalue += 1
            header.append('T%i[C]' % tvalue)
            tvalue += 1
        else:
            header.append('T%i[C]' % tvalue)
            tvalue += 1
    hvalue = 0
    for h in humidity:
        header.append('H%i[V]' % hvalue)
        hvalue += 1
    sh.write_line(fw, header)

    # create short data file
    fwshort = sh.new_txt_file('{}_short'.format(outputname))
    header = ['time [s]', 'duration [s]', 'Imean [uA]', 'Tmean [°C]', 'Hmean [%]']
    sh.write_line(fwshort, header)

    # create database output file
    if args.database:
        db_input = sh.load_data('../objs_it.json', {'db_operator':'"operator"', 'db_sensorID':'"sensorID"', 'db_sensorName':'"none"', 'db_tempChannel':'1'})

        print('Please provide input for the pixel database file.')
        db_input['db_operator'] = sh.rlinput('operator: ', db_input['db_operator'])
        db_input['db_sensorID'] = sh.rlinput('sensor ID: ', db_input['db_sensorID'])
        db_input['db_sensorName'] = sh.rlinput('sensor name: ', db_input['db_sensorName'])
        db_input['db_tempChannel'] = sh.rlinput('channel for temperature data: ', db_input['db_tempChannel'])

        db_date = time.localtime(time.time())
        db_date = '{:4d}-{:02d}-{:02d}'.format(db_date[0],db_date[1],db_date[2])
        db_tempChannel = int(db_input['db_tempChannel'])-1

        db_file = sh.new_txt_file('{}_It_1'.format(db_input['db_sensorID']))
        sh.write_line(db_file, [db_input['db_sensorID'], db_input['db_sensorName']])  # 'serial number', 'local device name'
        sh.write_line(db_file, ['dortmund', db_input['db_operator'], db_date])   # 'group', 'operator', 'date'
        sh.write_line(db_file, [args.voltage[0], args.delay, args.ndaqs, '1e5'])   # 'constant bias voltage (in V)'
        sh.write_line(db_file, ['time', 'U', 'I_avg', 'I_std', 'T', 'RH'])  # 'time', 'I', 'T', 'RH'

        sh.dump_data('../objs_it.json', db_input)

    # ramp to const bias voltage
    for d in range(len(source)):
        if source_channel[d] == 12:
            source[d].rampVoltage(args.voltage[0], source_channel[d])
            source[d].rampVoltage(args.voltage[1], source_channel[d])
        else:
            source[d].rampVoltage(args.voltage[0], source_channel[d])
    time.sleep(3)

    # live plot
    livePlot = not args.noLivePlot
    if livePlot:
        plt.ion()
        plt.title(r'It curve')
        plt.ylabel(r'$leakage$ $current$ [$\vert\mathrm{\mu A}\vert$]')
        plt.xlabel(r'$time$  [$\mathrm{s}$]')

    # start measurement
    t0 = time.time()
    k = 0
    try:
        while True:
            timestamp0 = time.time()
            Us = []
            Is = []
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
            for h in humidity:
                Hs.append(h.getHumidity(humidity_channel[n]))
            for j in range(args.ndaqs):
                timestamp = time.time()
                values = [timestamp, k]
                for d in range(len(source)):
                    if source_channel[d] == 12:
                        values.append(source[d].getVoltage(source_channel[1]))
                        I = source[d].getCurrent(source_channel[1])
                        values.append(I)
                        if livePlot:
                            plt.plot(timestamp-t0, abs(I), 'C0x' % iS, label=r'0' % iS)
                        values.append(source[d].getVoltage(source_channel[2]))
                        I = source[d].getCurrent(source_channel[2])
                        values.append(I)
                        if livePlot:
                            plt.plot(timestamp-t0, abs(I), 'C1x' % iS, label=r'1' % iS)
                    else:
                        Us.append(source[d].getVoltage(source_channel[d]))
                        values.append(Us[-1])
                        Is.append(source[d].getCurrent(source_channel[d]))
                        values.append(Is[-1])
                        if livePlot:
                            plt.plot(timestamp-t0, abs(Is[-1]), 'C0x', label=r'0')
                for t in Ts:
                    values.append(t)
                for h in Hs:
                    values.append(h)
                sh.write_line(fw, values)
                print(values)
                plt.pause(0.0001)
                # time.sleep(0.1)

            duration = round(timestamp-timestamp0, 1)
            Umean = np.mean(Us)
            Imean = np.mean(Is)*1e6
            Istd = np.std(Is)*1e6
            Tmean = np.mean(Ts)
            Hmean = np.mean(Hs)

            # write to short and database file
            sh.write_line(fwshort, [timestamp0, duration, Umean, Imean, Tmean, Hmean])
            if args.database:
                sh.write_line(db_file, [round(timestamp0-t0), Umean, '{:.6}'.format(Imean), '{:.6}'.format(Istd), '{:.4}'.format(Ts[db_tempChannel]), Hs[0]])

            time.sleep(args.delay)
            k += 1

    except (KeyboardInterrupt, SystemExit):
        print('Measurement was terminated...')
    finally:
        # ramp down bias voltage
        try:
            for d in range(len(source)):
                source[d].rampVoltage(0, source_channel[d])
                source[d].enableOutput(False)
        except ValueError as e:
            print('ValueError while ramping down...')
            raise e
        finally:
            pass

        # save data
        if livePlot:
            plt.savefig('%s.pdf' % outputname)

        # close files
        for s in source:
            s.close()
        for t in temperature:
            t.close()
        for h in humidity:
            h.close()
        for v in Vmeter:
            v.close()
        sh.close_txt_file(fw)
        # sh.close_txt_file(fwshort)
        if args.database:
            sh.close_txt_file(db_file)

    # wait until the user finishes the measurement
    # input()


if __name__ == '__main__':
    main()
