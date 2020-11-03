# -*- coding: utf-8 -*-
"""
Script to readout an MSO5204 Oscilloscope.
It is designed for measurements, where only the signal shape is analysed.
The default setting is that the signal is averaged over 256 acquisitons and than readout.
The output is are two pdf files and a txt tile of the acquired data from the oscilloscope.
One pdf file contains the full signal and the other a zoomed in version around the maximum amplitude of the signal.
"""

from e4control.devices.MSO5204 import MSO5204
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import argparse
from time import sleep
from pint import UnitRegistry
u = UnitRegistry()
Q_ = u.Quantity

parser = argparse.ArgumentParser()
parser.add_argument('config', help='path to the config file')


#  function to find the signal in the data from getWaveform
def find_signal(self, data, full_Signal=False):
	xdata, xunit = data[0].magnitude, data[0].units
	ydata, yunit = data[1].magnitude, data[1].units
	if len(data[1]) > 1000:
		search_range = int(len(data[1]) / 100)
	else:
		search_range = int(len(data[1]) / 5)
	condition = abs(min(data[1])) >= abs(max(data[1]))
	if condition:
		signal_peak = min(data[1])
	else:
		signal_peak = max(data[1])
	index = list(data[1]).index(signal_peak)
	if not full_Signal:
		xdata = xdata[index - search_range:index + search_range]
		ydata = ydata[index - search_range:index + search_range]
	return Q_(data[0].magnitude, data[0].units), Q_(xdata, xunit), Q_(data[1].magnitude, data[1].units) ,Q_(ydata, yunit)

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
    pass

def config_parameters(file_path):
    if os.path.exists(file_path):
        config_file = open(file_path, 'r+')
    else:
        config_file = open(file_path, 'w')
        config_file.writelines(['None\n'] * 9)
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
                param = int(input('Which parameter should be changed?(1, ..., 9)\n'))
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
    Trigger level: 100 millivolt
    Timescale: 2 nanosecond
    Recordlength: 10000
    Samplerate: 10000000000

    For Copy & paste
    129.217.166.109
    Savefolder
    Measurement_Name
    2
    2
    -15 millivolt
    2 nanosecond
    10000
    10000000000
    """

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


    dev = MSO5204(ip=ip)
    dev.setTriggerSource(source=trigger_channel)
    dev.setTriggerlev(level=trigger_level, channel=trigger_channel)
    dev.setModeAverage(pow=8)
    dev.setRecordlength(recordlength)
    dev.setSamplerate(samplerate)
    dev.setTime(timescale)
    sleep(5)
    dev.RunStop()
    data = dev.getWaveform(channel=signal_channel, start=0, stop=recordlength)
    sleep(3)
    dev.RunStart()
    time_full, time, voltage_full, voltage = find_signal(data=data)

    dev.savetotxt(file_name=measurement_name, xdata=time, ydata=voltage, folder=save_folder)
    dev.savetotxt(file_name=measurement_name + '_fullSignal', xdata=time_full, ydata=voltage_full, folder=save_folder)
    dev.savetopdf(file_name=measurement_name, xdata=time, ydata=voltage, folder=save_folder)
    dev.savetopdf(file_name=measurement_name + '_fullSignal', xdata=time_full, ydata=voltage_full, folder=save_folder)

	pass


def main():
    try:
        args = parser.parse_args()
        config = config_parameters(file_path=args.config)
        remote_Osci(config)
    except SystemExit:
        print('\nQuitting')
    except:
        e = sys.exc_info()[0]
        print(f'\nAn Error occured: {e}')


if __name__ == '__main__':
    main()
