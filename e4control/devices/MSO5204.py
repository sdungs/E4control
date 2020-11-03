# -*- coding: utf-8 -*-
'''
Class to remote a Tektroik MSO 5204B Mixed Signal Oscilloscope via Ethernet.
The Script communicates with the instrument using the pyvisa libary.
'''

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from pint import UnitRegistry
import pyvisa

u = UnitRegistry()
Q_ = u.Quantity

class MSO5204:


	def __init__(self, ip):
		#  get incontact with the scope via pyvisa. '@py' instructs to use the pyvisa-py backend.
		rm = pyvisa.ResourceManager('@py')
		self.instrument = rm.open_resource("TCPIP0::" + ip + "::inst0::INSTR")

		#  initialize scope variables
		self.setParameter()
		self.printParameters()
		self.getStatus()
		pass


	#  function to convert the returned strings from the scope in a more handy form
	def strConverter(self, string):
		while '\"' in string:
			string = string.replace('\"', '')
		string = string.replace('\n', '')
		if string.isnumeric():
			return int(string)
		try:
			return float(string)
		except:
			return string


	#  set Parameters to current values; called by the initialize function
	def setParameter(self):
		self.timescale = self.getTime()
		self.voltscale = self.getVoltagescale()
		self.channel = self.getChannel()
		self.trigger = self.getTriggerSource()
		self.triggerlev = self.getTriggerLevel()
		self.triggermod = self.getTriggerMode()
		self.average = self.getModeAverage()
		self.samplerate = self.getSamplerate()
		self.recordlength = self.getRecordlength()
		pass


	#  displays all parameters of the scope
	def printParameters(self):
		print(f'Settings of the Oscilloscope:\n\nChannel:\n{self.channel}\nTime: {self.timescale}\nVoltage Scale: {self.voltscale}\nTrigger Source: {self.trigger}\nTrigger Level: {self.triggerlev}\nTrigger Mode: {self.triggermod}\nMode Average: {self.average}\nSamplerate: {self.samplerate}')
		pass


	#  function to check if the scope is currently busy and to check the acquisition state
	def getStatus(self):
		running_state = self.strConverter(self.instrument.query('ACQ:STATE?'))
		if running_state:
			print('Acquisition state is ON.')
		else:
			print('Acquisition state is OFF.')

		status = int(self.strConverter(self.instrument.query('BUSY?')))
		if status:
			print('Scope is currently busy.')
		else:
			print('Scope is currently not busy. Measurement can be performed.\n')
		pass


	#  returns voltagescale for the current measurement
	def getVoltagescale(self):
		yunit = self.strConverter(self.instrument.query('WFMO:YUNIT?'))
		ymult = self.strConverter(self.instrument.query('WFMO:YMULT?'))
		return Q_(ymult, yunit)


	#  get the horizontal scale which is equal to the time
	def getTime(self):
		unit = self.strConverter(self.instrument.query('HOR:MAIN:UNIT?'))
		time = self.strConverter(self.instrument.query('HOR:MODE:SCA?'))
		return Q_(time, unit)


	#  set the horizontal scale to a given value
	def setTime(self, time):
		time = time.to('s').magnitude
		self.instrument.write(f'HOR:MODE:SCA {time}')
		self.timescale = self.getTime()
		print(f'Timescale set to {self.timescale}.')
		pass


	#  returns current trigger source
	def getTriggerSource(self):
		trigger_source = self.strConverter(self.instrument.query('TRIG:A:EDGE:SOURCE?'))
		return trigger_source


	#  sets trigger to a given source
	def setTriggerSource(self, source):
		source = str(source)
		if source.isnumeric():
			self.instrument.write(f'TRIG:A:EDGE:SOURCE CH{source}')
		else:
			self.instrument.write(f'TRIG:A:EDGE:SOURCE {source}')
		self.trigger = self.getTriggerSource()
		print(f'{self.trigger} is the Trigger Source.')
		pass


	#  returns the current trigger level
	def getTriggerLevel(self):
		trigger_level = self.strConverter(self.instrument.query('TRIG:A:LEVEL?'))
		return Q_(trigger_level, 'V')


	#  Set the Trigger level on an CH or the AUX inout to a given level. Sources except CH and AUX can not be handled
	def setTriggerlev(self, level, channel=None):
		level = level.to('V').magnitude
		if channel is not None:
			channel = str(channel)
			self.instrument.write(f'TRIG:A:LEVEL:CH{channel} {level}')
		else:
			try:
				self.instrument.write(f'TRIG:A:LEVEL:AUX {level}')
			except:
				print('Choose a Trigger level for the AUX source.')
		self.triggerlev = self.getTriggerLevel()
		print(f'The trigger level of {self.trigger} is {self.triggerlev}.')
		pass


	# returns trigger mode
	def getTriggerMode(self):
		triggermod = self.strConverter(self.instrument.query('TRIG:A:MODE?'))
		return triggermod


	# Sets the Trigger Mode. Póssible modes: "AUTO" or "NORMAL"
	def setTriggerMode(self, mode):
		self.instrument.write(f'TRIG:A:MODE {mode}')
		self.triggermod = self.getTriggerMode()
		print(f'Trigger mode set to {self.triggermod}.')
		pass


	#  returns the mode average
	def getModeAverage(self):
		mode = self.instrument.query('ACQ:MODE?')
		if 'AVE' in mode:
			ave = self.instrument.query('ACQ:NUMAV?')
		else:
			self.instrument.write('ACQ:MODE AVE')
			ave = self.strConverter(self.instrument.query('ACQ:NUMAV?'))
		return ave


	#  sets the mode average to a given value
	def setModeAverage(self, pow):
		modeAverage = 2**pow
		self.instrument.write('ACQ:Mode AVE')
		self.instrument.write(f'ACQ:NUMAV {modeAverage}')
		print(f'Number of acquisitions for an averaged waveform was set to {modeAverage}.')
		self.modeAverage = self.getModeAverage()
		pass


	#  sets the Aquisition mode to sample
	def setSampleMode(self):
		self.instrument.write('ACQ:Mode SAM')
		pass


	def getSamplerate(self):
		self.samplerate = self.strConverter(self.instrument.query('HOR:MODE:SAMPLER?'))
		return self.samplerate


	def setSamplerate(self, samplerate):
		self.instrument.write(f'HOR:MODE:SAMPLER {samplerate}')
		self.samplerate = self.getSamplerate()
		print(f'Samplerate set to {self.samplerate}')
		pass


	#  queries the acquisition number
	def getAcqNumber(self):
		acq_number = self.strConverter(self.instrument.query(f'ACQuire:NUMACq?'))
		return acq_number


	def getRecordlength(self):
		self.recordlength = self.strConverter(self.instrument.query('HOR:MODE:RECO?'))
		return self.recordlength


	def setRecordlength(self, recordlength):
		self.instrument.write(f'HOR:MODE:RECO {recordlength}')
		self.recordlength = self.getRecordlength()
		print(f'Recordlength set to {self.recordlength}')
		pass


	#  returns channel information for all channels
	def getChannel(self):
		voltScale = []
		for i in range(4):
			voltScale.append(self.strConverter(self.instrument.query(f'CH{i + 1}:SCA?')))
		voltScale = Q_(voltScale, 'V')

		chan = []
		for i in range(len(voltScale)):
			chan.append(f'CH{i + 1}: Voltagescale {voltScale[i]}')
		return chan


	#  set measurements to Amplitude, Risetime, Falltime and Period
	def setMeasurements(self):
		self.instrument.write('MEASU:MEAS1:AMP')
		self.instrument.write('MEASU:MEAS2:RIS')
		self.instrument.write('MEASU:MEAS3:FALL')
		self.instrument.write('MEASU:MEAS4:PERI')


	def getAmplitude(self):
		counts = self.strConverter(self.instrument.query('MEASU:MEAS1:COUNT?'))
		unit = self.strConverter(self.instrument.query('MEASU:MEAS1:UNIT?'))
		ampl_mean = self.strConverter(self.instrument.query('MEASU:MEAS1:MEAN?'))
		ampl_std = self.strConverter(self.instrument.query('MEASU:MEAS1:STD?'))
		return Q_([ampl_mean, ampl_std], unit), counts


	def getRiseTime(self):
		counts = self.strConverter(self.instrument.query('MEASU:MEAS2:COUNT?'))
		unit = self.strConverter(self.instrument.query('MEASU:MEAS2:UNIT?'))
		riseT_mean = self.strConverter(self.instrument.query('MEASU:MEAS2:MEAN?'))
		riseT_std = self.strConverter(self.instrument.query('MEASU:MEAS2:STD?'))
		return Q_([riseT_mean, riseT_std], unit), counts


	def getDecrTime(self):
		counts = self.strConverter(self.instrument.query('MEASU:MEAS3:COUNT?'))
		unit = self.strConverter(self.instrument.query('MEASU:MEAS3:UNIT?'))
		decrT_mean = self.strConverter(self.instrument.query('MEASU:MEAS3:MEAN?'))
		decrT_std = self.strConverter(self.instrument.query('MEASU:MEAS3:STD?'))
		return Q_([decrT_mean, decrT_std], unit), counts


	def getPeriod(self):
		counts = self.strConverter(self.instrument.query('MEASU:MEAS4:COUNT?'))
		unit = self.strConverter(self.instrument.query('MEASU:MEAS4:UNIT?'))
		period_mean = self.strConverter(self.instrument.query('MEASU:MEAS4:MEAN?'))
		period_std = self.strConverter(self.instrument.query('MEASU:MEAS4:STD?'))
		return Q_([period_mean, period_std], unit), counts


	#  returns the data recorded by the scope
	def getWaveform(self, channel, start, stop):
		try:
			source = self.strConverter(self.instrument.query('DATA:SOURCE?'))
			print(f'Data source is {source}.')
			if source is not f'CH{channel}':
				print('Channel will be redirected to the given channel.')
				self.instrument.write(f'DATA:SOURCE CH{channel}')
				source = self.strConverter(self.instrument.query('DATA:SOURCE?'))
				print(f'New Source is {source}.')

			'''
			see programmers manual page 110 for further information about data handling with the scope.
			'''
			self.instrument.write('DATA:ENC SRP') #  SRPbinary see programmers manual page 276
			self.instrument.write('WFMO:BYT_N 2') #  see scope programmers manual page 1189, valid byte numbers are 8, 16, 32, 64
			self.instrument.write(f'DATA:START {start}')

			record = self.recordlength
			if record < stop:
				print(f'Stop value is bigger than recordlength.\nThe new stop value will be the recordlength {record}.')
				stop = record

			self.instrument.write(f'DATA:STOP {stop}')

			ymult = self.strConverter(self.instrument.query('WFMO:YMULT?'))
			yzero = self.strConverter(self.instrument.query('WFMO:YZERO?'))
			yoff = self.strConverter(self.instrument.query('WFMO:YOFF?'))
			yunit = self.strConverter(self.instrument.query('WFMO:YUNIT?'))
			xincr = self.strConverter(self.instrument.query('WFMO:XINCR?'))
			xzero = self.strConverter(self.instrument.query('WFMO:XZERO?'))
			xunit = self.strConverter(self.instrument.query('WFMO:XUNIT?'))

			data = self.instrument.query_binary_values('CURVE?', container=np.array, datatype='H')

			ydata = (data - yoff) * ymult + yzero
			xdata = np.linspace(xzero, xincr * len(ydata), len(ydata))
			Y = Q_(ydata, yunit)
			X = Q_(xdata, xunit)
			print('Data successfully collected.')
			return [X, Y]

		except:
			e = sys.exc_info()[0]
			print(f'\nAn Error occured: {e}')


	#  sets acquisition state to ON
	def RunStart(self):
		self.instrument.write('ACQ:STATE RUN')
		print('Acquisition state is ON.')
		pass


	#  sets acquisition state to OFF
	def RunStop(self):
		self.instrument.write('ACQ:STATE STOP')
		print('Acquisition state is OFF.')
		pass

	#  function to save the data as a txt file
	def savetotxt(self, file_name, xdata, ydata, folder='', supress_file_check=False):
		#  Check if the folder already exists
		if folder is not '' and not os.path.exists(folder):
			os.makedirs(folder)

		xdata, xunit = xdata.magnitude, xdata.units
		ydata, yunit = ydata.magnitude, ydata.units

		#  check if file already exists
		if supress_file_check:
			np.savetxt(os.path.join(folder, file_name + '.txt'), np.column_stack([xdata, ydata]), header=f'time[{xunit}] voltage[{yunit}]')
			print('Data successfully saved as txt.')
		else:
			if os.path.exists(os.path.join(folder, file_name + '.txt')):
				x = input(f'Textfile {file_name}.txt already exist. Overwrite? (y/n):  ')
				yes = ['Yes', 'yes', 'Y', 'y', 'Ja', 'ja', 'J', 'j']
			else:
				x = None
			if x == None or x in yes:
				np.savetxt(os.path.join(folder, file_name + '.txt'), np.column_stack([xdata, ydata]), header=f'time[{xunit}] voltage[{yunit}]')
				print('Data successfully saved as txt.')
			else:
				print('Nothing to do.')
		pass


	#  function save the data as a pdf, only usable for single channel measurements
	def savetopdf(self, file_name, xdata, ydata, folder=''):
		#  Check if the folder already exists
		if folder is not '' and not os.path.exists(folder):
			os.makedirs(folder)

		xdata = xdata.to('µs').magnitude
		ydata = ydata.to('mV').magnitude

		#  check if file already exists
		if os.path.exists(os.path.join(folder, file_name + '.pdf')):
			x = input(f'Plot {file_name}.pdf already exist. Overwrite? (y/n):  ')
			yes = ['Yes', 'yes', 'Y', 'y', 'Ja', 'ja', 'J', 'j']
		else:
			x = None
		if x == None or x in yes:
			plt.clf()
			plt.plot(xdata, ydata, '.--', label=f'{file_name}')
			plt.xlabel(f'Time / µs')
			plt.ylabel(f'Voltage / mV')
			plt.grid()
			plt.legend()
			plt.tight_layout()
			plt.savefig(os.path.join(folder, file_name + '.pdf'))
			print('Data successfully plotted.')
		else:
			print('Nothing to do.')
		pass
