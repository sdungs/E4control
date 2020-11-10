# -*- coding: utf-8 -*-

import numpy as np
from numpy.random import normal
from .device import Device


class Test_device(Device):

	def __init__(self, connection_type, host, port):
		self.data_x = 0
		self.data_y = 0
		self.output_status = '1'
		pass

	def initialize(self):
		pass

	def get_data(self):
		return normal(0, 10, 1)[0]


	def output(self):
		self.x_data = self.get_data()
		self.y_data = self.get_data()
		self.printOutput('Test_device')
		self.printOutput(f'x_data: {self.x_data}')
		self.printOutput(f'y_data: {self.y_data}')
		return [['x_data', 'y_data'], [self.x_data, self.y_data]]

	def getOutput(self):
		return self.output_status

	def setOutput(self, value):
		if value:
			self.output_status = '1'
		else:
			self.output_status = '0'
		pass


	def rampVoltage(self, voltage):
		pass

	def close(self):
		pass

	def interaction(self, gui=False):
		if gui == True:
			device_dict = {
			'pass': True,
			'channel': 4,
			'toogleOutput': True
			}
			return device_dict
		pass
