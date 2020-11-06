# -*- coding: utf-8 -*-

"""
Class to remote controll a physical instrument (PI) controller, which can be used as a xyz-stage.
"""

import numpy as np
import sys
from .device import Device


class C804(Device):
	trm = '\r\t\n'
	x_position = None
	y_position = None
	z_position = None
	step = 0.034e-3


	def __init__(self, connection_type, host, port):
		super(C804, self).__init__(connection_type=connection_type, host=host, port=port)
		self.getAndSetParameter()
		print('Movement commands in mm.')


	def initialize(self):
		self.write('1FE1')
		self.write('2FE1')
		self.write('3FE1')
		self.getAndSetParameter()


	def getAndSetParameter(self):
		self.x_position = self.getX()
		self.y_position = self.getY()
		self.z_position = self.getZ()


	def setHome(self):
		self.write('DH')
		print('New home Established.')


	def goHome(self):
		self.write('GH')
		print('Going home.')


	def getX(self):
		xPos = self.ask('1TP')
		xPos = xPos.split('?')[0]
		xPos = xPos[3:-2]
		xPos = int(xPos)
		return float(xPos)


	def getY(self):
		yPos = self.ask('2TP')
		yPos = yPos.split('?')[0]
		yPos = yPos[3:-2]
		yPos = int(yPos)
		return float(yPos)


	def getZ(self):
		zPos = self.ask('3TP')
		zPos = zPos.split('?')[0]
		zPos = zPos[3:-2]
		zPos = int(zPos)
		return float(zPos)



#Relative movement in x, y and z


	def xRelMove(self, mm_x):
		nx = -np.round(mm_x / (self.step)).astype(int)
		self.write('1MR' + str(nx))
		pass


	def yRelMove(self, mm_y):
		ny = -np.round(mm_y / (self.step)).astype(int)
		self.write('2MR' + str(ny))
		pass


	def zRelMove(self, mm_z):
		nz = -np.round(mm_z*2 / self.step).astype(int)
		self.write('3MR'+str(nz))
		pass


	def output(self, show=True):
		try:
			self.printOutput('X-Y-Z-Stage')
			x = self.getX()
			y = self.getY()
			z = self.getZ()
			if show:
				self.printOutput(f'x-position:{x}\ny-position:{y}\nz-position:{z}')
			return [x, y, z]
		except :
			self.printOutput('Error!')
			sys.exit()
