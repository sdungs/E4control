# -*- coding: utf-8 -*-
"""
Script to readout an MSO5204 Oscilloscope in Sample mode.
The script was designed to measure the timing resolution of a silicon sensor with a TCT setup.
The output is a txt and a pdf file which contain timing information about the trigger and the DUT signal.
The input channels of the oscilloscope are a external trigger, which drives the pulsed laser, and the DUT output singal.
Compared to the other scripts, different methods to obtain the peak times are available: constant fraction (cf) methode, threshold methode and maximum methode, because no influence of the Landau noise and time walk is expected for a laser setup.
"""

from e4control.devices.MSO5204 import MSO5204
import numpy as np
import matplotlib.pyplot as plt
from matplotlib_rc.matplotlib_rc import set_matplotlib_params
import os
import sys
import argparse
from time import sleep
from tqdm import tqdm
from pint import UnitRegistry
u = UnitRegistry()
Q_ = u.Quantity
set_matplotlib_params()

parser = argparse.ArgumentParser()
parser.add_argument('config', help='path to the config file')


def show_plotted_delta_t(data, t, height):
    height = height.to('mV').magnitude
    t_signal = t[0]
    t_trigger = t[1]
    data_signal = data[0]
    data_trigger = data[1]
    plt.clf()
    time_sig, voltage_sig = data_signal[0].to('s').magnitude,   data_signal[1].to('mV').magnitude
    time_trig, voltage_trig = data_trigger[0].to('s').magnitude,    data_trigger[1].to('mV').magnitude
    plt.plot(time_sig, voltage_sig)
    plt.plot(time_trig, voltage_trig)
    plt.vlines(t_signal, 0, max(abs(voltage_sig)))
    plt.vlines(t_trigger, 0, max(voltage_trig))
    plt.hlines(height, t_trigger, t_signal)
    plt.show()
    pass


def savetopdf_samplemode(data, t, threshold, folder, file_name, methode):
    if not os.path.exists(folder):
        os.makedirs(folder)
    data_signal = data[0]
    data_trigger = data[1]
    t_signal = Q_(t[0], 's').to('ns').magnitude
    t_trigger = Q_(t[1], 's').to('ns').magnitude
    plt.clf()
    time_sig, voltage_sig = data_signal[0].to('ns').magnitude, data_signal[1].to('mV').magnitude
    time_trig, voltage_trig = data_trigger[0].to('ns').magnitude, data_trigger[1].to('mV').magnitude
    if methode == 'cf':
        height =  20 / 100 * max(voltage_trig)
    elif methode == 'threshold':
        height = threshold
    elif methode == 'max':
        heigth = max(voltage_sig)
    plt.plot(time_sig, voltage_sig, label='Signal Channel', marker='.', linestyle='')
    plt.plot(time_trig, voltage_trig, label='Trigger Channel', marker='.', linestyle='')
    plt.vlines(t_signal, min(voltage_trig), max(abs(voltage_sig)), label=r'$t_{Signal}$', colors='g')
    plt.vlines(t_trigger, min(voltage_trig), max(voltage_trig), label=r'$t_{Trigger}$', colors='r')
    plt.hlines(height, t_trigger, t_signal)
    plt.xlabel('Time [ns]')
    plt.ylabel('Amplitude [mV]')
    plt.legend()
    plt.savefig(os.path.join(folder, file_name + '.pdf'))
    pass


def interpolate(cf_voltage, x, y): #  cf stands for constant fraction
    m = (y[1] - y[0]) / (x[1] - x[0])
    b = y[0] - m * x[0]
    time = (cf_voltage - b) / m
    return time


