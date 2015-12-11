"""Unit tests for the state module."""

import unittest

from mock import MagicMock

from state import BaseState, CorridorState


class BaseStateTests(unittest.TestCase):
	"""Unit tests for the BaseState class."""

	def setUp(self):
		self.mock_robot = MagicMock()
		self.state = BaseState(self.mock_robot)

	def test_init(self):
		self.assertEqual(self.state.robot, self.mock_robot)
		self.assertFalse(self.state.is_oriented)

	def test_run(self):
		"""Verify that BaseState can't be used to run the robot."""
		with self.assertRaises(NotImplementedError):
			self.state.run()


class CorridorStateTests(unittest.TestCase):
	"""Unit tests for the CorridorState class."""

	def setUp(self):
		self.mock_robot = MagicMock()
		self.state = CorridorState(self.mock_robot)

	def test_find_perpendicular(self):
		test_cases = [
			([6, 7, 8, 7, 6, 5, 4, 3, 4, 5], 7),  # Right, looking right
			([7, 6, 6, 6, 7, 8, 8, 7, 6, 5], 2),  # Right, looking left
			([4, 5, 6, 7, 8, 7, 6, 6, 6, 7], 7),  # Left, looking right
			([5, 4, 3, 3, 4, 5, 6, 6, 7, 6], 2),  # Left, looking left
			([8, 7, 6, 5, 4, 3, 3, 4, 5, 6], 5),  # Looking straight at a wall
			([3, 4, 5, 6, 7, 8, 8, 8, 7, 6], 9)   # Looking down the corridor
		]

		for test_case in test_cases:
			self.assertEqual(self.state._find_perpendicular(test_case[0]),
							 test_case[1])

	def test_find_p_heading(self):
		orig_find_perpendicular = self.state._find_perpendicular
		self.state._find_perpendicular = MagicMock()
		p_hist = [0.2, 0.6, 0.2]

		test_cases = [
			(0, [0] * 8 + p_hist + [0] * 25),   # Centered at 270
			(11, [0] * 19 + p_hist + [0] * 14)  # Centered at 020
		]

		for test_case in test_cases:
			self.state._find_perpendicular.return_value = test_case[0]
			self.assertEqual(self.state._find_p_heading(), test_case[1])

		self.state._find_perpendicular = orig_find_perpendicular

	def test_rotate_p_heading(self):
		p_histogram = [0.2, 0.6, 0.2]
		self.state.p_heading = [0] * 17 + p_histogram + [0] * 16
		test_cases = [
			(30, [0] * 14 + p_histogram + [0] * 19),
			(-30, [0] * 20 + p_histogram + [0] * 13)
		]

		for test_case in test_cases:
			self.assertEqual(
				self.state._rotate_p_heading(test_case[0]),
				test_case[1]
			)
