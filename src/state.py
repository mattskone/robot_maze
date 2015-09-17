"""Implementations of the possible states for a robot."""

class BaseState(object):

	def __init__(self, robot):
		self.robot = robot

	def run(self, callback, *args, **kwargs):
		raise NotImplementedError()
