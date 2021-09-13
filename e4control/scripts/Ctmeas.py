# -*- coding: utf-8 -*-

import os
import argparse
import time
import datetime as dt
from math import ceil
import numpy as np
import matplotlib.pyplot as plt
import e4control.utils as sh


# arg parser
parser = argparse.ArgumentParser()
parser.add_argument('voltage', help='preset constant voltage', type=float)
parser.add_argument('output', help='name of output file')
parser.add_argument('config', help='path to config file')
parser.add_argument('-n', '--ndaqs', help='number of measurement repetitions, default=3', type=int, default=3)
parser.add_argument('-d', '--delay', help='delay between the measurements, in seconds, default=60', type=int, default=59)
parser.add_argument('-I', '--I_lim', help='set current limit as integer in µA. Default = 100', type=int, default=100)
parser.add_argument('-f', '--frequency', help='measuring frequency of the LCR meter, in Hz, default=10000', type=float, default=10000)
parser.add_argument('-l', '--lvolt', help='signal amplitude, in V, default=0.050', type=float, default=0.05)
parser.add_argument('-m', '--mode', type=str)
parser.add_argument('-i', '--integration', type=str, default='LONG')
parser.add_argument('-pre', '--preParams', help='Parameters for hold prior the Ct-measurement. Tuple of [voltage in V , time in s]. Default [-600, 43200]',
                    type=float, nargs=2, default=[-600, 43200])



def main():
    # parse arguments
    args = parser.parse_args()

    # print welcome message
    sh.print_welcome()

    # read configfile
    devices = sh.read_config(args.config)

    # create setting query
    sh.settings_query(devices, voltage=args.voltage, ndaqs=args.ndaqs, delay=args.delay)

    # connection
    source, source_channel = sh.device_connection(devices['S'])
    lcr, lcr_channel = sh.device_connection(devices['L'])
    temperature = []
    temperature_channel = []
    Vmeter = []
    l = lcr[0]
    lch = lcr_channel[0]
    if devices['T']:
        temperature, temperature_channel = sh.device_connection(devices['T'])

    # initialize
    for d in range(len(source)):
        source[d].initialize(source_channel[d])
        source[d].setVoltage(0, source_channel[d])
        source[d].setOutput(True, source_channel[d])

    # LCR-Meter
    l.initialize()
    if args.frequency:
        l.setFrequency(args.frequency)
    if args.mode:
        l.setMeasurementMode(args.mode)
    if args.integration:
        l.setIntegrationTimeAndAveragingRate(args.integration, 1)
    if args.lvolt:
        l.setVoltage(args.lvolt)
    # environmental sensors
    for t in temperature:
        t.initialize('T')

    # create directory
    argsoutput = sh.check_outputname(args.output)
    if not os.path.isdir(argsoutput):
        os.mkdir(argsoutput)
    os.chdir(argsoutput)
    about = sh.new_txt_file('about')
    sh.write_line(about, ['Frequency: [Hz]', str(l.getFrequency())])
    sh.write_line(about, ['AC_Voltage:  [V]', str(l.getVoltage())])
    sh.write_line(about, ['Measurement Mode: ', str(l.getMeasurementMode())])
    sh.close_txt_file(about)

    # create output file
    outputname = argsoutput.split('/')[-1]
    fw_preCt = sh.new_txt_file(f'{outputname}_preCt')
    fw = sh.new_txt_file(outputname)
    header = ['duration [s]']
    for d in range(len(source)):
        header.append('U[V]')
        header.append('I[uA]')
    tvalue = 0
    header.append('LCR_Value 1')
    header.append('LCR-Value 2')
    for n in range(len(temperature)):
        header.append('T%i[C]' % tvalue)
        tvalue += 1
    header.append('time')  # final header: [duration, U, I , LCR1, LCR2, T, time]
    sh.write_line(fw, header)
    sh.write_line(fw_preCt, header)

    # create short data files
    fwshort = sh.new_txt_file('{}_short'.format(outputname))
    header = ['duration of Ct [s]', 'Imean [uA]', 'Istd', 'LCR 1 mean', 'LCR 1 std', 'LCR 2 mean', 'LCR2 std', 'Tmean [°C]', 'time']
    sh.write_line(fwshort, header)

    # ramp to const bias voltage for "preCt-Phase"
    for d in range(len(source)):
        source[d].rampVoltage(args.preParams[0], source_channel[d])
    time.sleep(3)
    print('Starting "preCt-Phase" Hold at {} V for {}h.'.format(args.preParams[0], args.preParams[1] / 3600))
    t0 = time.time()

    softLimit = False
    while((t0 + args.preParams[1]) > time.time()):
        values = []
        timestamp = time.time()
        values.append(np.round(timestamp - t0, 1))
        for d in range(len(source)):
            values.append(source[d].getVoltage(source_channel[d]))
            values.append(source[d].getCurrent(source_channel[d]) * 1e6)
        fC, fR = l.getValues()
        values.append(fC)
        values.append(fR)
        for n in range(len(temperature)):
            values.append(temperature[n].getTemperature(temperature_channel[n]))
        values.append(timestamp)
        sh.write_line(fw_preCt, values)
        if (abs(values[2]) > abs(args.I_lim)):
            print('Software Limit reached! {}'.format(values[2]))
            sh.write_line(fw_preCt, ['Software Limit reached!', values[2]])
            softLimit = True
            break
        print(values)
        time.sleep(300)
    sh.close_txt_file(fw_preCt)

