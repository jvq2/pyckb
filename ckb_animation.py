#!/usr/bin/env python
import sys
import math
import argparse
import traceback
import urllib



class CkbAnimation(object):
	def __init__(self):
		self.args = []
		self.keycount = 0
		self.key_pixel_map = {}
		self.max_x = 0
		self.max_y = 0
		self.enable_debug_log = False
		self.debug_log = '/tmp/ckb_anim_debug.log'

		self.name = "<name>"
		self.author = "<author>"
		self.version = "0.01"
		self.year = "2016"
		self.license = "GPLv2"
		self.guid = "{E0BBA19E-C328-4C0E-8E3C-A06D5722B4FB}"
		self.desc = "A generic animation plugin"
		self.params = []
		self.kpmode = "position"
		self.time = "duration"
		self.parammode = "live"
		self.preempt = "on"
		self.presets = []


	@staticmethod
	def encode(s):
		""" Url Encode """
		# ckb uses its own non standard url encoding function that misses some
		# characters. Lets try to match that.
		return urllib.quote(s, '{}=')

	@staticmethod
	def decode(s):
		""" Url Decode """
		return urllib.unquote(s).decode('utf8')


	def debug(self, *args, **kwargs):
		""" If debuging is enabled, will print arg 1 to the log formatted with
			everything that follows. A new line is appended to the end of the
			message.

			self.debug("stuff")
			self.debug("stuff: {}", "other")
			self.debug("stuff: {} {x}", "yup", x="other")
		"""
		if not self.enable_debug_log:
			return

		# Format the first arg with all the rest
		msg = str(args[0]).format(*args[1:], **kwargs)

		# Write it to the log file
		with open(self.debug_log, 'a') as f:
			f.write('%s\n' % (msg,))


	@staticmethod
	def parse_args(args):
		""" Handles cli argument parsing """
		parser = argparse.ArgumentParser()
		parser.add_argument("--ckb-info", action="store_true")
		parser.add_argument("--ckb-run", action="store_true")
		return parser.parse_args()


	def info(self):
		""" Generates program information for digestion by the ckb interface """
		self.send_cmd('name', self.name)
		self.send_cmd('author', self.author)
		self.send_cmd('version', self.version)
		self.send_cmd('year', self.year)
		self.send_cmd('license', self.license)
		self.send_cmd('guid', self.guid)
		self.send_cmd('description', self.desc)

		for param in self.params:
			self.send_cmd('param', *param)

		self.send_cmd('kpmode', self.kpmode)
		self.send_cmd('time', self.time)
		self.send_cmd('parammode', self.parammode)
		self.send_cmd('preempt', self.preempt)

		for preset in self.presets:
			self.send_cmd('preset', *preset)


	def cli(self, args):
		""" Command line interface """
		try:
			self.debug('\n=================================================================')
			self.debug(args)
			self.args = self.parse_args(args)
			if self.args.ckb_info:
				self.info()
				return 0

			if self.args.ckb_run:
				return self.ckb_run()

			print 'This program is designed to run inside of CKB'
			return 1
		except:
			self.debug(traceback.format_exc())


	def ckb_run(self):
		""" Initial handshake that reads configs/etc.
			To be started when given --ckb-run
		"""
		ret_val = 0
		cont = True

		while cont:
			cmd, param, value = self.read_cmd()

			if [cmd, param] == ['begin', 'keymap']:
				cont = self.cmd_begin_keymap()

			elif [cmd, param] == ['begin', 'params']:
				cont = self.cmd_begin_params()

			elif [cmd, param] == ['begin', 'run']:
				ret_val = self.cmd_run()
				# end execution
				cont = False

			else:
				cont = self.cmd_unknown(cmd, param, value)

		return ret_val


	def cmd_run(self):
		""" Main anim loop. Runs when cmd `begin run` is given """
		ret_val = 0
		cont = True
		self.send_cmd('begin', 'run')

		while cont:
			cmd, param, value = self.read_cmd()

			if [cmd, param] == ['end', 'run']:
				cont = False

			elif cmd == 'start':
				self.start()

			elif cmd == 'stop':
				self.stop()

			elif cmd == 'time':
				self.tick(param)

			elif cmd == 'frame':
				cont = self.cmd_frame()

			elif [cmd, param] == ['begin', 'params']:
				cont = self.cmd_begin_params()

			elif cmd == 'key':
				cont = self.cmd_key(param, value)

			else:
				cont = self.cmd_unknown(cmd, param, value)

		self.send_cmd('end', 'run')
		return ret_val


	def read_cmd(self):
		""" Reads and returns a list consisting of a command, param, and value
			from stdin
		"""
		line = sys.stdin.readline()
		if line == "":
			self.debug("EOF")
			return "EOF", None, None

		cmd_line = line.strip("\n").split(None, 2)
		cmd_line = [self.decode(c) for c in cmd_line]
		cmd_line += [None] * (3 - len(cmd_line))
		self.debug('in: %s'%str(cmd_line))
		return cmd_line


	def send_cmd(self, *cmd_parts):
		out = ' '.join([self.encode(part) for part in cmd_parts])
		print out
		# print '%s %s %s' % (cmd, self.encode(param), self.encode(value))
		self.debug('out: {}', str(out))
		sys.stdout.flush()


	def cmd_unknown(self, cmd, param, value):
		""" Unknown command was given. Should return True to continue
			execution. False to stop.
		"""
		self.debug('Unknown command: %s' % ([cmd, param, value],))
		return True


	def cmd_begin_keymap(self):
		""" Reads keycount and key to pixel map from the main interface """
		cmd, param, value = self.read_cmd()

		assert cmd == 'keycount', "Keymap not followed by keycount"

		self.keycount = int(param)
		self.key_pixel_map = {}
		cmd, param, value = self.read_cmd()

		# Build the key to pixel map
		while cmd == 'key':
			x, y = [int(x) for x in value.split(',')]
			self.max_x = max(self.max_x, x)
			self.max_y = max(self.max_y, y)
			self.key_pixel_map[param] = [x, y]
			cmd, param, value = self.read_cmd()

		assert [cmd, param] == ['end', 'keymap'], "Unknown command/param following keymap"
		return True


	def cmd_begin_params(self):
		cmd, param, value = self.read_cmd()

		while cmd == 'param':
			self.parse_param(param, value)
			cmd, param, value = self.read_cmd()

		assert [cmd, param] == ['end', 'params']
		return True


	def cmd_key(self, param, value):
		""" Translates the x,y given to a specific key name.
			param is a string of "x,y"
			value is a key state string: "up" or "down"
		"""
		x, y = [int(p) for p in param.split(',')]
		key = self.get_closest_key(x, y)
		state = value or "up"
		self.keypress(key, x, y, state)
		return True


	def get_closest_key(self, x, y):
		""" Returns the key name of the closest key to x, y """
		closest_key = None
		closest_distance = 999999
		for key, key_pos in self.key_pixel_map.items():
			# If we are spot on, just return the key
			if key_pos == [x, y]:
				return key

			# Othewise calculate the distance
			distance = math.hypot(key_pos[0] - x, key_pos[1] - y)

			if distance < closest_distance:
				closest_key = key

		return closest_key


	def send_key_color(self, key, r, g, b, a=255):
		""" Given a key, color, and alpha sends the argb command """
		argb = "{a:02x}{r:02x}{g:02x}{b:02x}".format(a=a, r=r, g=g, b=b)
		self.send_cmd('argb', key, argb)


	def cmd_frame(self):
		""" Frame wrapper used to translate and output the return of frame() """
		# self.debug('begin frame')
		self.send_cmd('begin', 'frame')
		# print 'begin frame'
		cont = self.frame()
		# self.debug('end frame')
		self.send_cmd('end', 'frame')
		# print 'end frame'
		return cont


	def tick(self, delta):
		""" A time update event """
		pass

	def parse_param(self, param, value):
		""" Animation parameter has changed """
		pass

	def start(self):
		""" Called when a single animation event at the center of the keyboard
			is requested. Often called at animation startup
		"""
		pass

	def stop(self):
		""" Called to stop the animation initialized by start """
		pass

	def frame(self):
		""" Called when a frame is requested. Returns True to continue execution. """
		return True

	def keypress(self, key, x, y, state):
		""" Called when a key state has changed """
		pass

