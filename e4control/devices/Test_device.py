# -*- coding: utf-8 -*-

import numpy as np
from numpy.random import normal
from .device import Device


class Test_device(Device):

	def __init__(self, connection_type, host, port):
		self.data_x = 0
		self.data_y = 0
		self.output_status = '0'
		self.voltage = 0
		self.current = 0
		self.current_limit = 1
		self.Power = False
		self.setTemp = -20
		self.InTemp = 21
		self.sMode = 'int'
		self.status = 'status'
		self.voltage_limit = 100
		self.sHumidity = 40
		self.Humidity = 20
		self.rampSpeed = 5
		self. polarity = 'n'
		pass

	def initialize(self):
		pass

	def detData(self):
		return normal(0, 0.1, 1)[0]


	def output(self, show=False):
		self.x_data = self.detData()
		self.y_data = self.detData()
		self.Power = self.getPowerStatus()
		self.printOutput('Test_device')
		self.printOutput(f'Power: {self.Power}')
		self.printOutput(f'x_data: {self.x_data}')
		self.printOutput(f'y_data: {self.y_data}')
		return [['Power', 'x_data[C]', 'y_data[µA]'], [str(self.Power) ,self.x_data, self.y_data]]

	def getOutput(self, iChannel=-1):
		return self.output_status

	def setOutput(self, value, iChannel=-1):
		if value:
			self.output_status = '1'
		else:
			self.output_status = '0'
		pass

	def getPolarity(self, iChannel=-1):
		return self.polarity

	def setPolarity(self, new_polarity, iChannel=-1):
		self.polarity = new_polarity
		pass

	def getVoltage(self, iChannel=-1):
		return self.voltage

	def rampVoltage(self, new_voltage, iChannel=-1):
		self.voltage = new_voltage
		pass

	def setVoltage(self, new_voltage, iChannel=-1):
		self.voltage = new_voltage
		pass

	def getRampSpeed(self, iChannel=-1):
		return self.rampSpeed

	def setRampSpeed(self, new_rampSpeed, iChannel=-1):
		self.rampSpeed = new_rampSpeed
		pass

	def getCurrent(self, iChannel=-1):
		return self.current

	def setCurrent(self, new_current, iChannel=-1):
		self.current = new_current
		pass

	def getCurrentLimit(self, iChannel=-1):
		return self.current_limit

	def setCurrentLimit(self, new_current_limit, iChannel=-1):
		self.current_limit = new_current_limit
		pass

	def getVoltageLimit(self, iChannel=-1):
		return self.voltage_limit

	def setVoltageLimit(self, new_voltage_limit, iChannel=-1):
		self.voltage_limit = new_voltage_limit
		pass

	def getPowerStatus(self, iChannel=-1):
		return self.Power

	def enablePower(self, sBool, iChannel=-1):
		self.Power = sBool
		pass

	def getSetTemperature(self, iChannel=-1):
		return float(self.setTemp)

	def getInTemperature(self, iChannel=-1):
		return float(self.InTemp)

	def setTemperature(self, Tset, iChannel=-1):
		self.setTemp = Tset
		pass

	def getTemperature(self, iChannel=-1):
		return float(self.setTemp)

	def getHumidity(self, iChannel=-1):
		return float(self.Humidity)

	def getSetHumidity(self, iChannel=-1):
		return float(self.sHumidity)

	def setHumidity(self, value, iChannel=-1):
		self.sHumidity = value
		pass

	def setOperationMode(self, sMode, iChannel=-1):
		if (sMode == 'int'):
			self.sMode = 'int'
		elif (sMode == 'ext'):
			self.sMode = 'ext'
		elif (sMode == 'climate'):
			self.sMode = 'climate'
		elif (sMode == 'normal'):
			self.sMode = 'normal'
		pass

	def getOperationMode(self, iChannel=-1):
		if self.sMode == 'int':
			return 'int'
		elif (self.sMode == 'ext'):
			return 'ext'
		elif (self.sMode == 'climate'):
			return 'climate'
		elif (self.sMode == 'normal'):
			return 'normal'

	def getStatus(self, iChannel=-1):
		return self.status

	def enableOCP(self, bool, iChannel=-1):
		pass

	def reset(self):
		self.voltage = 0
		self.current = 0
		self.Power = False
		self.output_status = False
		pass

	def close(self):
		pass

	def interaction(self, gui=False):
		if gui:
			device_dict = {
			'pass': True,
			'channel': 4,
			'toogleOutput': True,
			'rampVoltage': True,
			'setVoltage': True,
			'setCurrent': True,
			'setCurrentLimit': True,
			'getSetTemperature': True,
			'setTemperature': True,
			'setHumidity': True,
			'enablePower': True,
			'setMode': True,
			'setOperationMode': True,
			'getStatus': True,
			'setOVP': True,
			'enableOCP': True,
			'setRampSpeed': True,
			'rampDeviceDown': True,
			'tooglePolarity': True,
			}
			return device_dict
		pass
