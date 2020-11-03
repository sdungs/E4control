# -*- coding: utf-8 -*-
"""
Script to readout an MSO5204 Oscilloscope for a ⁹⁰Sr setup.
The script is designed to make timing measurements of silicon sensors.
The oscilloscope input are a trigger and a signal channel.
The outputs of this script are txt files that contain the data of coincident signals and
a pdf where the data and the time difference is plotted.
"""

from e4control.devices.MSO5204 import MSO5204
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import argparse
from scipy.optimize import curve_fit
from time import sleep
from tqdm import tqdm
from pint import UnitRegistry
u = UnitRegistry()
Q_ = u.Quantity

parser = argparse.ArgumentParser()
parser.add_argument('config', help='path to the config file')


"""
Errorclass wich is raised when the signal channel does not reach the threshold.
"""
class NoPeak(Exception):
    pass


"""
Linear fitfunction. It is needed for the interpolation using curve_fit.
"""
def lin_func(x, m, b):
    return m * x + b


"""
Function to interpolate between two measurement points, to find the time corresponding to the cf voltage.
"""
def interpolate_curve_fit(cf_voltage, x_data, y_data):
    params, covariance = curve_fit(lin_func, x_data, y_data)
    m = params[0]
    b = params[1]
    return (cf_voltage - b) / m


"""
Function to save the data to a pdf file, compared to the savetopdf function of the MS=5204 class, this function allows two readout two channels (signal and trigger channel).
"""
def savetopdf_90sr(data, t, cf_factor, folder, file_name):
    if not os.path.exists(folder):
        os.makedirs(folder)
    data_signal = data[0]
    data_trigger = data[1]
    t_signal = Q_(t[0], 's').to('ns').magnitude
    t_trigger = Q_(t[1], 's').to('ns').magnitude
    plt.clf()
    time_sig, voltage_sig = data_signal[0].to('ns').magnitude, data_signal[1].to('mV').magnitude
    time_trig, voltage_trig = data_trigger[0].to('ns').magnitude, data_trigger[1].to('mV').magnitude
    height =  cf_factor / 100 * max(voltage_trig)
    plt.plot(time_sig, voltage_sig, label='Signal Channel', marker='.', linestyle='')
    plt.plot(time_trig, voltage_trig, label='Trigger Channel', marker='.', linestyle='')
    plt.vlines(t_signal, min(voltage_trig), max(abs(voltage_sig)), label=r'$t_{Signal}$', colors='g')
    plt.vlines(t_trigger, min(voltage_trig), max(voltage_trig), label=r'$t_{Trigger}$', colors='r')
    plt.hlines(height, t_trigger, t_signal)
    plt.xlabel('Time [ns]')
    plt.ylabel('Amplitude [mV]')
    plt.legend()
    plt.savefig(os.path.join(folder, file_name + '.pdf'))


"""
Function which returns the time corresponding to the cf voltage.
The input is the raw data of the signal channel, the cf factor and the minimal threshold to accept a peak as a signal.
"""
def get_cf_time_signal(data, cf_factor, min_signal_peak):
    time, voltage = data[0].to('s').magnitude, data[1].to('V').magnitude

    max = np.max(voltage)
    #  check if the signal reaches the given threshold min_signal_peak
    if Q_(max, 'V').to('mV').magnitude < min_signal_peak.to('mV').magnitude:
        raise NoPeak
    #  get constant fraction (cf) of the maximum
    cf = cf_factor / 100 * max

    #  cut the data after the maximum to avoid two cf indicies
    index_max = np.where(voltage == max)[0][0]
    voltage = voltage[:index_max]
    time = time[:index_max]

    #  find index for measurement closest to cf of the maximum
    reverse_index_cf = np.where(abs(cf - voltage[::-1]) == min(abs(cf - voltage[::-1])))[0][0]
    index_cf = np.where(voltage[::-1][reverse_index_cf] == voltage)[0][0]

    #  interpolate to get the exact time when the cf of the maximum is reached
    if voltage[index_cf] < cf:
        return interpolate_curve_fit(cf, time[index_cf: index_cf + 2], voltage[index_cf: index_cf + 2])
    else:
        return interpolate_curve_fit(cf, time[index_cf - 1: index_cf + 1], voltage[index_cf - 1: index_cf + 1])


"""
Function which returns the time corresponding cf voltage of the trigger channel.
The input is the raw data and the cf factor.
"""
def get_cf_time_trigger(data, cf_factor):
    time, voltage = data[0].to('s').magnitude, data[1].to('V').magnitude

    max = np.max(voltage)
    #  get constant fraction (cf) of the maximum
    cf = cf_factor / 100 * max

    #  cut the data after the maximum to avoid to cf indicies
    index_max = np.where(voltage == max)[0][0]
    voltage = voltage[index_max - 15:index_max]
    time = time[index_max - 15:index_max]

    #  find index for measurement closest to cf of the maximum
    reverse_index_cf = np.where(abs(cf - voltage[::-1]) == min(abs(cf - voltage[::-1])))[0][0]
    index_cf = np.where(voltage[::-1][reverse_index_cf] == voltage)[0][0]

    #  interpolate to get the exact time when the cf of the maximum is reached
    if voltage[index_cf] < cf:
        return interpolate_curve_fit(cf, time[index_cf: index_cf + 2], voltage[index_cf: index_cf + 2])
    else:
        return interpolate_curve_fit(cf, time[index_cf - 1: index_cf + 1], voltage[index_cf - 1: index_cf + 1])


