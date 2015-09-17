"""Unit tests for the state module."""

import unittest

from mock import MagicMock

from state import BaseState


class BaseStateTests(unittest.TestCase):
	"""Unit tests for the BaseState class."""

	def setUp(self):
		self.mock_robot = MagicMock()
		self.state = BaseState(self.mock_robot)
		self.mock_callback = MagicMock()

	def test_init(self):
		self.assertEqual(self.state.robot, self.mock_robot)

	def test_run(self):
		"""Verify that BaseState can't be used to run the robot."""
		with self.assertRaises(NotImplementedError):
			self.state.run(self.mock_callback)
