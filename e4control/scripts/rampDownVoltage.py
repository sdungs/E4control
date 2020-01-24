#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import argparse
import time

from .. import utils as sh

parser = argparse.ArgumentParser()
parser.add_argument('config', help='config file')
args = parser.parse_args()

# read configfile
devices = sh.read_config(args.config)

# connection
source, source_channel = sh.device_connection(devices['S'])

# ramp down voltage(s)
for d in range(len(source)):
    if source_channel[d] == 12:
        source[d].initialize(source_channel[1])
        source[d].setOutput(True, source_channel[1])
        source[d].rampVoltage(0, source_channel[1])
        remaining = source[d].getCurrent(source_channel[1]) * 1E6
        k = 0
        while k <= 10 and remaining > 0.01:
            print('Please wait! Current still: %0.6f uA' % remaining)
            time.sleep(5)
            remaining = source[d].getCurrent(source_channel[1]) * 1E6
            k += 1
        source[d].setOutput(False, source_channel[1])
        source[d].initialize(source_channel[2])
        source[d].setOutput(True, source_channel[2])
        source[d].rampVoltage(0, source_channel[2])
        remaining = source[d].getCurrent(source_channel[2]) * 1E6
        k = 0
        while k <= 10 and remaining > 0.01:
            print('Please wait! Current still: %0.6f uA' % remaining)
            time.sleep(5)
            remaining = source[d].getCurrent(source_channel[2]) * 1E6
            k += 1
        source[d].setOutput(False, source_channel[2])
    else:
        source[d].initialize(source_channel[d])
        source[d].setOutput(True, source_channel[d])
        source[d].rampVoltage(0, source_channel[d])
        remaining = source[d].getCurrent(source_channel[d]) * 1E6
        k = 0
        while k <= 10 and remaining > 0.01:
            print('Please wait! Current still: %0.6f uA' % remaining)
            time.sleep(5)
            remaining = source[d].getCurrent(source_channel[d]) * 1E6
            k += 1
        source[d].setOutput(False, source_channel[d])

# close files
for s in source:
    s.close()
