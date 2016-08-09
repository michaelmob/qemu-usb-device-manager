import json
from sys import exit
from threading import Event
from time import sleep
from monitor import Monitor

class Client(object):
	"""Client that interacts with monitor on a higher level
	"""
	def __init__(self, config_filepath, machine_name, localhost_replace=None):
		"""Load configuration from json file 
		
		Args:
			config_filepath (str): Configuration file path
			machine_name (str): Virtual machine name
		"""
		self.config_filepath = config_filepath
		self.machine_name = machine_name
		self.localhost_replace = localhost_replace
		self.load_config()
		print("Limited QEMU Monitor Client for USB Switching")
		print("Type 'help' for a list of commands.")


	def load_config(self):
		"""Load configuration file 
		"""
		with open(self.config_filepath) as f:
			_dict = json.load(f)

		# Verify required keys are present
		rewrite = False
		required_keys = ("usb-devices", "virtual-machines")

		for key in required_keys:
			if not key in _dict.keys():
				_dict[key] = {}
				rewrite = True
				print("Element '%s' missing from config." % key)

		if rewrite:
			print("Adding required elements. Please modify them in your config.")
			print("Reload by typing 'reload' after you are finished.", "\n")
			with open(self.config_filepath, "w") as f:
				json.dump(_dict, f)
			return self.load_config()

		# Get useful info from config
		self.usb_devices_full = {
			k: v for k, v in _dict["usb-devices"].items()
				if v.get("action") != "disabled"
		}
		self.usb_devices = list(self.usb_devices_full.values())
		self.vm_names = list(_dict["virtual-machines"].keys())
		self.config = _dict["virtual-machines"].get(self.machine_name)

		if not self.config:
			return

		# Determine if we need to replace localhost from full config
		if "localhost-replace" in _dict.keys():
			self.localhost_replace = _dict["localhost-replace"]

		# Create monitor
		if "monitor" in self.config:
			host = self.config["monitor"]

			if self.localhost_replace:
				host = (host
					.replace("127.0.0.1", self.localhost_replace)
					.replace("localhost", self.localhost_replace))

			self.monitor = Monitor(host)


	def monitor_command(self, func):
		"""Quick monitor command: Connect, run, disconnect 
		
		Args:
			func (function): Callback function
		"""
		if not self.monitor.connect():
			print("Could not connect to monitor.")
			return
		result = func(self.monitor)
		self.monitor.disconnect()
		return result


	def device_names_to_ids(self, devices):
		"""Create list of devices by searching for 'devices' values and trying
		to find 'usb_devices_full' keys with them, otherwise use same value
		
		Args:
			devices (list): List of devices
		"""
		result = []

		for device in devices:
			name = self.usb_devices_full.get(device)
			result.append(name.get("id") if name else device)

		return result


	def parse_command(self, text):
		"""Split command and args 
		
		Args:
			text (str): Command
		"""
		text = text.split(" ", 1)
		return (text[0], text[1].split(" ") if len(text) > 1 else None)


	def run_command(self, text):
		"""Run command for monitor 
		
		Args:
			text (str): Command
		"""
		command, args = self.parse_command(text)

		# List commands
		if command == "help":
			self.command_help(args)

		elif command == "exit" or command == "quit":
			exit(0)

		elif command == "wait" or command == "sleep":
			if args: sleep(float(args[0]))

		# Reload configuration file
		elif command == "reload":
			self.load_config()

		# Show monitor information
		elif command == "monitor":
			self.command_monitor(args)

		# Set active machine
		elif command == "set":
			self.command_set(args)

		# ** All commands below require that monitor is set and online **
		elif not self.config:
			print("No virtual machine is set. Set one with the 'set' command.")

		# List USB devices
		elif command == "list":
			self.command_list(args)

		# List USB devices connected to host
		elif command == "hostlist" or command == "listhost":
			self.command_hostlist(args)

		# Add USB device
		elif command == "add":
			self.command_add(args)

		# Remove USB devices
		elif command == "remove" or command == "rem" or command == "del":
			self.command_remove(args)

		else:
			print("Unknown command. Type 'help' for a list of commands.")


	def command_help(self, args):
		"""List commands 
		
		Args:
			args (list): List arguments
		"""
		print("- help - List commands")
		print("- exit - Exit limited monitor")
		print("- wait [seconds] - Wait for an amount of time")
		print("- reload - Reload config file")
		print("- monitor - Show monitor information")
		print("- list - List USB devices connected to virtual machine")
		print("- hostlist - List USB devices connected to host")
		print("- set - Show available virtual machines")
		print("- set [name] - Set active machine by name")
		print("- add - Add all USB devices")
		print("- add [id] - Add USB device by id")
		print("- add [name] - Add USB device by specified name")
		print("- remove - Remove all USB devices")
		print("- remove [id] - Remove USB device by id")
		print("- remove [name] - Remove USB device by specified name")


	def command_monitor(self, args):
		"""Show monitor information

		Args:
			args (list): List arguments
		"""
		try:
			print("Host:", self.monitor.host)
		except:
			print("No monitor set.")
			return
			

	def command_set(self, args):
		"""Set active machine 
		
		Args:
			args (list): List arguments
		"""
		if args:
			# Backup old name, and reload new one
			old_name = self.machine_name
			self.machine_name = args[0]
			self.load_config()

			if not self.config:
				print("Invalid virtual machine.")

				# Reload old config
				self.machine_name = old_name
				self.load_config()
			else:
				print("Virtual machine set.")
				return  # Return to not show available virtual machines

		# Show available virtual machines
		print("Set Virtual Machine:", self.machine_name)
		print("Virtual Machines: ")
		for name in self.vm_names:
			print("-", name, "[Active]" if name == self.machine_name else "")


	def command_list(self, args):
		"""List USB devices connected to virtual machine 
		
		Args:
			args (list): List arguments
		"""
		if not self.monitor.connect():
			print("Could not connect to monitor.")
			return

		for device in self.monitor.usb_devices_more():
			print("- ID: %s / Device: %s / %s" % (
				device.get("id", "Unknown  "),
				device["device"], device["product"]
			))

		self.monitor.disconnect()

	def command_hostlist(self, args):
		"""List USB devices connected to host 
		
		Args:
			args (list): List arguments
		"""
		if not self.monitor.connect():
			print("Could not connect to monitor.")
			return

		# Display host usb devices
		for device in self.monitor.host_usb_devices_more():
			print("- ID: %s / %s %s" % (
				device.get("id", "Unknown"), device.get("product", "Unknown"),
				"[Connected]" if "device" in device else "",
			))

		self.monitor.disconnect()


	def command_add(self, args):
		"""Add USB devices 
		
		Args:
			args (list): List arguments
		"""
		# Add all USB devices
		if not args:
			args = [  # Only add devices without the action of "remove only"
				device["id"] for device in self.usb_devices
					if device.get("action") != "remove only"
			]
		else:
			args = self.device_names_to_ids(args)
		
		# Add USB device
		if not self.monitor_command(lambda m: m.add_usb(args)):
			print("Could not add one or more of devices: %s" % args)


	def command_remove(self, args):
		"""Remove USB devices 
		
		Args:
			args (list): List arguments
		"""
		# Remove all USB devices
		if not args:
			args = [  # Only add devices without the action of "add only"
				device["id"] for device in self.usb_devices
					if device.get("action") != "add only"
			]
		else:
			args = self.device_names_to_ids(args)

		# Remove USB device
		if not self.monitor_command(lambda m: m.remove_usb(args)):
			print("Could not remove one or more of devices: %s" % args)