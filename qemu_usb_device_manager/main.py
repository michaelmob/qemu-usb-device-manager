#!/usr/bin/env python3
import os
import sys
from argparse import ArgumentParser
from . import constants
from .client import Client
from .utils import directories, find_file


def main():
	"""
	Run QEMU USB Device Manager.
	"""
	directories_ = directories()

	# Arguments
	parser = ArgumentParser(description="Limited QEMU Monitor Wrapper for USB management")
	parser.add_argument("--name", "--set", "-n", "-s", help="Name of virtual machine")
	parser.add_argument("--command", "-c", help="Command", nargs="*")
	parser.add_argument("--config", "--conf", help="YAML config file location", nargs="?")
	parser.add_argument("--log", help="Log file location", nargs="?")
	args = parser.parse_args()

	# Configuration File
	config_filepath = None

	if args.config and os.path.isfile(args.config):
		config_filepath = args.config

	else:
		extensions = (".yml", ".yaml")

		# Attempt to find local config
		config_filepath = find_file(
			(directories_["CURRENT_DIR"],),
			constants.CONFIG_NAME_SHORT,
			extensions
		)

		# Search in BASE_DIR and HOME_DIR now
		if not config_filepath:
			config_filepath = find_file(
				directories_.values(),
				constants.CONFIG_NAME_LONG,
				extensions
			)

		# Environment variable?
		if not config_filepath:
			config_filepath = os.environ.get("QEMU_USB_DEVICE_MANAGER_CONFIG", None)

	if not (config_filepath and os.path.isfile(config_filepath)):
		print(constants.CONFIG_DOES_NOT_EXIST % config_filepath)
		print(constants.CONFIG_LOOKED_FOR % constants.CONFIG_NAME_LONG)
		for name, directory in directories_.items():
			print("- %s: %s" % (name, directory))

		# Some Windows installs don't give the user enough time to read the
		# error message before closing
		import time
		time.sleep(3)
		sys.exit(0)


	# Log File
	log_filepath = None

	log_env = os.environ.get("QEMU_USB_DEVICE_MANAGER_LOG")
	if log_env:
		log_filepath = log_env


	# Monitor Wrapper Client
	client = Client(args.name, config_filepath, args.log)


	# Loop over CLI commands when commands specified
	if args.command:
		for command in args.command:
			print(">" + command)
			client.run_command(command)


	# Otherwise, run forever
	else:
		while True:
			client.run_command(input(">"))


if __name__ == "__main__":
	main()