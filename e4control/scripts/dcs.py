# -*- coding: utf-8 -*-

import os
import sys
import argparse
import time
import termios, tty

from threading import Thread

from .. import utils as sh

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


def print(string):
    sys.stdout.write(string + '\r\n')


def main():
    args = parser.parse_args()

    # print welcome message
    sh.print_welcome()

    # read configfile
    config_devices = sh.read_dcs_config(args.config)

    # create setting query
    sh.show_dcs_device_list(config_devices)

    # connection
    devices = sh.connect_dcs_devices(config_devices)

    # check if SHT75 is used for T and H, remove one as T and H are always displayed
    for idx_h, d_h in enumerate(config_devices):
        if d_h[0] == 'H' and d_h[1] == 'SHT75':
            for idx_t, d_t in enumerate(config_devices):
                if d_t[0] == 'T' and d_t[1] == 'SHT75':
                    if d_h[3] == d_t[3]:
                        # devices[idx_h]=devices[idx_t]
                        devices.pop(idx_h)
                        print('Linked H{} with T{}.'.format(idx_h + 1, idx_t + 1))

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

    starttime = time.time()

    while True:
        key_thread = pressedKeyThread()
        key_thread.start()
        while key_thread.is_alive():
            values = [str(time.time())]
            print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
            timestamp = (time.time() - starttime) / 60
            h, s = divmod(timestamp, 1)
            # timestamp = time.strftime('%a, %d %b %Y %H:%M:%S ', time.localtime())
            print(' \033[35m CONTROL CENTER \t ' + 'runtime: %.0f min %.0f s \033[0m' % (h, s * 60))
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
            if args.logfile:
                sh.write_line(fw, values)
            time.sleep(1)
            print('press c (=CHANGE PARAMETER) or q (=QUIT)')
            print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
            if key_thread.is_alive():
                time.sleep(10)
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
                print('%i: %s' % (i + 1, config_devices[i][1]))
            x = int(input('Choose the number of a Device:'))
            if (x - 1) in range(len(config_devices)):
                devices[x - 1].interaction()
            else:
                continue
        else:
            print('Cannot handle this key. Continuing.')
            time.sleep(1)

    # print(threadKey.is_alive())
    for d in devices:
        d.close()
    if args.logfile:
        sh.close_txt_file(fw)


if __name__ == '__main__':
    main()
