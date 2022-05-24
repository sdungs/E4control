# E4control v1.8.9
E4control is a python based software for device controlling and data taking.

It consists of two packages: **devices** and **scripts**.

The device classes can be used in any Python environment to establish a communication link and to execute commands, but the easiest way to perform measurements is to run one of the scripts provided.

## Devices
Following devices are currently supported:
- Espec LU-114 (Climate Chamber)
- HP 4284A (LCR Meter)
- Huber Minichiller (Chiller)
- Iseg SHQ (Source Meter)
- Iseg SHR (Source Meter)
- Julabo FP88 (Chiller)
- Keithley 196 (Multimeter)
- Keithley 487 (Picoammeter/Voltage Source)
- Keithley 617 (Electrometer)
- Keithley 2000 (Multimeter)
- Keithley 2410 (Source Meter)
- Keithley 2614 (Source Meter)
- Physical Instruments C804 (xyz-stage controller)
- Rohde&Schwarz HMP4040 (Power Supply)
- Sensirion SHT75 (Temperature & Humidity Sensor, connected via a RasPi)
- TENMA 72-2710 (Power Supply)
- TENMA 72-13330 (Power Supply)
- TTi TSX3510P (Power Supply)
- Weiss SB22 (Climate Chamber)

## Scripts
- *e4control_measure_IV* , to perform a current vs voltage measurement
- *e4control_measure_CV* , to perform a capacity vs voltage measurement
- *e4control_measure_It* , to perform a current vs time measurement
<!-- - *e4control_measure_Cint*, to perform a capcity vs. voltage measurement with hold for 'hold_t' at 'hold_v' for 'times' times -->
- *e4control_dcs* , for manual real time device controlling
- *e4control_dcs_gui* , for manual real time device controlling using a gui


## Installation
### Prerequisites
To use e4control, Python is needed. To ease installation, [pip for Python](https://pypi.python.org/pypi/pip) is also needed.

Please note that the software is only tested with Python 3 & pip3, although it may work with Python 2 as well. But at least the SHT sensor requires Python 3 to run.

### Installation procedure
1. Download or clone this repository.
2. Open a terminal and change directory to E4control.
3. For installation enter: `pip install .` (Ensure python3/pip3 usage!)
4. *(add PATH to .bashrc)*

### How to use the SHT75 Temperature & Humidity Sensor
0. A Raspberry Pi is required for read-out.
1. Install the latest version of E4control also on the Pi. Default path is *~/software/* (otherwise see 3.)
2. Connect the SHT75 to the corresponding pins of the Pi. Check [SHT_Server](/e4control/devices/SHT_Server.py) for some information on the pin configuration.
3. Ensure the ssh connection by adjusting the __init__ function in [SHT75 class](e4control/devices/SHT75.py). This may include copying the ssh-key to the Pi in order to get rid of the necessity to manually type in the password, changing the default shell to bash and making StartServer.sh executable. Default username is *labuser*. If the path is differing from the default, it needs to adapted in [StartServer.sh](/e4control/devices/StartServer.sh), as well.

Running E4control directly on the Pi is possible. The config should read:
` T SHT75 lan localhost 50000 1`

## How to run scripts?
If -h or --help is supplied at the command line, the basic usage of the script will be explained, printing a short explanation of each argument.

#### config file
A config file with all used devices is needed for every script. For an example see [exampleConfig](/examples/exampleConfig).
In the first column the purpose of the respective device is written (S = source meter, L = LCR meter, T = temperature device, H = humidity device, C = cooling device). The other columns contain device name, connection type, host and port. The columns are separated by a single space.

A line is ignored if it has '#' as its first character.

#### e4control_measure_IV
To measure the current against voltage, enter:
`e4control_measure_IV V_min V_max output config -I I_lim -s V_steps -n ndaqs -d delay -noLivePlot -db database`

- V_min   -> starting voltage | float | in V
- V_max   -> end voltage | float | in V
- output  -> output directory name | string
- config  -> config file name | string
- I_lim   -> current limit | float | in uA
- V_steps -> number of voltage steps | int
- ndaqs   -> number of data acquistion at every set voltage | int
- delay   -> delay after setting new voltage | int | in s
- noLivePlot-> hide live plot | flag
- database-> enable pixel database output | flag

example:
`e4control_measure_IV 0 100 meas_1 config_IV -I 3 -s 11 -n 5 -d 2 `

#### e4control_measure_CV
To measure the capacitance against voltage, enter:
`e4control_measure_CV V_min V_max output config -s V_steps -n ndaqs -d delay -f lcr_frequency -p noLivePlot -db database`

- V_min   -> starting voltage | float | in V
- V_max   -> end voltage | float | in V
- output  -> output directory name | string
- config  -> config file name | string
- V_steps -> number of voltage steps | int
- ndaqs   -> number of data acquistion at every set voltage | int
- delay   -> delay after setting new voltage | int | in s
- lcr_frequency -> LCR meter frequency | float | in Hz
- lvolt   ->
- mode    ->
- integration->
- noLivePlot-> hide live plot | flag
- database-> enable pixel database output | flag

example:
`e4control_measure_CV 0 100 meas_2 config_CV -s 11 -n 5 -d 2 -f 10000`

#### e4control_measure_It
To measure the current against time at a fixed voltage, enter:
`e4control_measure_It output config -v voltage -n ndaqs -d delay -p noLivePlot -db database`

- voltage -> constant set voltage | float | in V
- output  -> output directory name | string
- config  -> config file name | string
- ndaqs   -> number of data acquistion at every measure point | int
- delay   -> delay between two measure points | int | in s
- noLivePlot-> hide live plot | flag
- database-> enable pixel database output | flag

*this measurement runs until ctrl+C is pressed*

example:
`e4control_measure_It meas_3 config_It -v 50 -n 5 -d 30 -p 1`

#### e4control_dcs and e4control_gui_dcs
To access the terminal interface enter:
`e4control_dcs config -l logfile `
or the quivalent for the gui-dcs:
`e4control_gui_dcs config -l logfile `

- config  -> config file name | string
- logfile -> logfile name | string

examples:
`e4control_dcs config_dcs -l log_1 ` *with log named log_1*  
`e4control_dcs config_dcs ` *without log*
`e4control_gui_dcs config -l log_2 ` *gui-dcs with log named log_2*
`e4control_gui_dcs config ` *gui-dcs without log*
