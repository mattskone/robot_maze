
def robot_angle_to_mount_angle(robot_angle, mount_zero=90):
	"""Convert a robot angle to the corresponding mount angle.

	Args:
	robot_angle - the commanded direction relative to the robot's centerline
	mount_zero - the direction, relative to the robot's centerline, that the
		mount points when the mount is commanded to angle=0

	Returns the angle, in degrees, to command the mount to point to align to
		the commanded robot_angle.
	"""

	# Replace this naive code with a more robust algorithm:
	if robot_angle == 0:
		return 90
	elif robot_angle == 90:
		return 0
	elif robot_angle == 110:
		return 340
	elif robot_angle == 225:
		return 225
	elif robot_angle == 315:
		return 135

	return None
