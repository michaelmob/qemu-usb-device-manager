#!/usr/bin/python3
import os
import sys
from argparse import ArgumentParser
from client import Client
from utils import get_gateway


# Arguments
parser = ArgumentParser(description="Limited QEMU Monitor for USB Switching")
parser.add_argument("--name", help="name of virtual machine")
parser.add_argument("--config", help="JSON config file location", nargs="?")
parser.add_argument("--localhost", help="replace localhost/127.0.0.1 with value")
parser.add_argument("--command", help="command", nargs="*")
args = parser.parse_args()


# Configuration
config_filepath = args.config or os.path.join(os.path.dirname(__file__), "config.json")

if not os.path.isfile(config_filepath):
	print("Configuration file (%s) does not exist" % config_filepath)
	sys.exit(0)


# Replace localhost on client; useful when machine is a VM
if args.localhost == "gateway":
	args.localhost = get_gateway()


# Monitor Wrapper Client
client = Client(config_filepath, args.name, args.localhost)


# Loop over cli commands
if args.command:
	for command in args.command:
		print(">" + command)
		client.run_command(command)


# Run forever
while True:
	client.run_command(input(">"))