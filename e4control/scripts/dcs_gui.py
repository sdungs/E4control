# -*- coding: utf-8 -*-

import os
import sys
import argparse
import time
import termios, tty
import PySimpleGUI as sg
import numpy as np
from e4control import __version__ as version

# This is to include a matplotlib figure in a Tkinter canvas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from threading import Thread

from .. import utils as sh


# arg parser
parser = argparse.ArgumentParser()
parser.add_argument('config', help='config file')
parser.add_argument('-l', '--logfile', help='potential logfile')

def get_timestamp(starttime):
    time_now = time.time()
    timestamp = (time_now - starttime) / 60
    h, s = divmod(timestamp, 1)
    return int(np.round(h, 0)) , int(np.round(s * 60, 0)), time_now


def change_channel(device_dict, iChannel):
    number_channels = device_dict['channel']
    layout_device_channel = [
            [sg.Text('Which Channel?')]
    ]
    button_names_channel = []
    for i in np.linspace(1, number_channels, number_channels):
        layout_device_channel.append([sg.Button(f'CH{int(i)}')])
        button_names_channel.append(f'CH{int(i)}')

    if not iChannel == -1:
        layout_device_channel.append([sg.Button('Back')])

    window_channel = sg.Window('Select Channel', layout_device_channel)

    while True:
        event_channel, value_channel = window_channel.read()
        if event_channel == sg.WIN_CLOSED:
            window_channel.close()
            abort('Error: No Channel assigned.')
            break
        if event_channel == 'Back':
            window_channel.close()
            switch = False
            break
        if event_channel in button_names_channel:
            iChannel = button_names_channel.index(event_channel)
            window_channel.close()
            switch = True
            break
    if switch == False:
        return iChannel
    else:
        return iChannel + 1


def toogle_output(device, iChannel):
    if bool(int(device.getOutput(iChannel))):
        device.rampVoltage(0, iChannel)
        device.setOutput(False, iChannel)
    else:
        device.setOutput(True, iChannel)
pass


def toogle_power(device):
    if int(bool(device.getPowerStatus())):
        device.enablePower(False)
    else:
        device.enablePower(True)
pass


def enable_OCP(device, iChannel):
    layout_OCP = [
            [sg.Text(f'Enable OCP:')],
            [sg.Button('Yes'), sg.Button('No')],
            [sg.Button('Back')]
    ]
    window_OCP = sg.Window(f'Set Mode', layout_OCP)
    while True:
        event_OCP, value_OCP = window_OCP.read()
        if event_OCP == sg.WIN_CLOSED or event_OCP == 'Back':
            window_OCP.close()
            break
        if event_OCP in ['Yes', 'No']:
            if event_OCP == 'Yes':
                device.enableOCP(True)
            elif event_OCP == 'No':
                device.enableOCP(False)
            window_OCP.close()
            break
    pass


def change_mode(device):
    layout_mode = [
            [sg.Text(f'Choose Mode:')],
            [sg.Button('int'), sg.Button('ext')],
            [sg.Button('Back')]
    ]
    window_mode = sg.Window(f'Set Mode', layout_mode)
    while True:
        event_mode, value_mode = window_mode.read()
        if event_mode == sg.WIN_CLOSED or event_mode == 'Back':
            window_mode.close()
            break
        if event_mode in ['int', 'ext']:
            device.setOperationMode(event_mode)
            window_mode.close()
            break
    pass

def change_operation_mode(device):
    layout_operation_mode = [
            [sg.Text(f'Choose Operation Mode:')],
            [sg.Button('climate'), sg.Button('normal')],
            [sg.Button('Back')]
    ]
    window_operation_mode = sg.Window(f'Set Mode', layout_operation_mode)
    while True:
        event_operation_mode, value_operation_mode = window_operation_mode.read()
        if event_operation_mode == sg.WIN_CLOSED or event_operation_mode == 'Back':
            window_operation_mode.close()
            break
        if event_operation_mode in ['climate', 'normal']:
            device.setOperationMode(event_operation_mode)
            window_operation_mode.close()
            break
    pass