def get_cf_time(data):
    time, voltage = data[0].to('s').magnitude, data[1].to('V').magnitude

    max = np.max(voltage)
    #  get constant fraction (cf) of the maximum
    cf = 0.2 * max

    #  cut the data after the maximum to avoid to cf indicies
    index_max = np.where(voltage == max)[0][0]
    voltage = voltage[:index_max]
    time = time[:index_max]

    #  find index for measurement closest to cf of the maximum
    index_cf = np.where(abs(cf - voltage) == min(abs(cf - voltage)))[0][0]

    #  interpolate to get the exact time when the cf of the maximum is reached
    if voltage[index_cf] < cf:
        return interpolate(cf, time[index_cf: index_cf + 2], voltage[index_cf: index_cf + 2])
    else:
        return interpolate(cf, time[index_cf - 1: index_cf + 1], voltage[index_cf - 1: index_cf + 1])

def get_threshold_time(data, threshold=Q_(400, 'mV')):
    if threshold.magnitude < 0:
        time, voltage = data[0].to('s').magnitude, -data[1].to('V').magnitude
        threshold = -threshold.to('V').magnitude
    else:
        time, voltage = data[0].to('s').magnitude, data[1].to('V').magnitude
        threshold = threshold.to('V').magnitude

    max = np.max(voltage)

    #  cut the data after the maximum to avoid to cf indicies
    index_max = np.where(voltage == max)[0][0]
    voltage = voltage[:index_max]
    time = time[:index_max]
    #  find index for measurement closest to cf of the maximum
    index_threshold = np.where(abs(threshold - voltage) == min(abs(threshold - voltage)))[0][0]


    #  interpolate to get the exact time when the cf of the maximum is reached
    if voltage[index_threshold] < threshold:
        return interpolate(threshold, time[index_threshold: index_threshold + 2], voltage[index_threshold: index_threshold + 2])
    else:
        return interpolate(threshold, time[index_threshold - 1: index_threshold + 1], voltage[index_threshold - 1: index_threshold + 1])


def get_max_time(data):
    time, voltage = data[0].to('s').magnitude, data[1].to('V').magnitude
    max = np.max(voltage)

    #  cut the data after the maximum to avoid to cf indicies
    index_max = np.where(voltage == max)[0][0]
    return time[index_max]


def get_amplitude(data):
    voltage = data[1].to('V').magnitude
    return np.max(voltage)


# Disable printing
def blockPrint():
    sys.stdout = open(os.devnull, 'w')
    pass

# Restore printing
def enablePrint():
    sys.stdout = sys.__stdout__
    pass


def printConfig(config):
    print('Current configuration:')
    print(f'1. IP: {config[0]}')
    print(f'2. Save Folder: {config[1]}')
    print(f'3. Measurement Name: {config[2]}')
    print(f'4. Signal Channel: {config[3]}')
    print(f'5. Trigger Channel: {config[4]}')
    print(f'6. Trigger level: {config[5]}')
    print(f'7. Time scale: {config[6]}')
    print(f'8. Recordlength: {config[7]}')
    print(f'9. Samplerate: {config[8]}')
    print(f'10. Repetitions: {config[9]}')
    print(f'11. Threshold: {config[10]}')
    print(f'12. Methode: {config[11]}')
    pass


