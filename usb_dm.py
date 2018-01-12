#!/usr/bin/python3
import os
import sys
from argparse import ArgumentParser
from src import constants, client


HOME_PATH = os.path.expanduser("~")
BASE_PATH = os.path.dirname(__file__)


# Arguments
parser = ArgumentParser(description="Limited QEMU Wrapper for USB Switching")
parser.add_argument("--name", "-n", help="Name of virtual machine")
parser.add_argument("--command", "-c", help="Command", nargs="*")
parser.add_argument("--config", help="YAML/JSON config file location", nargs="?")
args = parser.parse_args()


# Configuration
if args.config and os.path.isfile(args.config):
	config_filepath = args.config

else:
	possible_config_filepaths = (
		os.path.join(BASE_PATH, "config.yml"),
		os.path.join(BASE_PATH, "config.json"),
		os.path.join(HOME_PATH, "usb_dm_config.yml"),
		os.path.join(HOME_PATH, "usb_dm_config.json")
	)

	for path in possible_config_filepaths:
		if os.path.isfile(path):
			config_filepath = path
			break


if not os.path.isfile(config_filepath):
	print(constants.CONFIG_DOES_NOT_EXIST % config_filepath)
	sys.exit(0)


# Monitor Wrapper Client
client = client.Client(config_filepath, args.name)


# Loop over CLI commands when commands specified
if args.command:
	for command in args.command:
		print(">" + command)
		client.run_command(command)


# Otherwise, run forever
else:
	while True:
		client.run_command(input(">"))