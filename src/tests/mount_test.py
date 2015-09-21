"""Unit tests for the mount module."""

import unittest

from mock import MagicMock, patch

import mount


class MountTest(unittest.TestCase):
	"""Unit tests for the Mount class."""

	@patch('mount.SwivelMount.center')
	def setUp(self, mock_center):
		self.mock_driver = MagicMock()
		self.m = mount.SwivelMount(driver=self.mock_driver)

	def test_init(self):
		attrs = {
			'driver': self.mock_driver,
			'mount_center': 0,
			'servo_center': 90,
			'max_right': 90,
			'max_left': 270,
			'clockwise_servo': False,
			'current_angle': 0
		}

		for k, v in attrs.items():
			self.assertEqual(getattr(self.m, k), v)

	def test_init_invalid_values(self):
		"""Verify that supplied angles are in range 0-359."""

		for attr in ['center', 'arc', 'servo_center']:
			with self.assertRaises(ValueError):
				m = mount.SwivelMount(**{attr: 375})

	def test_mount_angle_to_servo_angle(self):
		"""Verify mount angle is translated to the correct servo angle."""

		# Clockwise servos:
		self.m.clockwise_servo = True
		clockwise_test_cases = [
			(0, 90),
			(90, 180),
			(270, 0)
		]

		for case in clockwise_test_cases:
			self.assertEqual(
				self.m._mount_angle_to_servo_angle(case[0]),
				case[1]
		)

		# Counterclockwise servos:
		self.m.clockwise_servo = False
		counterclockwise_test_cases = [
			(0, 90),
			(90, 0),
			(270, 180)
		]

		for case in counterclockwise_test_cases:
			self.assertEqual(
				self.m._mount_angle_to_servo_angle(case[0]),
				case[1]
		)

	def test_swivel(self):
		"""Verify driver is called correctly to swivel the mount."""
		self.m.swivel(90)
		self.mock_driver.servo.assert_called_once_with(0)

	def test_swivel_invalid_angles(self):
		"""Verify exception thrown if invalid angle specified."""

		for angle in [-1, 360]:
			with self.assertRaises(ValueError):
				self.m.swivel(angle)

	@patch('mount.SwivelMount.swivel')
	def test_center(self, mock_swivel):
		self.m.center()
		mock_swivel.assert_called_once_with(0)
