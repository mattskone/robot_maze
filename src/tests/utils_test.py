"""Unit tests for the utils module."""

import unittest

import utils


class UtilsTest(unittest.TestCase):

	def test_robot_angle_to_mount_angle(self):
		test_cases = [
			(0, 90),
			(90, 0),
			(100, 350),
			(225, 225),
			(315, 135)
		]

		for test_case in test_cases:
			self.assertEqual(
				utils.robot_angle_to_mount_angle(test_case[0]), test_case[1]
			)