# Ct-measurement at constant voltage
    # start measurement
    print('This measurement runs until ctrl+C is pressed!')
    t0 = time.time()
    k = 0
    for d in range(len(source)):
        source[d].rampVoltage(args.voltage, source_channel[d])
    time.sleep(3)
    try:
        while True and not softLimit:
            timestamp0 = time.time()
            print('This measurement has been runing for a total time of {}.'.format(str(dt.timedelta(seconds=timestamp0 - t0)).split('.')[0]))
            Us = []
            Is = []
            LCR1s = []
            LCR2s = []
            Ts = []  # final header: [duration, U, I , LCR1, LCR2, T, time]
            timestamp = time.time()
            for j in range(args.ndaqs):
                values = []
                timestamp = time.time()
                if j == (ceil(args.ndaqs / 2) - 1):
                    midDuration = np.round(timestamp - t0, 1)
                values.append(np.round(timestamp - t0, 1))
                for d in range(len(source)):
                    Us.append(source[d].getVoltage(source_channel[d]))
                    values.append(Us[-1])
                    Is.append(source[d].getCurrent(source_channel[d]) * 1e6)
                    values.append(Is[-1])
                fC, fR = l.getValues()
                LCR1s.append(fC)
                LCR2s.append(fR)
                values.append(fC)
                values.append(fR)
                for n in range(len(temperature)):
                    Ts.append(temperature[n].getTemperature(temperature_channel[n]))
                values.append(timestamp)
                sh.write_line(fw, values)
                if (abs(values[2]) > abs(args.I_lim)):
                    print('Software Limit reached! {}'.format(values[2]))
                    sh.write_line(fw, ['Software Limit reached!', values[2]])
                    softLimit = True
                    break
                print(values)
                plt.pause(0.001)

            duration = round(timestamp0 - t0, 1)
            Imean = np.mean(Is)
            Istd = np.std(Is)
            LCR1mean = np.mean(LCR1s)
            LCR1std = np.std(LCR1s)
            LCR2mean = np.mean(LCR2s)
            LCR2std = np.std(LCR2s)
            Tmean = np.mean(Ts)

            # write to short file
            sh.write_line(fwshort, [midDuration, Imean, Istd, LCR1mean, LCR1std, LCR2mean, LCR2std, Tmean, timestamp])
            time.sleep(args.delay)
            k += 1
            if args.mode == 'YTD':
                print('Cint: {} pF'.format((LCR1mean*np.sin(np.radians(LCR2mean))/(2*np.pi*args.frequency)*1e12)))

    except (KeyboardInterrupt, SystemExit):
        print('Measurement was terminated...')
    finally:
        # ramp down bias voltage
        try:
            for d in range(len(source)):
                source[d].rampVoltage(0, source_channel[d])
                source[d].setOutput(False)
        except ValueError as e:
            print('ValueError while ramping down...')
            raise e
        finally:
            pass

        # close files
        for s in source:
            s.close()
        for t in temperature:
            t.close()
        for v in Vmeter:
            v.close()
        sh.close_txt_file(fw)
        sh.close_txt_file(fwshort)

    # wait until the user finishes the measurement
    print('Press "Enter" to close the measurement.')
    input()


if __name__ == '__main__':
    main()