def general_interaction(device, interaction_name, interaction_unit, interaction_function, channel):
    key_str = 'new_value'
    layout_general_interaction = [
            [sg.Text(f'Type in new {interaction_name}:')],
            [sg.Input(key=key_str), sg.Text(interaction_unit), sg.Button('Ok')],
            [sg.Button('Back')]
    ]
    window_general_interaction = sg.Window(f'Set {interaction_name}', layout_general_interaction)
    while True:
        event_general_interaction, values_general_interaction = window_general_interaction.read()
        if event_general_interaction == sg.WIN_CLOSED or event_general_interaction == 'Back':
            window_general_interaction.close()
            break
        if event_general_interaction == 'Ok':
            exec(f'device.{interaction_function}(float(values_general_interaction[key_str]), channel)')
            window_general_interaction.close()
            break
    pass


def control_window(devices, fw):
    blockPrint()
    starttime = time.time()
    iChannel = -1 # default value, if a device does not has any channels
    layout = [
            [sg.Text('CONTROL CENTER', size=(14,3))],
            [sg.Text('Runtime: '), sg.Text(size=(2,1), key=f'timestamp_min'), sg.Text('min'), sg.Text(size=(2,1), key=f'timestamp_sec'), sg.Text('s')],
    ]

    device_counter = 0
    device_names = []
    for d in devices:
        device_name = d.__class__.__name__
        device_names.append(f'{device_name}')
        layout.append([sg.Text(f'\n{device_name}', size=(len(device_name), 2))])
        header, values = d.output()
        for h, v in zip(header, values):
            layout.append([sg.Text(f'{h}:\t'), sg.Text(size=(12,1), key=f'{h}{device_counter}')])
        device_counter += 1
    layout.append([sg.Button('Change'), sg.Button('Quit')])

    window = sg.Window(f'E4control v{version}: Device control script', layout)

    while True:
        event, value = window.read(timeout=0)
        if event == sg.WIN_CLOSED or event == 'Quit':
            window.close()
            abort()


        if event == 'Change':
            layout_change = []
            device_counter = 0
            button_names_change = []
            for d in device_names:
                if device_names.count(d) > 1:
                    button_names_change.append(f'{d} {device_counter}')
                    layout_change.append([sg.Button(f'{d} {device_counter}')])
                    device_counter += 1
                else:
                    button_names_change.append(f'{d}')
                    layout_change.append([sg.Button(f'{d}')])



            layout_change.append([sg.Button('Back')])

            window_change = sg.Window('List of active devices', layout_change)
            while True:
                event_change, value_change = window_change.read()
                if event_change == sg.WIN_CLOSED or event_change == 'Back':
                    window_change.close()
                    break
                if event_change in button_names_change:
                    device_change = devices[button_names_change.index(event_change)]
                    device_interaction_dict = device_change.interaction(gui=True)
                    d_i_d_keys = list(device_interaction_dict.keys())
                    layout_device_interaction = []
                    if 'pass' in d_i_d_keys:
                        layout_device_interaction.append([sg.Text('Nothing to do.')])

                    if 'channel' in d_i_d_keys:
                        iChannel = change_channel(device_interaction_dict, iChannel)

                        layout_device_interaction.append(
                                [sg.Text(f'Current Channel: ', size=(18, 2)), sg.Text(size=(3, 2), key='CH'), sg.Button('Switch Channel')]
                        )

                    if 'toogleOutput' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'Output: ', size=(18, 2)), sg.Text(size=(3, 2), key='Output_status'), sg.Button('Toogle Output')]
                        )

                    if 'enablePower' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'Power: ', size=(18, 2)), sg.Text(size=(3, 2), key='power_status'), sg.Button('Toogle Power')]
                        )

                    if 'setMode' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'Mode: ', size=(18, 2)), sg.Text(size=(3, 2), key='mode_status'), sg.Button('Change Mode')]
                        )

                    if 'setOperationMode' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'Operation Mode: ', size=(18, 2)), sg.Text(size=(8, 2), key='operation_mode_status'), sg.Button('Change Operation Mode')]
                        )

                    if 'getStatus' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'Status: ', size=(18, 2)), sg.Text(size=(15, 2), key='status_status')]
                        )

                    if 'rampVoltage' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'Voltage: ', size=(18, 2)), sg.Text(size=(15, 2), key='ramp_voltage_status'), sg.Text('V', size=(2,2)), sg.Button('Change Voltage')]
                        )

                    if 'setVoltage' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'Voltage: ', size=(18, 2)), sg.Text(size=(15, 2), key='set_voltage_status'), sg.Text('V', size=(2,2)), sg.Button('Set Voltage')]
                        )

                    if 'setCurrent' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'Current: ', size=(18, 2)), sg.Text(size=(15, 2), key='current_status'), sg.Text('A', size=(2,2)), sg.Button('Set Current')]
                        )

                    if 'setCurrentLimit' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'Current Limit: ', size=(18, 2)), sg.Text(size=(15, 2), key='current_limit_status'), sg.Text('uA', size=(2,2)), sg.Button('Set Current Limit')]
                        )

                    if 'getSetTemperature' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'Temperature: ', size=(18, 2)), sg.Text(size=(15, 2), key='getin_temperature_status'), sg.Text('C', size=(2,2))]
                        )
                        layout_device_interaction.append(
                                [sg.Text(f'Set Temperature: ', size=(18, 2)), sg.Text(size=(15, 2), key='getset_temperature_status'), sg.Text('C', size=(2,2)), sg.Button('Set Temperature')]
                        )

                    if 'setHumidity' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'Humidity: ', size=(18, 2)), sg.Text(size=(15, 2), key='humidity_status'), sg.Text('%', size=(2,2))]
                        )
                        layout_device_interaction.append(
                                [sg.Text(f'Set Humidity: ', size=(18, 2)), sg.Text(size=(15, 2), key='set_humidity_status'), sg.Text('%', size=(2,2)), sg.Button('Change Set Humidity')]
                        )

                    if 'setTemperature' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'Temperature: ', size=(18, 2)), sg.Text(size=(15, 2), key='temperature_status'), sg.Text('C', size=(2,2))]
                        )
                        layout_device_interaction.append(
                                [sg.Text(f'Set Temperature: ', size=(18, 2)), sg.Text(size=(15, 2), key='set_temperature_status'), sg.Text('C', size=(2,2)), sg.Button('Set Temperature')]
                        )

                    if 'setOVP' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'OVP: ', size=(18, 2)), sg.Text(size=(15, 2), key='ovp_status'), sg.Text('V', size=(2,2)), sg.Button('Set OVP')]
                        )

                    if 'enableOCP' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Button('Enable OCP')]
                        )


                    layout_device_interaction.append([sg.Button('Back')])

                    window_device_interaction = sg.Window(f'{device_change.__class__.__name__}', layout_device_interaction)

                    while True:
                        event_interaction, values_interaction = window_device_interaction.read(timeout=0)
                        if event_interaction == sg.WIN_CLOSED or event_interaction == 'Back':
                            window_device_interaction.close()
                            break
                        if 'channel' in d_i_d_keys:
                            window_device_interaction['CH'].update(iChannel)
                        if event_interaction == 'Switch Channel':
                            iChannel = change_channel(device_interaction_dict, iChannel)
                        if 'toogleOutput' in d_i_d_keys:
                            if bool(int(device_change.getOutput(iChannel))):
                                output_status = 'On'
                            else:
                                output_status = 'Off'
                            window_device_interaction['Output_status'].update(output_status)
                        if event_interaction == 'Toogle Output':
                            toogle_output(device_change, iChannel)
                        if 'enablePower' in d_i_d_keys:
                            if bool(int(device_change.getPowerStatus())):
                                power_status = 'On'
                            else:
                                power_status = 'Off'
                            window_device_interaction['power_status'].update(power_status)
                        if event_interaction == 'Toogle Power':
                            toogle_power(device_change)
                        if 'setMode' in d_i_d_keys:
                            mode_status = device_change.getOperationMode()
                            window_device_interaction['mode_status'].update(mode_status)
                        if 'setOperationMode' in d_i_d_keys:
                            operation_mode_status = device_change.getOperationMode()
                            window_device_interaction['operation_mode_status'].update(operation_mode_status)
                        if 'getStatus' in d_i_d_keys:
                            status_status = device_change.getStatus()
                            window_device_interaction['status_status'].update(status_status)
                        if event_interaction == 'Change Mode':
                            change_mode(device_change)
                        if event_interaction == 'Change Operation Mode':
                            change_operation_mode(device_change)
                        if 'rampVoltage' in d_i_d_keys:
                            ramp_voltage_status = device_change.getVoltage(iChannel)
                            window_device_interaction['ramp_voltage_status'].update(ramp_voltage_status)
                        if event_interaction == 'Change Voltage':
                            general_interaction(device_change, 'voltage', 'V', 'rampVoltage', iChannel)
                        if 'setVoltage' in d_i_d_keys:
                            set_voltage_status = device_change.getVoltage(iChannel)
                            window_device_interaction['set_voltage_status'].update(set_voltage_status)
                        if event_interaction == 'Set Voltage':
                            general_interaction(device_change, 'voltage', 'V', 'setVoltage', iChannel)
                        if 'setCurrent' in d_i_d_keys:
                            current_status = device_change.getCurrent(iChannel)
                            window_device_interaction['current_status'].update(current_status)
                        if event_interaction == 'Set Current':
                            general_interaction(device_change, 'current', 'A', 'setCurrent', iChannel)
                        if 'setCurrentLimit' in d_i_d_keys:
                            current_limit_status = device_change.getCurrentLimit(iChannel)
                            window_device_interaction['current_limit_status'].update(current_limit_status)
                        if event_interaction == 'Set Current Limit':
                            general_interaction(device_change, 'current limit', 'uA', 'setCurrentLimit', iChannel)
                        if 'getSetTemperature' in d_i_d_keys:
                            getset_temperature_status = device_change.getSetTemperature()
                            getin_temperature_status = device_change.getInTemperature()
                            window_device_interaction['getset_temperature_status'].update(getset_temperature_status)
                            window_device_interaction['getin_temperature_status'].update(getin_temperature_status)
                        if 'setTemperature' in d_i_d_keys:
                            temperature_status = device_change.getTemperature()
                            set_temperature_status = device_change.getSetTemperature()
                            window_device_interaction['temperature_status'].update(temperature_status)
                            window_device_interaction['set_temperature_status'].update(set_temperature_status)
                        if event_interaction == 'Set Temperature':
                            general_interaction(device_change, 'temperature', 'C', 'setTemperature', iChannel)
                        if 'setHumidity' in d_i_d_keys:
                            humidity_status = device_change.getHumidity()
                            set_humidity_status = device_change.getSetHumidity()
                            window_device_interaction['humidity_status'].update(humidity_status)
                            window_device_interaction['set_humidity_status'].update(set_humidity_status)
                        if event_interaction == 'Change Set Humidity':
                            general_interaction(device_change, 'humidity', '%', 'setHumidity', iChannel)
                        if 'setOVP' in d_i_d_keys:
                            ovp_status = device_change.getVoltageLimit()
                            window_device_interaction['ovp_status'].update(ovp_status)
                        if event_interaction == 'Set OVP':
                            general_interaction(device_change, 'OVP', 'V', 'setVoltageLimit', iChannel)
                        if event_interaction == 'Enable OCP':
                            enable_OCP(device_change, iChannel)
                        time.sleep(0.5)
                    iChannel = -1 # reset iChannel to its default value -1 after the change window is closed

            # {
            # 'pass': ,
            # 'channel': ,
            # 'enableOutput': ,
            # 'toogleOutput'
            # 'rampVoltage': ,
            # 'setVoltage': ,
            # 'setCurrent': ,
            # 'setCurrentLimit': ,
            # 'setTemperature': ,
            # 'setHumidity': ,
            # 'enablePower': ,
            # 'getStatus': ,
            # 'enableOCP': ,
            # 'setOVP': ,
            # 'setMode': ,
            # 'setPowerMode': ,
            # 'setOperationMode': ,
            # }
            # x = int(input('Choose the number of a Device:'))
            # if (x-1) in range(len(config_devices)):
            #     devices[x-1].interaction()
            # else:
            #     continue
        device_counter = 0
        h, s, time_now = get_timestamp(starttime)
        all_values = [time_now]
        window['timestamp_min'].update(h)
        window['timestamp_sec'].update(s)

        for d in devices:
            header, values = d.output()
            for h, v in zip(header, values):
                window[f'{h}{device_counter}'].update(float(v))
                all_values.append(float(v))
            device_counter += 1

        if not fw == -1:
            sh.write_line(fw, all_values)
        time.sleep(1)
    enablePrint()
    pass


