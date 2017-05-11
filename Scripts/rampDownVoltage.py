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

#set active source
d = source[0]
ch = source_channel[0]

#initialize
d.initialize(ch)
d.enableOutput(True,ch)

#ramp down voltage
d.rampVoltage(0,ch)
d.enableOutput(False)

#close files
for s in source:
    s.close()
