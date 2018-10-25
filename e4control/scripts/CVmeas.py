
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import argparse
import time

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import sem

from .. import utils as sh


parser = argparse.ArgumentParser()
parser.add_argument('v_min', help='min voltage (V)', type=float)
parser.add_argument('v_max', help='max voltage (V)', type=float)
parser.add_argument('output', help='output file')
parser.add_argument('config', help='config file')
parser.add_argument('-s', '--v_steps', help='number of volt steps', type=int, default=2)
parser.add_argument('-n', '--ndaqs', type=int, default=5)
parser.add_argument('-d', '--delay', type=int, default=1)
parser.add_argument('-f', '--frequenz', type=float)
parser.add_argument('-l', '--lvolt', type=float)
parser.add_argument('-m', '--mode', type=str)
parser.add_argument('-i', '--integration', type=str)
parser.add_argument('-p', '--livePlot', type=bool, default = True)


def main():
    args = parser.parse_args()

    # read configfile
    devices = sh.read_config(args.config)

    # create setting query
    sh.settings_query(devices, v_min=args.v_min, v_max=args.v_max, v_steps=args.v_steps, ndaqs=args.ndaqs, lcr_freq=args.frequenz, lcr_volt=args.lvolt, lcr_aper=args.integration, lcr_mode=args.mode)

    # connection
    source, source_channel = sh.device_connection(devices['S'])
    lcr, lcr_channel = sh.device_connection(devices['L'])
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
    l = lcr[0]
    lch = lcr_channel[0]

    # initialize
    d.initialize(ch)
    d.setVoltage(0, ch)
    d.enableOutput(True, ch)
    l.initialize()
    if args.frequenz:
        l.setFrequency(args.frequenz)
    if args.mode:
        l.setMeasurementMode(args.mode)
    if args.integration:
        l.setIntegrationTimeAndAveragingRate(args.integration, 1)
    if args.lvolt:
        l.setVoltage(args.lvolt)
    for t in temperature:
        t.initialize('T')
    for h in humidity:
        h.initialize('H')
    for v in Vmeter:
        v.initialize('V')
    for a in Ameter:
        a.initialize('I')

    # create directory
    argsoutput = sh.check_outputname(args.output)
    if not os.path.isdir(argsoutput):
        os.mkdir(argsoutput)
    os.chdir(argsoutput)

    # create outputfile
    outputname = argsoutput.split('/')[-1]
    fw = sh.new_txt_file(outputname)

    lcr_freq = l.getFrequency()
    lcr_volt = l.getVoltage()
    lcr_aper = l.getIntegrationTimeAndAveragingRate()
    lcr_mode = l.getMeasurementMode()
    lcr_details = ['freq='+str(lcr_freq), 'volt='+str(lcr_volt), 'aper='+str(lcr_aper), 'mode='+str(lcr_mode)]
    sh.write_line(fw, lcr_details)

    header = ['time', 'no.', 'U[V]', 'I[uA]', 'C[pF]', 'Rlcr']
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
    vnumber = 0
    for v in Vmeter:
        header.append('V%i[V]' % vnumber)
        vnumber += 1
    for a in Ameter:
        header.append('A [uA]')
    sh.write_line(fw, header)

    # create value arrays
    Us = []
    Cmeans = []
    Csem = []
    Cs = []
    Ns = []
    Ts = []
    Hs = []
    Vs = []
    As = []

    # live plot
    if args.livePlot:
        plt.ion()
        fig = plt.figure(figsize=(8, 8))
        ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=2, rowspan=2)
        ax2 = plt.subplot2grid((3, 2), (2, 0), colspan=2)
        ax1.errorbar(Us, Cmeans, yerr=Csem, fmt='o')
        ax1.set_xlabel(r'$U $ $ [\mathrm{V}]$')
        ax1.set_ylabel(r'$C_{mean} $ $ [\mathrm{pF}]$')
        ax1.set_title(r'CV curve')
        ax2.plot(Ns, Cs, 'o')
        ax2.set_xlabel(r'$No.$')
        ax2.set_ylabel(r'$C $ $ [\mathrm{pF}]$')
        ax2.set_title(r'Voltage steps')
        plt.tight_layout()
        plt.pause(0.0001)

    # start measurement
    for i in range(args.v_steps):
        voltage = args.v_min + (args.v_max-args.v_min)/(args.v_steps-1)*i
        print('Set voltage: %.2f V' % voltage)
        d.rampVoltage(voltage, ch)
        time.sleep(args.delay)
        Cs = []
        Ns = []
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
            else:
                Ts.append(temperature[n].getTempPT1000(temperature_channel[n]))

        for n in range(len(humidity)):
            Hs.append(humidity[n].getVoltage(humidity_channel[n]))
        for n in range(len(Ameter)):
            As.append(Ameter[n].getCurrent(Ameter_channel[n]) * 1E6)

        l.getValues()
        time.sleep(0.1)
        l.getValues()
        time.sleep(0.1)
        l.getValues()
        time.sleep(0.1)

        for j in range(args.ndaqs):
            getVoltage = d.getVoltage(ch)
            print('Get voltage: %.2f V' % (getVoltage))
            getCurrent = d.getCurrent(ch)*1E6
            print('Get current: %.2f uA' % (getCurrent))

            Lvalues = l.getValues()
            capacity = Lvalues[0] * 1E12
            print('Get capacity: %.2f pF' % (capacity))
            resis = Lvalues[1]
            Cs.append(capacity)
            timestamp = time.time()

            for n in range(len(Vmeter)):
                Vs.append(Vmeter[n].getVoltage(Vmeter_channel[n]))

            values = []
            values = [timestamp, i, getVoltage, getCurrent, capacity, resis]
            for t in Ts:
                values.append(t)
            for h in Hs:
                values.append(h)
            for v in Vmeter:
                values.append(v)
            for a in Ameter:
                values.append(a)
            sh.write_line(fw, values)

            Ns.append(j+1)
            if args.livePlot:
                ax2.clear()
                ax2.set_title(r'Voltage step : %0.2f V' % voltage)
                ax2.set_xlabel(r'$No.$')
                ax2.set_ylabel(r'$C $ $ [\mathrm{pF}]$')
                ax2.plot(Ns, Cs, 'r--o')
                plt.pause(0.0001)
        Us.append(voltage)
        Cmeans.append(np.mean(Cs))
        Csem.append(sem(Cs))
        if args.livePlot:
            ax1.errorbar(Us, Cmeans, yerr=Csem, fmt='g--o')
            plt.pause(0.0001)

    # ramp down voltage
    d.rampVoltage(0, ch)
    remaining = d.getCurrent(ch) * 1E6
    k = 0
    while k <= 10 and remaining > 0.01:
        print('Please wait! Current still: %0.6f uA' % remaining)
        time.sleep(5)
        remaining = d.getCurrent(ch) * 1E6
        k += 1
    d.enableOutput(False)

    # short data version
    fwshort = sh.new_txt_file('%s_short' % outputname)
    header = ['U[V]', 'Cmean[pF]', 'Csem[pF]']
    sh.write_line(fwshort, header)
    for i in range(len(Us)):
        sh.write_line(fwshort, [Us[i], Cmeans[i], Csem[i]])

    # show and save curve
    plt.close('all')
    nCmeans = np.array(Cmeans)
    c1 = 1/nCmeans**2
    plt.plot(Us, c1, 'o')
    plt.grid()
    plt.title(r'CV curve: %s' % outputname)
    plt.xlabel(r'$U $ $ [\mathrm{V}]$')
    plt.ylabel(r'$1/C_{mean}^2 $ [$\mathrm{1/pF}^2$]')
    plt.xlim(min(Us)-5, max(Us)+5)
    plt.tight_layout()
    plt.savefig('%s.pdf' % outputname)

    # close files
    for s in source:
        s.close()
    for dl in lcr:
        dl.close()
    for t in temperature:
        t.close()
    for h in humidity:
        h.close()
    for v in Vmeter:
        v.close()
    sh.close_txt_file(fw)
    sh.close_txt_file(fwshort)

    #input()


if __name__ == '__main__':
    main()