def show_dcs_device_list_gui(devices):

    layout = []
    for i in devices:
        layout.append([sg.Text(i)])


    layout.append([sg.Text('Correct devices?')])
    layout.append([sg.Button('Yes'), sg.Button('No')])
    window = sg.Window(f'E4control v{version}: Device control script', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'No':
            window.close()
            abort()
        elif event == 'Yes':
            window.close()
            break
    pass


def welcome_dcs_gui(config):
    layout = [
            [sg.Text(f'This is e4control, v{version}.')],
            [sg.Text(f'If you are not familiar with this version, please check the log (via \"git log\") for recent changes.')],
            [sg.Text('')],
            [sg.Text(f'Selected configfile: {config}')],
            [sg.Button('Contine'), sg.Button('Quit')]
    ]
    window = sg.Window(f'E4control v{version}: Device control script', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Quit':
            window.close()
            abort()
            sys.exit()
        elif event == 'Contine':
            window.close()
            break
    pass


def abort(err_msg=False):
    if err_msg:
        layout = [
                [sg.Text(f'{err_msg}')],
                [sg.Button('Quit')]
        ]
    else:
        layout = [
                [sg.Text(f'Aborted!')],
                [sg.Button('Quit')]
        ]
    window = sg.Window(f'E4control v{version}: Device control script', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Quit':
            window.close()
            sys.exit()
    pass


# Disable printing
def blockPrint():
    sys.stdout = open(os.devnull, 'w')
    pass


# Restore printing
def enablePrint():
    sys.stdout = sys.__stdout__
    pass


def main():
    args = parser.parse_args()
    welcome_dcs_gui(args.config)

    # read configfile
    config_devices = sh.read_dcs_config(args.config)

    # create setting query
    show_dcs_device_list_gui(config_devices)

    # connection
    devices = sh.connect_dcs_devices(config_devices)

    # check if SHT75 is used for T and H, remove one as T and H are always displayed
    for idx_h,d_h in enumerate(config_devices):
        if d_h[0]=='H' and d_h[1]=='SHT75':
            for idx_t,d_t in enumerate(config_devices):
                if d_t[0]=='T' and d_t[1]=='SHT75':
                    if d_h[3]==d_t[3]:
                        # devices[idx_h]=devices[idx_t]
                        devices.pop(idx_h)
                        print('Linked H{} with T{}.'.format(idx_h+1,idx_t+1))

    # logfile
    if args.logfile:
        blockPrint()
        checktxtfile = (args.logfile + '.txt')
        if os.path.isfile(checktxtfile):
            sys.exit('logfile ' + args.logfile + ' already exists!')
        fw = sh.new_txt_file(args.logfile)
        header = ['time']
        d_names = []
        for i in config_devices:
            d_names.append('|')
            d_names.append(i[0])
            d_names.append(i[1])
            d_names.append('|')
        for i in devices:
            header = header + (i.output(show=False)[0])
        sh.write_line(fw, d_names)
        sh.write_line(fw, header)
        enablePrint()
    else:
        fw = -1

    control_window(devices, fw)

    # print(threadKey.is_alive())
    for d in devices:
        d.close()
    if args.logfile:
        sh.close_txt_file(fw)


if __name__ == '__main__':
    main()