def config_parameters(file_path):
    if os.path.exists(file_path):
        config_file = open(file_path, 'r+')
    else:
        config_file = open(file_path, 'w')
        config_file.writelines(['None\n'] * 12)
        config_file.close()
        config_file = open(file_path, 'r+')

    config = config_file.readlines()
    printConfig(config)

    yes = ['yes', 'y']
    no = ['no', 'n']
    quit = ['quit']
    possible_inputs = yes + no + quit

    x = input('Do you want to keep the current settings? (y/n/quit)')
    while x not in possible_inputs:
        print('Possible inputs are y/n/quit.')
        x = input('Do you want to keep the current settings? (y/n/quit)')
    if x in quit:
        sys.exit()

    if x in no:
        while True:
            try:
                x = input('Continue changing parameters? (y/n/quit)')
                while x not in possible_inputs:
                    print('Possible inputs are y/n/quit.')
                    x = input('Continue changing parameters? (y/n/quit)')
                if x in quit:
                    sys.exit()
                elif  x in no:
                    break
                config_file.close()
                config_file = open(file_path, 'r')
                config = config_file.readlines()
                printConfig(config)
                config_file.close()
                config_file = open(file_path, 'w+')
                param = int(input('Which parameter should be changed?(1, ..., 11)\n'))
                value = str(input('Type in the new parameter.\n'))
                config[param - 1] = value + '\n'
                config_file.writelines(config)
            except IndexError:
                config_file.writelines(config)
                config_file.close()
                print('Index out of range.')
                sys.exit()
    config_file.close()

    x = input('Start measurement? (y/n/quit)')
    while x not in possible_inputs:
        print('Possible inputs are y/n/quit.')
        x = input('Start measurement? (y/n/quit)')
    if x in quit or x in no:
        sys.exit()

    #  remove /n from the strings
    for buffer, n in zip(config, range(len(config))):
        config[n] = buffer.replace('\n', '')

    return config
"""
Standard Inputs:

IP: 129.217.166.109
Signal CH: 2
Trigger CH: 3
Trigger level: 1000 millivolt
Timescale: 2 nanosecond
Recordlength: 10000
Samplerate: 10000000000
Repetitions: 1000
Threshold: 40 millivolt
Methode: Threshold

For Copy & paste
129.217.166.109
Savefolder (LGAD/Messdaten/Savefolder)
Measurement Name
2
3
400 mV
2 nanosecond
2800
10000000000
1000
40 mV
threshold
"""


def except_pipeline(dev, signal_channel, trigger_channel, recordlength, methode, threshold):
    sleep(0.1)
    dev.RunStop()
    data_signal = dev.getWaveform(channel=signal_channel, start=0, stop=recordlength)
    sleep(0.1)
    data_trigger = dev.getWaveform(channel=trigger_channel, start=0, stop=recordlength)
    sleep(0.1)
    dev.RunStart()
    if methode == 'cf':
        t_signal = get_cf_time(data_signal)
        t_trigger = get_cf_time(data_trigger)
    elif methode == 'threshold':
        t_signal = get_threshold_time(data_signal, threshold)
        t_trigger = get_threshold_time(data_trigger)
    elif methode == 'max':
        t_signal = get_max_time(data_signal)
        t_trigger = get_max_time(data_trigger)
    else:
        enablePrint()
        print('Wrong methode. Possible methodes are: cf, threshold and max.')
        raise SystemExit
    amplitude_signal = get_amplitude(data_signal)
    amplitude_trigger = get_amplitude(data_trigger)
    return data_signal, data_trigger, t_signal, t_trigger, amplitude_signal, amplitude_trigger


