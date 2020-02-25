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
#from devices import TTI2
from devices import MOTH

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
    mes_name='Temperature'

    # set TTI2
    TEMP = MOTH(args.connection_type,args.connection_host,args.connection_port)
    temp_unit = '[C]'

    # start measurement
    print('This measurement runs until ctrl+C is pressed!')
    # get and input data into influxDB
    try:
        while True:
            temp1 = TEMP.getEnvTemperature()
            temp2 = TEMP.getNtcTemperature()
            print('Temp1:'+temp1+ 'C \t Temp2:'+temp2+ 'C')
            #now=datetime.utcnow()
            #str_now=datetime.strftime(now,'%Y-%m-%dT%H:%M:%SZ')

            data=[
                  { 
                   'fields' : { 
                                'temp1' : temp1,
                                'temp2' : temp2
                              },
                   'measurement' : mes_name,
                   'time':datetime.utcnow(),
                   #'time':str_now,
                   'tags':{
                           'temp1_unit':temp_unit,
                           'temp2_unit':temp_unit
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