"""
Function which return the maximum and the minimum of the input data.
"""
def get_amplitude(data):
    voltage = data[1].to('V').magnitude
    return np.max(voltage), np.min(voltage)


"""
Disable console output.
"""
def blockPrint():
    sys.stdout = open(os.devnull, 'w')
    pass


"""
Enalbe console output.
"""
def enablePrint():
    sys.stdout = sys.__stdout__
    pass


"""
Function to print the config settings from the config file.
"""
def printConfig(config):
    print('Current configuration:')
    print(f'1. IP: {config[0]}')
    print(f'2. Save Folder (absolute path): {config[1]}')
    print(f'3. Measurement Name: {config[2]}')
    print(f'4. Signal Channel: {config[3]}')
    print(f'5. Trigger Channel: {config[4]}')
    print(f'6. Trigger level with unit: {config[5]}')
    print(f'7. Trigger mode: {config[6]}')
    print(f'8. Time scale with unit: {config[7]}')
    print(f'9. Recordlength: {config[8]}')
    print(f'10. Samplerate: {config[9]}')
    print(f'11. Repetitions: {config[10]}')
    print(f'12. CF factor: {config[11]}')
    print(f'13. Minimal Signal Peak with unit: {config[12]}')
    pass


"""
Function to change the config file via the console.
The Function returns the config in a data type the remote_Osci function can handle it.
"""
def config_parameters(file_path):
    if os.path.exists(file_path):
        config_file = open(file_path, 'r+')
    else:
        config_file = open(file_path, 'w')
        config_file.writelines(['None\n'] * 13)
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
                param = int(input('Which parameter should be changed?(1, ..., 13)\n'))
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
Trigger level: 15 millivolt
Trigger mode: NORMAL
Timescale: 2 nanosecond
Recordlength: 10000
Samplerate: 10000000000
Repetitions: 1000
CF factor: 20
Minimal Szintillaotr Peak: 25 mV

For Copy & paste:
129.217.166.109
Savefolder (LGAD/Messdaten/Savefolder)
Measurement Name
2
3
15 mV
NORMAL
2 nanosecond
10000
10000000000
1000
20
20 mV

