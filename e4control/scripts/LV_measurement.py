#!/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import time
import datetime as dt

import numpy as np
import matplotlib.pyplot as plt

from influxdb import InfluxDBClient
from datetime import datetime

#from .. import utils as sh
from devices import TTI2

parser = argparse.ArgumentParser()
parser.add_argument('-dh', '--dbhost', help='host IP address for inluxDB', type=float, default=127.0.0.1)
parser.add_argument('-dp', '--dbport', help='prt number of influxDB', type=int, default=8086)
parser.add_argument('-dn', '--dbname', help='database name in influxDB', type=int, default='dcsDB')
parser.add_argument('-ct', '--connection_type', help='connection type between machine and hardware',type=str)
parser.add_argument('-ch', '--connection_host', help='connection host of hard ware')
parser.add_argument('-cp', '--connection_port', help='port number for hard ware')



def main():
    args = parser.parse_args()

    # set InfluxDB Client 
    client=InfluxDBClient(args.dbhost,args.dbport,args.dbname);
    list_database=client.get_list_database()
    if not {"name" : args.dbname } in list_database :
        client.create_database(args.dbname)
    mes_name='LV'

    # set TTI2
    LV = TTI2(args.connection_type,args.connection_host,args.connection_port)

    # start measurement
    # get and input data into influxDB
    try:
        while True:
            LV_voltage = LV.getVoltage(2) 
            LV_current = LV.getCurrent(2) 
            print('Current: %.3fA \t Voltage: %.2fV' % (LV_current, LV_voltage))
            LV_voltage_unit='[V]'
            LV_current_unit='[A]'

            #now=datetime.utcnow()
            #str_now=datetime.strftime(now,'%Y-%m-%dT%H:%M:%SZ')

            data=[
                  { 
                   'fields' : { 'LV_Current' : LV_current,
                                'LV_Voltage' : LV_voltage
                              },
                   'measurement' : mes_name,
                   'time':datetime.utcnow(),
                   #'time':str_now,
                   'tags':{
                           'LV_Current_unit':LV_current_unit,
                           'LV_Voltage_unit':LV_voltage_unit
                          }
                  }
                 ]

            res=client.write_points(data)

            time.sleep(2)

    except (KeyboardInterrupt, SystemExit):
        print('Measurement was terminated...')

    finally:
        # decrease voltage for PS
        pass
    # wait until the user finishes the measurement
    print('Press "Enter" to close the measurement.')
    input()

if __name__ == '__main__':
    main()

