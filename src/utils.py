import re
from urllib.request import urlopen
from platform import system
from subprocess import check_output
from . import constants


def get_gateway():
	"""
	Find gateway IP Address from ipconfig.
	Gateway IP Address should ideally be the host machine's local IP address.

	* Note: This is not good, but is the only way to do it without
	using external dependencies
	
	Returns:
		str
	"""
	if system() != "Windows":
		print(constants.UTIL_GATEWAY_UNSUPPORTED)
		return

	pattern = re.compile("y[\.|\ ]+:(?:\s.*?)+((?:[0-9]+\.){3}[0-9])")
	output = pattern.search(check_output("ipconfig").decode())
	return output.group(1) if output else None


def download_string(url):
	"""
	Download string from a URL.

	Returns:
		str
	"""
	return urlopen(url).read().decode("utf-8")