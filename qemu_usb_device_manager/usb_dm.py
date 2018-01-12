#!/usr/bin/env python3
import os
import sys
from argparse import ArgumentParser
from .src import constants, client


HOME_PATH = os.path.expanduser("~")
BASE_PATH = os.path.dirname(__file__)


# Arguments
parser = ArgumentParser(description="Limited QEMU Monitor Wrapper for USB management")
parser.add_argument("--name", "-n", help="Name of virtual machine")
parser.add_argument("--command", "-c", help="Command", nargs="*")
parser.add_argument("--config", help="YAML/JSON config file location", nargs="?")
parser.add_argument("--log", help="Log file location", nargs="?")
args = parser.parse_args()


# Configuration File
config_filepath = None

if args.config and os.path.isfile(args.config):
	config_filepath = args.config

else:
	possible_config_filepaths = (
		os.path.join(BASE_PATH, "config.yml"),
		os.path.join(BASE_PATH, "config.json"),
		os.environ.get("QEMU_USB_DEVICE_MANAGER_CONFIG"),
		os.path.join(HOME_PATH, "usb_dm_config.yml"),
		os.path.join(HOME_PATH, "usb_dm_config.json")
	)

	for path in possible_config_filepaths:
		if path and os.path.isfile(path):
			config_filepath = path
			break


if not (config_filepath and os.path.isfile(config_filepath)):
	print(constants.CONFIG_DOES_NOT_EXIST % config_filepath)
	sys.exit(0)


# Log File
log_filepath = None

log_env = os.environ.get("QEMU_USB_DEVICE_MANAGER_LOG")
if log_env:
	log_filepath = log_env


# Monitor Wrapper Client
client = client.Client(args.name, config_filepath, args.log)


# Loop over CLI commands when commands specified
if args.command:
	for command in args.command:
		print(">" + command)
		client.run_command(command)


# Otherwise, run forever
else:
	while True:
		client.run_command(input(">"))