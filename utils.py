import re
from platform import system
from subprocess import check_output

def get_gateway():
	"""Find gateway IP Address from ipconfig

	* Note: This is not good, but is the only way to do it without
	using external dependencies
	
	Returns:
		str
	"""
	if system() != "Windows":
		print("get_gateway() is currently only supported on Windows")
		return

	pattern = re.compile("y[\.|\ ]+:(?:\s.*?)+((?:[0-9]+\.){3}[0-9])")
	output = pattern.search(check_output("ipconfig").decode())
	return output.group(1) if output else None