"""


"""
Function which should handle unexpected errors, so that long term measurements do not collapse.
The Function retries the measurement until accepted data is produced.
"""
def handle_allErrors(dev, signal_channel, trigger_channel, recordlength, cf_factor, min_signal_peak, exception):
    try:
        enablePrint()
        print(f'Readout failed due to {exception}.\nContinue')
        blockPrint()
        return pipeline(dev=dev, signal_channel=signal_channel, trigger_channel=trigger_channel,  recordlength=recordlength, cf_factor=cf_factor, min_signal_peak=min_signal_peak)
    except NoPeak:
        return False
    except Exception:
        return False


"""
Function which handles the NoPeak error.
This error occured, when the signal channel does not reach the given threshold (min_signal_peak).
"""
def handle_NoPeak(dev, signal_channel, trigger_channel, recordlength, cf_factor, min_signal_peak):
    try:
        return pipeline(dev=dev, signal_channel=signal_channel, trigger_channel=trigger_channel,  recordlength=recordlength, cf_factor=cf_factor, min_signal_peak=min_signal_peak)
    except NoPeak:
        return False


"""
Function to compare the old and new measured data.
Only new data should be accepted and saved.
"""
def check_data(old, new):
    if not new:
        return False
    elif True in (np.array(old) == np.array(new[2:])):
        return True
    else:
        return False


"""
Readout pipeline. The pipeline returns the data measured by the oscilloscpe and all further calculated information about the data.
"""
def pipeline(dev, signal_channel, trigger_channel, recordlength, cf_factor, min_signal_peak):
    acq_number_prev = dev.getAcqNumber()
    acq_number_now = dev.getAcqNumber()

    #  measure until a new acqusition occured, to ensure that only new data is recorded
    while acq_number_now == acq_number_prev:
        sleep(0.01)
        acq_number_now = dev.getAcqNumber()

    acq_number_prev = acq_number_now

    #  receive the data from the oscilloscope
    dev.RunStop()
    data_signal = dev.getWaveform(channel=signal_channel, start=0, stop=recordlength)
    sleep(0.05)
    data_trigger = dev.getWaveform(channel=trigger_channel, start=0, stop=recordlength)
    sleep(0.05)
    dev.RunStart()

    #  check if the signals are accepted and calculate the time corresponding to the cf voltage
    t_signal = get_cf_time_signal(data_signal, cf_factor, min_signal_peak)
    t_trigger = get_cf_time_trigger(data_trigger, cf_factor)
    amplitude_signal, min_signal = get_amplitude(data_signal)
    amplitude_trigger, min_trigger = get_amplitude(data_trigger)
    return [data_signal, data_trigger, t_signal, t_trigger, amplitude_signal, amplitude_trigger, min_signal, min_trigger]


def remote_Osci(config):
    ip = config[0]
    save_folder = config[1]
    measurement_name = config[2]
    signal_channel = config[3]
    trigger_channel = config[4]
    tl_value, tl_unit = config[5].split(' ')
    trigger_level = Q_(float(tl_value), tl_unit)
    trigger_mode = str(config[6])
    ts_value, ts_unit  = config[7].split(' ')
    timescale = Q_(float(ts_value), ts_unit)
    recordlength = int(config[8])
    samplerate = int(config[9])
    repetitions = int(config[10])
    cf_factor = float(config[11])
    msp_value, msp_unit = config[12].split(' ')
    min_signal_peak = Q_(float(msp_value), msp_unit)

    #  initilise the oscillospoe witht the settings from the config file
    dev = MSO5204(ip=ip)
    dev.setTriggerMode(mode=trigger_mode)
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
        file.writelines(f'# t_signal[s]\tt_trigger[s]\tsignal_amplitude[V]\ttrigger_amplitude[V]\tmin_signal[V]\tmin_trigger[V]\tcf_factor = {cf_factor}\t Trigger: CH{trigger_channel}, Signal: CH{signal_channel}')

        acq_number_prev = dev.getAcqNumber()

        #  initialise old_data
        old_data = np.zeros(6)

        #  loop over the wanted repetitions. An error handling block is included, to ensure a stable readout
        for i in tqdm(range(repetitions), desc='Sr90'):
            blockPrint()
            try:
                return_data = pipeline(dev=dev, signal_channel=signal_channel, trigger_channel=trigger_channel,  recordlength=recordlength, cf_factor=cf_factor, min_signal_peak=min_signal_peak)
                while check_data(old_data, return_data):
                    return_data = pipeline(dev=dev, signal_channel=signal_channel, trigger_channel=trigger_channel,  recordlength=recordlength, cf_factor=cf_factor, min_signal_peak=min_signal_peak)
            except NoPeak:
                return_data = False
                try:
                    while (not return_data) or check_data(old_data, return_data):
                        return_data = handle_NoPeak(dev=dev, signal_channel=signal_channel, trigger_channel=trigger_channel,  recordlength=recordlength, cf_factor=cf_factor, min_signal_peak=min_signal_peak)
                except Exception:
                    e = sys.exc_info()[0]
                    return_data = False
                    while (not return_data) or check_data(old_data, return_data):
                        return_data = handle_allErrors(dev=dev, signal_channel=signal_channel, trigger_channel=trigger_channel,  recordlength=recordlength, cf_factor=cf_factor, min_signal_peak=min_signal_peak, exception=e)
            except Exception:
                e = sys.exc_info()[0]
                return_data = False
                while (not return_data) or check_data(old_data, return_data):
                    return_data = handle_allErrors(dev=dev, signal_channel=signal_channel, trigger_channel=trigger_channel,  recordlength=recordlength, cf_factor=cf_factor, min_signal_peak=min_signal_peak, exception=e)

            data_signal, data_trigger = return_data[0], return_data[1]
            t_signal, t_trigger = return_data[2], return_data[3]
            amplitude_signal, amplitude_trigger = return_data[4], return_data[5]
            min_signal, min_trigger = return_data[6], return_data[7]

            #  saving the data as a pdf and txt files. The trigger and signal data are seperately saved in txt files
            savetopdf_90sr([data_signal, data_trigger], [t_signal, t_trigger], cf_factor, folder=f'{os.path.join(save_folder, measurement_name)}/Pictures', file_name=f'{measurement_name}_pic{i}')
            dev.savetotxt(file_name=f'{measurement_name}_triggerFile{i}', xdata=data_trigger[0], ydata=data_trigger[1], folder=f'{os.path.join(save_folder, measurement_name)}/data_files', supress_file_check=True)
            dev.savetotxt(file_name=f'{measurement_name}_signalFile{i}', xdata=data_signal[0], ydata=data_signal[1], folder=f'{os.path.join(save_folder, measurement_name)}/data_files', supress_file_check=True)

            file.writelines(f'\n{t_signal}\t{t_trigger}\t{amplitude_signal}\t{amplitude_trigger}\t{min_signal}\t{min_trigger}')
            old_data = return_data[2:]

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
    except:
        enablePrint()
        e = sys.exc_info()[0]
        sys.exit(f'\nAn Error occured: {e}')


if __name__ == '__main__':
    main()
