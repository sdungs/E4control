# -*- coding: utf-8 -*-

import os
import argparse
import time

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import sem

from .. import utils as sh

# arg parser
parser = argparse.ArgumentParser()
parser.add_argument('v_min', help='min voltage (V)', type=float)
parser.add_argument('v_max', help='max voltage (V)', type=float)
parser.add_argument('output', help='output file')
parser.add_argument('config', help='config file')
parser.add_argument('-I', '--I_lim', help='current limit, in uA, default=3', type=float, default=3)
parser.add_argument('-s', '--v_steps', help='number of voltage steps', type=int, default=2)
parser.add_argument('-n', '--ndaqs', help='number of measurement repetitions, default=10', type=int, default=10)
parser.add_argument('-d', '--delay', help='delay between the measurements, in seconds, default=5', type=int, default=5)
parser.add_argument('-p', '--noLivePlot', help='disables the livePlot', action='store_true')
parser.add_argument('-db', '--database', help='creates an additional logfile, matching the pixel database requirements', action='store_true')


def main():
    args = parser.parse_args()

    # print welcome message
    sh.print_welcome()

    # read configfile
    devices = sh.read_config(args.config)

    # create setting query
    sh.settings_query(devices, v_min=args.v_min, v_max=args.v_max, v_steps=args.v_steps, I_lim=args.I_lim, ndaqs=args.ndaqs, delay=args.delay)

    # connection
    source, source_channel = sh.device_connection(devices['S'])
    temperature = []
    temperature_channel = []
    humidity = []
    humidity_channel = []
    Vmeter = []
    Vmeter_channel = []
    Ameter = []
    Ameter_channel = []
    if devices['T']:
        temperature, temperature_channel = sh.device_connection(devices['T'])
    if devices['H']:
        humidity, humidity_channel = sh.device_connection(devices['H'])
    if devices['V']:
        Vmeter, Vmeter_channel = sh.device_connection(devices['V'])
    if devices['I']:
        Ameter, Ameter_channel = sh.device_connection(devices['I'])

    # set active source
    d = source[0]
    ch = source_channel[0]

    # initialize
    d.initialize(ch)
    d.setVoltage(0, ch)
    d.enableOutput(True, ch)
    for t in temperature:
        t.initialize('T')
    for h in humidity:
        h.initialize('H')
    for v in Vmeter:
        v.initialize('V')
    for a in Ameter:
        a.initialize('I')

    # Check Current limit
    sh.check_limits(d, ch, I_lim=args.I_lim/1e6)

    # create directory
    argsoutput = sh.check_outputname(args.output)
    if not os.path.isdir(argsoutput):
        os.mkdir(argsoutput)
    os.chdir(argsoutput)

    # create output file
    outputname = argsoutput.split('/')[-1]
    fw = sh.new_txt_file(outputname)
    header = ['time', 'no.', 'U[V]', 'I[uA]']
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
    for v in Vmeter:
        header.append('V[V]')
    for a in Ameter:
        header.append('A [uA]')
    sh.write_line(fw, header)

    # create short data file
    fwshort = sh.new_txt_file('%s_short' % outputname)
    header = ['U[V]', 'Imean[uA]', 'Isem[uA]']
    sh.write_line(fwshort, header)

    # create database output file
    if args.database:
        db_input = sh.initialize_db('IV')

    # create value arrays
    Us = []
    Imeans = []
    Isem = []
    Is = []
    Ts = []
    Hs = []
    Vs = []
    As = []

    softLimit = False

    # live plot
    livePlot = not args.noLivePlot
    if livePlot:
        plt.ion()
        fig = plt.figure(figsize=(8, 8))
        ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=2, rowspan=2)
        ax2 = plt.subplot2grid((3, 2), (2, 0), colspan=2)
        ax1.errorbar([], [], yerr=[], fmt='o')
        ax1.set_xlabel(r'$U $ $ [\mathrm{V}]$')
        ax1.set_ylabel(r'$I_{mean} $ $ [\mathrm{uA}]$')
        ax1.set_title(r'IV curve')
        ax2.plot([], [], 'o')
        ax2.set_xlabel(r'$No.$')
        ax2.set_ylabel(r'$I $ $ [\mathrm{uA}]$')
        ax2.set_title(r'Voltage steps')
        plt.tight_layout()
        plt.pause(0.0001)

    # start measurement
    t0 = time.time()+args.delay
    try:
        for i in range(args.v_steps):
            voltage = args.v_min + (args.v_max-args.v_min)/(args.v_steps-1)*i
            print('Set voltage: %.2f V' % voltage)
            d.rampVoltage(voltage, ch)
            time.sleep(args.delay)
            timestamp0 = time.time()
            Is = []
            Ts = []
            Hs = []
            Vs = []
            As = []
            for n in range(len(temperature)):
                if temperature_channel[n] == 50:
                    ts = temperature[n].getTempPT1000all()
                    Ts.append(ts[0])
                    Ts.append(ts[1])
                    Ts.append(ts[2])
                    Ts.append(ts[3])
                    Ts.append(ts[4])
                elif temperature_channel[n] == 2:
                    ts = temperature[n].getTemperature()
                    Ts.append(ts[0])
                    Ts.append(ts[1])
                else:
                    Ts.append(temperature[n].getTemperature(temperature_channel[n]))

            for idx,h in enumerate(humidity):
                if h.connection_type == 'lan':
                    Hs.append(h.getHumidity(humidity_channel[idx]))
                else:
                    Hs.append(h.getVoltage(humidity_channel[idx]))

            for n in range(len(Vmeter)):
                Vs.append(Vmeter[n].getVoltage(Vmeter_channel[n]))

            for n in range(len(Ameter)):
                As.append(Ameter[n].getCurrent(Ameter_channel[n])*1E6)

            if livePlot:
                ax2.clear()
                ax2.set_title(r'Voltage step : %0.2f V' % voltage)
                ax2.set_xlabel(r'$No.$')
                ax2.set_ylabel(r'$I $ $ [\mathrm{uA}]$')

            for j in range(args.ndaqs):
                getVoltage = d.getVoltage(ch)
                print('Get voltage: %.2f V' % (getVoltage))
                current = d.getCurrent(ch)*1E6
                print('Get current: %.2f uA' % (current))
                if (abs(current) > args.I_lim):
                    print('Software Limit reached!')
                    softLimit = True
                    break
                Is.append(current)
                timestamp = time.time()

                values = [timestamp, i, getVoltage, current]
                for t in Ts:
                    values.append(t)
                for h in Hs:
                    values.append(h)
                for v in Vs:
                    values.append(v)
                for a in As:
                    values.append(a)
                sh.write_line(fw, values)

                if livePlot:
                    ax2.plot(j+1, current, 'r--o')
                    plt.pause(0.0001)

            if softLimit:
                break
            Us.append(voltage)
            Imeans.append(np.mean(Is))
            Istd = np.std(Is)
            Isem.append(sem(Is))
            if livePlot:
               ax1.errorbar(Us, Imeans, yerr=Isem, fmt='g--o')
               plt.pause(0.0001)

            # write to short and data base file
            sh.write_line(fwshort, [Us[i], Imeans[i], Isem[i]])
            if args.database:
                if Ts == []:
                    Ts = float('nan')
                else:
                    Ts = Ts[db_input['db_tempChannel']]
                if Hs == []:
                    Hs = float('nan')
                else:
                    Hs = Hs[db_input['db_humChannel']]

                sh.write_line(db_file, [round(timestamp0-t0), Us[i], '{:.4}'.format(Imeans[i]), '{:.4}'.format(Istd), '{:.4}'.format(Ts), '{:.4}'.format(Hs)])

    except (KeyboardInterrupt, SystemExit):
        print('Measurement was terminated...')
    finally:
        # ramp down voltage
        try:
            d.rampVoltage(0, ch)
            d.enableOutput(False)
        except ValeError as e:
            print('ValueError while ramping down...')
            raise e        

        # show and save curve
        plt.close('all')
        plt.errorbar(Us, Imeans, yerr=Isem, fmt='o')
        plt.grid()
        plt.title(r'IV curve: %s' % outputname)
        plt.xlabel(r'$U $ $ [\mathrm{V}]$')
        plt.ylabel(r'$I_{mean} $ $ [\mathrm{uA}]$')
        plt.xlim(min(Us)-5, max(Us)+5)
        plt.tight_layout()
        plt.savefig('%s.pdf' % outputname)
        print('Plot saved.')

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
        sh.close_txt_file(fwshort)
        if args.database:
            sh.close_txt_file(db_file)

        # wait until the user finishes the measurement
        print('Press "Enter" to finish the measurement.')
        input()


if __name__ == '__main__':
    main()
