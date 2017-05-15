#!/usr/bin/env python
# -*- coding: utf-8 -*-

import script_header as sh
import argparse

parser=argparse.ArgumentParser()
parser.add_argument("config",help="config file")
args=parser.parse_args()

#read configfile
devices = sh.read_config(args.config)

#connection
source, source_channel = sh.device_connection(devices["S"])

#ramp down voltage(s)
for d in range(len(source)):
    if source_channel[d] == 12:
        source[d].initialize(source_channel[1])
        source[d].enableOutput(True,source_channel[1])
        source[d].rampVoltage(0,source_channel[1])
        source[d].enableOutput(False,source_channel[1])
        source[d].initialize(source_channel[2])
        source[d].enableOutput(True,source_channel[2])
        source[d].rampVoltage(0,source_channel[2])
        source[d].enableOutput(False,source_channel[2])
    else:
        source[d].initialize(source_channel[d])
        source[d].enableOutput(True,source_channel[d])
        source[d].rampVoltage(0,source_channel[d])
        source[d].enableOutput(False,source_channel[d])

#close files
for s in source:
    s.close()