def remote_Osci(config):
    ip = config[0]
    save_folder = '/home/sebastian/Dokumente/MSc_Pape/LGADs/Messdaten/' + config[1]
    measurement_name = config[2]
    signal_channel = config[3]
    trigger_channel = config[4]
    tl_value, tl_unit = config[5].split(' ')
    trigger_level = Q_(int(tl_value), tl_unit)
    ts_value, ts_unit  = config[6].split(' ')
    timescale = Q_(int(ts_value), ts_unit)
    recordlength = int(config[7])
    samplerate = int(config[8])
    repetitions = int(config[9])
    threshold_value, threshold_unit  = config[10].split(' ')
    threshold = Q_(int(threshold_value), threshold_unit)
    methode = config[11]

    dev = MSO5204(ip=ip)
    dev.setTriggerSource(source=trigger_channel)
    dev.setTriggerlev(level=trigger_level, channel=trigger_channel)
    dev.setSampleMode()
    dev.setRecordlength(recordlength)
    dev.setSamplerate(samplerate)
    dev.setTime(timescale)
    dev.RunStart()
    #  check if measurement already exists
    if os.path.exists(os.path.join(save_folder, measurement_name)):
        x = input(f'Folder already exist. Overwrite? (y/n):  ')
        yes = ['Yes', 'yes', 'Y', 'y', 'Ja', 'ja', 'J', 'j']
    else:
        os.makedirs(os.path.join(save_folder, measurement_name))
        x = None
    if x == None or x in yes:
        file = open(os.path.join(save_folder, measurement_name, f'{measurement_name}_delta_t.txt'), 'w+')
        file.writelines('# t_signal[second]\tt_trigger[second]\tsignal_amplitude[V]\ttrigger_amplitude[V]')
        for i in tqdm(range(repetitions), desc='Sample'):
            acq_number_prev = dev.getAcqNumber()
            acq_number_now = dev.getAcqNumber()
            while acq_number_now == acq_number_prev:
                sleep(0.01)
                acq_number_now = dev.getAcqNumber()

            acq_number_prev = acq_number_now
            blockPrint()
            dev.RunStop()
            data_signal = dev.getWaveform(channel=signal_channel, start=0, stop=recordlength)
            data_trigger = dev.getWaveform(channel=trigger_channel, start=0, stop=recordlength)
            dev.RunStart()

            try:
                if methode == 'cf':
                    t_signal = get_cf_time(data_signal)
                    t_trigger = get_cf_time(data_trigger)
                    threshold = None
                elif methode == 'threshold':
                    t_signal = get_threshold_time(data_signal, threshold)
                    t_trigger = get_threshold_time(data_trigger)
                elif methode == 'max':
                    t_signal = get_max_time(data_signal)
                    t_trigger = get_max_time(data_trigger)
                    threshold = None
                else:
                    enablePrint()
                    print('Wrong methode. Possible methodes are:\ncf, threshold')
                    raise SystemExit
                amplitude_signal = get_amplitude(data_signal)
                amplitude_trigger = get_amplitude(data_trigger)
            except TypeError:
                enablePrint()
                print('Readout failed.\nContinue')
                blockPrint()
                return_data = except_pipeline(dev=dev, signal_channel=signal_channel, trigger_channel=trigger_channel, recordlength=recordlength, methode=methode, threshold=threshold)
                t_signal = return_data[2]
                t_trigger = return_data[3]
                amplitude_signal = return_data[4]
                amplitude_trigger = return_data[5]
            except IndexError:
                enablePrint()
                print('Something in the interpolation went wrong.\nSkip data point and start plotting results.')
                blockPrint()
                return_data = except_pipeline(dev=dev, signal_channel=signal_channel, trigger_channel=trigger_channel, recordlength=recordlength, methode=methode, threshold=threshold)
                data_signal = return_data[0]
                data_trigger = return_data[1]
                t_signal = return_data[2]
                t_trigger = return_data[3]
                amplitude_signal = return_data[4]
                amplitude_trigger = return_data[5]
                show_plotted_delta_t([data_signal, data_trigger], [t_signal, t_trigger], threshold)

            savetopdf_samplemode([data_signal, data_trigger], [t_signal, t_trigger], threshold, folder=f'{os.path.join(save_folder, measurement_name)}/Pictures', file_name=f'{measurement_name}_pic{i}', methode=methode)
            file.writelines(f'\n{t_signal}\t{t_trigger}\t{amplitude_signal}\t{amplitude_trigger}')

        print('Data successfully saved as txt.')
        file.close()
    else:
        sys.exit('Nothing to do.')


def main():
    try:
        args = parser.parse_args()
        config = config_parameters(file_path=args.config)
        remote_Osci(config)
    except SystemExit:
        enablePrint()
        print('\nQuitting')
    except TypeError:
        sys.exit('Readout failed again.\nQuitting')
    except:
        enablePrint()
        e = sys.exc_info()[0]
        sys.exit(f'\nAn Error occured: {e}')


if __name__ == '__main__':
    main()
