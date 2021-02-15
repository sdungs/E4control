# -*- coding: utf-8 -*-

"""
Class to remote controll a physical instrument (PI) controller, which can be used as a xyz-stage.
"""

import numpy as np
import sys
from .device import Device


class C804(Device):

	def __init__(self, connection_type, host, port):
		super(C804, self).__init__(connection_type=connection_type, host=host, port=port)
		self.getAndSetParameter()
		self.trm = '\r\t\n'
		self.x_position = None
		self.y_position = None
		self.z_position = None
		self.step = 0.034e-3
		print('Movement commands in mm.')


	def initialize(self):
		"""
		Initialize the device to standard values.
		"""
		self.write('1FE1')
		self.write('2FE1')
		self.write('3FE1')
		self.getAndSetParameter()


	def getAndSetParameter(self):
		"""
		Set the devices coordinates to the current coordinates.
		"""
		self.x_position = self.getX()
		self.y_position = self.getY()
		self.z_position = self.getZ()


	def setHome(self):
		"""
		Flag the current position as home.
		"""
		self.write('DH')
		print('New home Established.')


	def goHome(self):
		"""
		Go to the flagged home position.
		"""
		self.write('GH')
		print('Going home.')


	def getX(self):
		"""
		Get the current x coordinate.

		Returns
		-------
		xPos : float
		    Positon of the x coordinate.
		"""
		xPos = self.ask('1TP')
		xPos = xPos.split('?')[0]
		xPos = xPos[3:-2]
		xPos = int(xPos)
		return float(xPos)


	def getY(self):
		"""
		Get the current y coordinate.

		Returns
		-------
		yPos : float
		    Positon of the y coordinate.
		"""
		yPos = self.ask('2TP')
		yPos = yPos.split('?')[0]
		yPos = yPos[3:-2]
		yPos = int(yPos)
		return float(yPos)


	def getZ(self):
		"""
		Get the current z coordinate.

		Returns
		-------
		zPos : float
		    Positon of the z coordinate.
		"""
		zPos = self.ask('3TP')
		zPos = zPos.split('?')[0]
		zPos = zPos[3:-2]
		zPos = int(zPos)
		return float(zPos)



#Relative movement in x, y and z


	def xRelMove(self, mm_x):
		"""
		Move the PI-stage in x direction for a given value.

		Parameters
		-------
		mm_x : float
		    Value in mm.
		"""
		nx = -np.round(mm_x / (self.step)).astype(int)
		self.write('1MR' + str(nx))


	def yRelMove(self, mm_y):
		"""
		Move the PI-stage in y direction for a given value.

		Parameters
		-------
		mm_y : float
		    Value in mm.
		"""
		ny = -np.round(mm_y / (self.step)).astype(int)
		self.write('2MR' + str(ny))


	def zRelMove(self, mm_z):
		"""
		Move the PI-stage in z direction for a given value.

		Parameters
		-------
		mm_z : float
		    Value in mm.
		"""
		nz = -np.round(mm_z*2 / self.step).astype(int)
		self.write('3MR'+str(nz))


	def output(self, show=True):
		"""
		Get the current coordinates of the PI-stage.

		Parameters
		-------
		show : bool, optional
            Parameter to configure if the output is printed.
		"""
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

	def interaction(self, gui=False):
		"""
		Trigger an interaction with the device.
		This function is used by the dcs and the gui_dcs script.

		Parameters
		----------
		gui : bool
		    Parameter to turn on the gui function.
		    Only used for the gui_dcs script.
		"""
		if gui:
			device_dict = {
				'move': True,
				'setHome': True,
				'goHome': True,
			}
		else:
			print(
				'Select a channel!'
			)
			iChannel = input('Possible inputs: 1 or 2\n')
			while not iChannel in ['1', '2']:
				iChannel = input('Possible Inputs: 1 or 2! \n')
			print(f'Channel {iChannel} choosen.')
			print(
				'0: Continue dcs mode without any changes\n'
				'1: Move in x-direction\n'
				'2: Move in y-direction\n'
				'3: Move in z-direction'
			)

			x = input('Number? \n')
			while not (x in ['0', '1', '2', '3', ]):
				x = input('Possible Inputs: 0, 1, 2 or 3! \n')

			if x == '0':
				pass
			elif x == '1':
				x_move = input('Type in x-movement in mm.')
				self.xRelMove(x_move)
			elif x == '2':
				y_move = input('Type in y-movement in mm.')
				self.xRelMove(y_move)
			elif x == '3':
				z_move = input('Type in z-movement in mm.')
				self.xRelMove(z_move)
