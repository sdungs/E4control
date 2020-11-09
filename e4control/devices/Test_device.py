# -*- coding: utf-8 -*-

import numpy as np
from numpy.random import normal
from .device import Device


class Test_device(Device):

	def __init__(self, connection_type, host, port):
		self.data_x = 0
		self.data_y = 0
		pass

	def initialize(self):
		pass


	def output(self):
		return [['x_data', 'y_data'], [normal(0, 10, 1)[0], normal(0, 10, 1)][0]]
