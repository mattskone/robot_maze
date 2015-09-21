"""Unit tests for the sensor module."""

import unittest

from mock import call, MagicMock, patch

import sensor

SENSOR_PIN = 0


class UltrasonicSensorTest(unittest.TestCase):
	"""Unit tests for the UltrasonicSensor class."""

	def setUp(self):
		self.driver = MagicMock()
		self.mount = MagicMock()
		self.s = sensor.UltrasonicSensor(driver=self.driver,
										 mount=self.mount,
										 pin=SENSOR_PIN)

	def test_init(self):
		self.assertEqual(self.s.driver, self.driver)
		self.assertEqual(self.s.mount, self.mount)
		self.assertEqual(self.s.pin, SENSOR_PIN)

	def test_sense_distance(self):
		"""Verify actions to take a distance measurement."""

		measurements = [29, 29, 28]
		self.driver.us_dist.side_effect = lambda x: measurements.pop()

		self.assertEqual(self.s.sense_distance(60), 29)
		self.mount.swivel.assert_called_once_with(60)

	@patch('sensor.UltrasonicSensor.sense_distance')
	def test_sense_swath(self, mock_sense_distance):
		measurements = [101, 100, 102]
		mock_sense_distance.side_effect = lambda x: measurements.pop()

		self.assertEqual(self.s.sense_swath(45), 100)
		expected_calls = [call(30), call(45), call(60)]
		self.assertEqual(mock_sense_distance.call_args_list,
						 expected_calls)
