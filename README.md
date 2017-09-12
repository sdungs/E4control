# E4control v0.0.1
E4control is a python based software for device controlling and data taking.

It consists of two packages: **devices** and **scripts**.

## Devices
Following devices are currently supported:
- Hameg HMP4040 (Power Supply)
- HP 4284A (LCR Meter)
- Iseg SHQ (Source Meter)
- Julabo FP88 (Chiller)
- Keithley 196 (Multimeter)
- Keithley 487 (Picoammeter/Voltage Source)
- Keithley 2000 (Multimeter)
- Keithley 2410 (Source Meter)
- TTi TSX3510P (Power Supply)
- Weiss SB22 (Climate Chamber)

## Scripts
- *e4control_measure_IV* , to perform a current vs voltage measurement
- *e4control_measure_CV* , to perform a capacity vs voltage measurement
- *e4control_measure_It* , to perform a current vs time measurement
- *e4control_testbeamDCS* , for manual real time device controlling


## Installation
Python [pip](https://pypi.python.org/pypi/pip) is needed, install it if it is not available yet.
1. download or clone this repository
2. open a terminal and change directory to E4control
3. to install enter: `pip install .`
4. *(add PATH to .bashrc)*

## How to run scripts?
#### config file
A config file with all used devices is needed for every script. For an example see [exampleConfig](https://github.com/sdungs/E4control/blob/master/exampleConfig).
In the first column the purpose of the respective device is written (S = source meter, L = LCR meter, T = temperature device, H = humidity device, C = cooling device). The other columns contain device name, connection type, host and port. *For the testbeamDCS config file the port coulumn must be empty.* The coulums are seperated by a single space.

#### e4control_measure_IV
enter:  
`e4control_measure_IV V_min V_max output config -I I_lim -s V_steps -n ndaqs -d delay `

- V_min   -> starting voltage | float | in V
- V_max   -> end voltage | float | in V
- output  -> output directory name | string
- config  -> config file name | string
- I_lim   -> current limit | float | in uA
- V_steps -> number of voltage steps | int
- ndaqs   -> number of data acquistion at every set voltage | int
- delay   -> delay after setting new voltage | int | in s

example:  
`e4control_measure_IV 0 100 meas_1 config_IV -I 3 -s 11 -n 5 -d 2 `

#### e4control_measure_CV
enter:  
`e4control_measure_CV V_min V_max output config -s V_steps -n ndaqs -d delay -f lcr_frequenz`

- V_min   -> starting voltage | float | in V
- V_max   -> end voltage | float | in V
- output  -> output directory name | string
- config  -> config file name | string
- V_steps -> number of voltage steps | int
- ndaqs   -> number of data acquistion at every set voltage | int
- delay   -> delay after setting new voltage | int | in s
- lcr_frequenz -> LCR meter frequenz | float | in Hz   

example:  
`e4control_measure_CV 0 100 meas_2 config_CV -s 11 -n 5 -d 2 -f 10000`

#### e4control_measure_It
enter:  
`e4control_measure_It output config -v voltage -n ndaqs -d delay -p plot `

- output  -> output directory name | string
- config  -> config file name | string
- voltage -> constant set voltage | float | in V
- ndaqs   -> number of data acquistion at every measure point | int
- delay   -> delay between two measure points | int | in s
- plot    -> enable or disable live plotting | 0 == off, 1 == on

*this measurement is running until ctrl+C has been pressed*

example:  
`e4control_measure_It meas_3 config_It -v 50 -n 5 -d 30 -p 1`

#### e4control_testbeamDCS
enter:  
`e4control_testbeamDCS config -l logfile `

- config  -> config file name | string
- logfile -> logfile name | string

example:  
`e4control_testbeamDCS config_TDCS -l log_1 ` *with log*  
`e4control_testbeamDCS config_TDCS ` *without log*
