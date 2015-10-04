"""Unit tests for the sensor module."""

import unittest

from mock import call, MagicMock, patch

import sensor

SENSOR_PIN = 0


class BaseSensorTest(unittest.TestCase):
	"""Unit tests for the BaseSensor class."""

	def setUp(self):
		self.driver = MagicMock()
		self.mount = MagicMock()
		self.s = sensor.BaseSensor(driver=self.driver,
								   mount=self.mount,
								   pin=SENSOR_PIN)

	def test_init(self):
		self.assertEqual(self.s.driver, self.driver)
		self.assertEqual(self.s.mount, self.mount)
		self.assertEqual(self.s.pin, SENSOR_PIN)

	def test_sense(self):
		with self.assertRaises(NotImplementedError):
			self.s.sense(foo='bar')

	def test_center(self):
		self.s.center()
		self.mount.center.assert_called_once_with()

class UltrasonicSensorTest(unittest.TestCase):
	"""Unit tests for the UltrasonicSensor class."""

	def setUp(self):
		self.driver = MagicMock()
		self.mount = MagicMock()
		self.s = sensor.UltrasonicSensor(driver=self.driver,
										 mount=self.mount,
										 pin=SENSOR_PIN)

	@patch('sensor.UltrasonicSensor.sense_swath')
	def test_sense(self, mock_sense_swath):
		mock_sense_swath.return_value = 50
		self.assertEqual(self.s.sense(x=45), 50)
		mock_sense_swath.assert_called_once_with(45)

	def test_sense_distance(self):
		"""Verify actions to take a distance measurement."""

		measurements = [29, 29, 28]
		self.driver.us_dist.side_effect = lambda x: measurements.pop()
		expected_measurement = 29 + sensor.MOUNT_ERROR

		self.assertEqual(self.s.sense_distance(60), expected_measurement)
		self.mount.move.assert_called_once_with(x=60)

	@patch('sensor.UltrasonicSensor.sense_distance')
	def test_sense_swath(self, mock_sense_distance):
		measurements = [101, 100, 102]
		mock_sense_distance.side_effect = lambda x: measurements.pop()

		self.assertEqual(self.s.sense_swath(350), 100)
		expected_calls = [call(330), call(350), call(10)]
		self.assertEqual(mock_sense_distance.call_args_list,
						 expected_calls)

	@patch('sensor.UltrasonicSensor.sense_distance')
	def test_sense_swath_out_of_arc(self, mock_sense_distance):
		mock_sense_distance.side_effect = ValueError()
		with self.assertRaises(ValueError):
			self.s.sense_swath(180)
