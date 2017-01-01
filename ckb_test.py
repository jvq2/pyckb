#!/usr/bin/env python
from ckb_animation import CkbAnimation
import sys
import math
import time

class TestAnim(CkbAnimation):
	def __init__(self):
		super(TestAnim, self).__init__()
		self.enable_debug_log = True
		# self.debug_log = '/tmp/btest'

		self.name = "Test Anim"
		self.author = "Joey"
		self.version = "0.01"
		self.year = "2016"
		self.license = "GPLv2"
		self.guid = "{E0BBA19E-C328-4C0E-8E3C-A06D5722B4FB}"
		self.desc = "A generic animation plugin"
		self.params = [
			["angle", "angle", "Angle:", "90"],
			["agradient", "color", "Wave color:", "ffffffff"],
			["double", "length", "Wave length:", "%25", "100.000000", "1.000000", "100.000000"],
			["bool", "symmetric", "Symmetric", "0"]
			]
		self.presets = [
			["Shimmer", "duration=2.0", "length=50.0", "symmetric=1"],
			["Rainbow", "color=0:ffff0000 17:ffffff00 33:ff00ff00 50:ff00ffff 67:ff0000ff 83:ffff00ff 100:ffff0000", "duration=2.0"],
			["Vertical rainbow", "color=0:ffff0000 17:ffffff00 33:ff00ff00 50:ff00ffff 67:ff0000ff 83:ffff00ff 100:ffff0000", "duration=2.0", "angle=180"]
			]


	def parse_param(self, param, value):
		pass


	def start(self):
		pass


	def stop(self):
		pass


	def tick(self, delta):
		pass


	def keypress(self, key, x, y, state):
		self.debug("{} {} {} {}", key, x, y, state)
		pass


	def frame(self):
		import random, time
		x = int(abs(math.sin(time.time()))*255)
		y = int(abs(math.sin(time.time()/2))*255)
		for key in self.key_pixel_map:
			# self.send_key_color(key, 255, 0, 255)
			# self.send_key_color(key, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

			self.send_key_color(key, x, 0, x)
		return True




if __name__ == '__main__':
	anim = TestAnim()
	sys.exit(anim.cli(sys.argv))

