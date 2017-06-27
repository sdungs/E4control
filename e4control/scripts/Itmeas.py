#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import time

import matplotlib.pyplot as plt

from .. import utils as sh


# arg parser
parser = argparse.ArgumentParser()
parser.add_argument('output', help='output file')
parser.add_argument('config', help='config file')
parser.add_argument('-v', '--voltage', type=float, nargs='+', default=[-30])
parser.add_argument('-d', '--delay', type=int, default=60)
parser.add_argument('-n', '--ndaqs', type=int, default=5)
parser.add_argument('-p', '--plot', type=int, default=1)


def main():
    args = parser.parse_args()

    # read configfile
    devices = sh.read_config(args.config)

    # create setting query
    sh.settings_query(devices, ndaqs=args.ndaqs, delay=args.delay)

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

    # create outputfile
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

    # ramp to const bias voltage
    iS = 0
    for d in range(len(source)):
        if source_channel[d] == 12:
            source[d].rampVoltage(args.voltage[iS], source_channel[d])
            iS += 1
            source[d].rampVoltage(args.voltage[iS], source_channel[d])
            iS += 1
        else:
            source[d].rampVoltage(args.voltage[iS], source_channel[d])
            iS += 1
    if args.plot == 1:
        plt.ion()
        plt.title(r'It curve')
        plt.ylabel(r'$leakage$ $current$ [$\vert\mathrm{\mu A}\vert$]')
        plt.xlabel(r'$time$  [$\mathrm{s}$]')

    t0 = time.time()
    k = 1

    try:
        while True:
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
                timestamp = time.time()
                values = [timestamp, k]
                iS = 0
                for d in range(len(source)):
                    if source_channel[d] == 12:
                        values.append(source[d].getVoltage(source_channel[1]))
                        I = source[d].getCurrent(source_channel[1]) * 1E6
                        values.append(I)
                        if args.plot == 1:
                            plt.plot(timestamp-t0, abs(I), 'C%ix' % iS, label=r'%i' % iS)
                        iS += 1
                        values.append(source[d].getVoltage(source_channel[2]))
                        I = source[d].getCurrent(source_channel[2]) * 1E6
                        values.append(I)
                        if args.plot == 1:
                            plt.plot(timestamp-t0, abs(I), 'C%ix' % iS, label=r'%i' % iS)
                        iS += 1
                    else:
                        values.append(source[d].getVoltage(source_channel[d]))
                        I = source[d].getCurrent(source_channel[d])
                        values.append(I*1E6)
                        if args.plot == 1:
                            plt.plot(timestamp-t0, abs(I*1E6), 'C%ix' % iS, label=r'%i' % iS)
                        iS += 1
                for t in Ts:
                    values.append(t)
                for h in Hs:
                    values.append(h)
                sh.write_line(fw, values)
                print(values)
                plt.pause(0.0001)
                time.sleep(0.1)
            time.sleep(args.delay)
            k += 1

    except (KeyboardInterrupt, SystemExit):
        # ramp down bias voltage
        for d in range(len(source)):
            source[d].rampVoltage(0, source_channel[d])
            source[d].enableOutput(False)

        # save data
        if args.plot:
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

        raw_input()


if __name__ == '__main__':
    main()
