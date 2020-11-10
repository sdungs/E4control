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

import e4control.utils as sh


# arg parser
parser = argparse.ArgumentParser()
parser.add_argument('config', help='config file')
parser.add_argument('-l', '--logfile', help='potential logfile')

class pressedKeyThread(Thread):
    pressed_key = ''

    def run(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        self.pressed_key = ch
        print('"{}" has been pressed.'.format(self.pressed_key))


def get_timestamp(starttime):
    timestamp = (time.time() - starttime) / 60
    h, s = divmod(timestamp, 1)
    return int(np.round(h, 0)) , int(np.round(s * 60, 0))


def change_channel(device_dict):
    number_channels = device_dict['channel']
    layout_device_channel = [
            [sg.Text('Which Channel?')]
    ]
    button_names_channel = []
    for i in np.linspace(1, number_channels, number_channels):
        layout_device_channel.append([sg.Button(f'CH{int(i)}')])
        button_names_channel.append(f'CH{int(i)}')

    window_channel = sg.Window('Select Channel', layout_device_channel)

    while True:
        event_channel, value_channel = window_channel.read()
        if event_channel == sg.WIN_CLOSED:
            window_channel.close()
            abort('Error: No Channel assigned.')
            break
        if event_channel in button_names_channel:
            iChannel = button_names_channel.index(event_channel)
            window_channel.close()
            break
    return iChannel + 1


def toogle_output(device):
    if device.getOutput() == '1':
        device.rampVoltage(0)
        device.setOutput(False)
        return 'Off'
    else:
        device.setOutput(True)
        return 'On'


def control_window(devices):
    starttime = time.time()
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
        blockPrint()
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
                    iChannel = 0 # default value, if a device does not has any channels
                    device_change = devices[button_names_change.index(event_change)]
                    device_interaction_dict = device_change.interaction(gui=True)
                    d_i_d_keys = list(device_interaction_dict.keys())
                    button_names_interaction = []
                    layout_device_interaction = []
                    if 'pass' in d_i_d_keys:
                        layout_device_interaction.append([sg.Text('Nothing to do.')])

                    if 'channel' in d_i_d_keys:
                        iChannel = change_channel(device_interaction_dict)

                        layout_device_interaction.append(
                                [sg.Text(f'Current Channel: ', size=(18, 2)), sg.Text(size=(3, 2), key='CH'), sg.Button('Switch Channel')]
                        )
                        button_names_interaction.append('Switch Channel')

                    if 'toogleOutput' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'Output: ', size=(18, 2)), sg.Text(size=(3, 2), key='Output_status'), sg.Button('Toogle Output')]
                        )
                        # layout_device_interaction.append([sg.Button('Toogle Output')])
                        button_names_interaction.append('Toogle Output')

                    if 'setVoltage' in d_i_d_keys:
                        layout_device_interaction.append(
                                [sg.Text(f'Voltage: ', size=(18, 2)), sg.Text(size=(10, 2), key='voltage_status'), sg.Text('V', size=(2,2)), sg.Button('Change Voltage')]
                        )
                        # layout_device_interaction.append([sg.Button('Change Voltage')])
                        button_names_interaction.append('Toogle Output')



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
                            iChannel = change_channel(device_interaction_dict)
                        if 'toogleOutput' in d_i_d_keys:
                            if device_change.getOutput() == '1':
                                output_status = 'On'
                            else:
                                output_status = 'Off'
                            window_device_interaction['Output_status'].update(output_status)
                        if event_interaction == 'Toogle Output':
                            output_status = toogle_output(device_change)

            # {
            # 'pass': ,
            # 'channel': ,
            # 'enableOutput': ,
            # 'toogleOutput'
            # 'setVoltage': ,
            # 'setCurrent': ,
            # 'serCurrentLimit': ,
            # 'setTemperature': ,
            # 'getStatus': ,
            # }
            # x = int(input('Choose the number of a Device:'))
            # if (x-1) in range(len(config_devices)):
            #     devices[x-1].interaction()
            # else:
            #     continue
        device_counter = 0
        for d in devices:
            header, values = d.output()
            for h, v in zip(header, values):
                window[f'{h}{device_counter}'].update(v)
            device_counter += 1

        h, s = get_timestamp(starttime)
        window['timestamp_min'].update(h)
        window['timestamp_sec'].update(s)
        time.sleep(1)
    enablePrint()


    while True:
        key_thread = pressedKeyThread()
        key_thread.start()
        while key_thread.is_alive():
            values = [str(time.time())]
            print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
            timestamp = (time.time()-starttime) / 60
            h, s = divmod(timestamp, 1)
            # timestamp = time.strftime('%a, %d %b %Y %H:%M:%S ', time.localtime())
            print(' \033[35m CONTROL CENTER \t ' + 'runtime: %.0f min %.0f s \033[0m' % (h, s*60))
            print('-----------------------------------------------------')
            for d in devices:
                try:
                    h, v = d.output()
                    values += v
                    print('-----------------------------------------------------')
                except:
                    h = []
                    v = []
                    h, v = d.output()
                    values += v
                    print('-----------------------------------------------------')
            # if args.logfile:
                # sh.write_line(fw, values)
            time.sleep(1)
            print('press c (=CHANGE PARAMETER) or q (=QUIT)')
            print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
            if key_thread.is_alive():
                time.sleep(5)
            print('')

        key_thread.join()
        key = key_thread.pressed_key
        print('Interpreting "{}" key...'.format(key_thread.pressed_key))

        if key == 'q':
            print('Quitting...')
            break

        if key == 'c':
            print('List of active Devices:')
            print('0: Continue dcs mode without changes')
            for i in range(len(config_devices)):
                print('%i: %s' % (i+1, config_devices[i][1]))
            x = int(input('Choose the number of a Device:'))
            if (x-1) in range(len(config_devices)):
                devices[x-1].interaction()
            else:
                continue
        else:
            print('Cannot handle this key. Continuing.')
            time.sleep(1)


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
    # pass

# Restore printing
def enablePrint():
    sys.stdout = sys.__stdout__


# def print(string):
#     sys.stdout.write(string+'\r\n')

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

    control_window(devices)

    # print(threadKey.is_alive())
    for d in devices:
        d.close()
    if args.logfile:
        sh.close_txt_file(fw)


if __name__ == '__main__':
    main()
