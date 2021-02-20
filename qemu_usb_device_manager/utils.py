import os
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


def directories():
	"""
	Dictionary of current, home, and base directories.

	Returns:
		dict
	"""
	return {
		"CURRENT_DIR": os.getcwd(),
		"HOME_DIR": os.path.expanduser("~"),
		"BASE_DIR": os.path.dirname(__file__),
	}


def find_file(directories, filename, extensions):
	"""
	Finds specified file in specified directories.

	Args:
		directories (list): List of directories to search
		filename (str): Name of file to find
		extensions (list): List of extensions

	Returns:
		str if file found
		None if file not found
	"""
	for directory in directories:
		for extension in extensions:
			path = os.path.join(directory, filename + extension)
			if os.path.isfile(path):
				return path