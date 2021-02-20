import os
import logging
import yaml
from sys import exit
from socket import gethostname
from time import sleep
from . import constants
from .monitor import Monitor
from .utils import get_gateway, download_string



class Client(object):
	"""
	Client that interacts with monitor on a higher level.
	"""
	required_keys = ("usb-devices", "host-machine", "virtual-machines")
	actions = {
		"ignore": ("ignore", "ignored", "disable", "disabled"),
		"add only": ("add only", "addonly", "add_only", "add-only"),
		"remove only": ("remove only", "removeonly", "remove_only", "remove-only")
	}


	def __init__(self, machine_name, config_filepath, log_filepath=None):
		"""
		Load configuration from yaml file.
		
		Args:
			config_filepath (str): Configuration file path
			machine_name (str): Virtual machine name
		"""
		# Initiate logging
		if log_filepath:
			logging.basicConfig(filename=log_filepath)

		self.config_filepath = config_filepath
		self.machine_name = machine_name
		self.load_config()
		print(constants.CLIENT_WELCOME)


	def load_config(self):
		"""
		Load configuration file.
		** This method needs to be split up and cleaned.
		"""
		try:
			with open(self.config_filepath) as f:
				self.config = yaml.load(f, Loader=yaml.FullLoader)
		except Exception as exc:
			logging.exception(exc)
			return False

		# Verify required keys are present
		rewrite_required = False
		
		# Find missing elements
		for key in self.required_keys:
			if not key in self.config.keys():
				self.config[key] = {}
				rewrite_required = True
				print(constants.CONFIG_MISSING_ELEMENT % key)

		# Rewrite configuration with required elements
		if rewrite_required:
			print(constants.CONFIG_REWRITE_MESSAGE)
			try:
				with open(self.config_filepath, "w") as f:
					yaml.dump(self.config, f)
			except Exception as exc:
				print(constants.CONFIG_CANNOT_REWRITE)
				logging.exception(exc)
				return False
			return self.load_config()

		self.configuration_url = self.config.get("configuration-url", None)
		self.host_config = self.config["host-machine"]

		# Set machine by hostname if not specified
		if not self.machine_name and not self.is_host_machine():
			hostname = gethostname()
			for key, value in self.config["virtual-machines"].items():
				if "hostname" in value and value["hostname"] == hostname:
					self.machine_name = key

		# Get useful info from config
		self.usb_devices_full = {
			k: v for k, v in self.config["usb-devices"].items()
				if v.get("action") not in self.actions["ignore"]
		}

		# VM
		self.vm_config = self.config["virtual-machines"].get(self.machine_name)
		self.vm_names = list(self.config["virtual-machines"].keys())
		self.usb_devices = list(self.usb_devices_full.values())

		# No machine config? No monitor inside machine config? Goodbye.
		if not (self.vm_config and "monitor" in self.vm_config):
			return True

		# Host name for monitor
		monitor_host = self.vm_config["monitor"]

		# If monitor_host starts with a colon, we should guess which IP to use
		# when it's not, Monitor IP:Port is probably specified by user
		if monitor_host[0] != ":":
			self.monitor = Monitor(monitor_host)
			return True

		# Did user define their own monitor host?
		# User can set 'ip-address' to '-' to automatically determine ip address
		default_ip = None
		if self.host_config.get("ip-address", "-") == "-":
			# Are we the host machine?
			if self.is_host_machine():
				default_ip = "127.0.0.1"

			# Or are we the virtual machine?
			else:
				default_ip = get_gateway()
		
		# Remember that "monitor_host" is just a port prefixed with a colon
		host = self.host_config.get("ip-address", default_ip) + monitor_host

		# Create monitor
		self.monitor = Monitor(host)
		return True


	def is_host_machine(self):
		"""
		Determine if current machine is the host.

		Returns:
			bool
		"""
		return self.host_config.get("hostname", "") == gethostname()


	def monitor_command(self, func):
		"""
		The monitor command process: Connect, run, disconnect.
		
		Args:
			func (function): Callback function
		"""
		if not self.monitor.connect():
			print(constants.MONITOR_CANNOT_CONNECT)
			return
		result = func(self.monitor)
		self.monitor.disconnect()
		return result


	def device_names_to_ids(self, devices):
		"""
		Create list of devices by looping through 'devices' values and trying to
		find the keys in 'usb_devices_full'.

		Ignore if not vendor and product id.
		
		Args:
			devices (list): List of devices
		"""
		result = []
		host_devices = self.monitor_command(lambda m: m.host_usb_devices())
		host_ids = [device["id"] for device in host_devices]

		for device in devices:
			# named device
			name = self.usb_devices_full.get(device)
			if name:
				id = name.get("id")

			# vendor and product id
			else:
				id = device if ":" in device else None

			# Be sure ids exist, otherwise the error message below is spat out
			# and VM performance seems to become crippled
			# qemu-system-x86_64: libusb_release_interface: -99 [OTHER]
			# libusb: error [release_interface] release interface failed, error -1 errno 22
			if id in host_ids:
				result.append(id)

		return result


	def parse_command(self, text):
		"""
		Split command and args.
		
		Args:
			text (str): Command
		"""
		text = text.split(" ", 1)
		return (text[0], text[1].split(" ") if len(text) > 1 else None)


	def run_command(self, text):
		"""
		Run command for monitor
		
		Args:
			text (str): Command
		"""
		command, args = self.parse_command(text)

		# List commands
		if command == "help":
			self.command_help(args)

		# Exit
		elif command == "exit" or command == "quit":
			exit(0)

		# Version
		elif command == "version":
			self.command_version(args)

		# Wait
		elif command == "wait" or command == "sleep":
			if args: sleep(float(args[0]))

		# Reload configuration file
		elif command == "reload":
			self.command_reload(args)

		# Update configuration file from 'configuration-url'
		elif command == "update":
			self.command_update(args)
			self.command_reload([])

		# Show monitor information
		elif command == "monitor":
			self.command_monitor(args)

		# Set active machine
		elif command == "set":
			self.command_set(args)

		# ** All commands below require that monitor is set and online **
		elif not self.vm_config:
			print(constants.CLIENT_NO_VM_SET)

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
			print(constants.CLIENT_UNKNOWN_COMMAND)


	def command_info(self, args):
		"""
		Print info about current session.

		Args:
			args (list): List arguments
		"""
		print(constants.CLIENT_INFO % {
			"VERSION": constants.VERSION,
			"CONFIG_FILEPATH": self.config_filepath,
			"HOME_DIR": os.path.expanduser("~"),
			"BASE_DIR": os.path.dirname(__file__),
			"CURRENT_DIR": os.getcwd()
		})


	def command_version(self, args):
		"""
		Print version.
		
		Args:
			args (list): List arguments
		"""
		print(constants.VERSION)


	def command_help(self, args):
		"""
		List commands.
		
		Args:
			args (list): List arguments
		"""
		print(constants.CLIENT_HELP)


	def command_monitor(self, args):
		"""
		Show monitor information.

		Args:
			args (list): List arguments
		"""
		try:
			print("Host:", self.monitor.host)
		except:
			print(constants.MONITOR_NOT_SET)
			return


	def command_update(self, args):
		"""
		Download url set in 'configuration-url' and attempt to parse with YAML.
		If the new config is valid YAML then replace current config.
		
		Args:
			args (list): List arguments
		"""
		old_url = None
		if args:
			old_url = self.configuration_url
			self.configuration_url = args[0]

		if not self.configuration_url:
			print(constants.CONFIG_URL_NOT_SET)
			return

		try:
			# Download new config
			new_config = download_string(self.configuration_url)

			# Parse new config
			new_config = yaml.safe_load(new_config)

			# Attempt parsing and see if required keys are available
			for key in self.required_keys:
				new_config[key]

			# Overwrite old configuration
			with open(self.config_filepath, "w") as f:
				f.write(yaml.dump(new_config))
				print(constants.CONFIG_UPDATED_FROM_URL)

		except Exception as exc:
			if old_url:
				self.configuration_url = old_url

			print(constants.CONFIG_CANNOT_LOAD_NEW)
			logging.exception(exc)


	def command_reload(self, args):
		"""
		Reload configuration.
		
		Args:
			args (list): List arguments
		"""
		if args:
			self.config_filepath = args[0]

		if self.load_config():
			print(constants.CONFIG_RELOAD)
		else:
			print(constants.CONFIG_CANNOT_RELOAD)
			

	def command_set(self, args):
		"""
		Set active machine.
		
		Args:
			args (list): List arguments
		"""
		if args:
			# Backup old name, and reload new one
			old_name = self.machine_name
			self.machine_name = args[0]
			self.load_config()

			if not self.vm_config:
				print(constants.CLIENT_INVALID_VM)

				# Reload old config
				self.machine_name = old_name
				self.load_config()
			else:
				print(constants.CLIENT_SET_ACTIVE % self.machine_name)
				return  # Return to not show available virtual machines

		# Show available virtual machines
		print(constants.CLIENT_CURRENT_VM % self.machine_name)
		print(constants.CLIENT_VMS)
		for name in self.vm_names:
			print("-", name, "[Active]" if name == self.machine_name else "")


	def command_list(self, args):
		"""
		List USB devices connected to virtual machine.
		
		Args:
			args (list): List arguments
		"""
		if not self.monitor.connect():
			print(constants.MONITOR_CANNOT_CONNECT)
			return

		for device in self.monitor.usb_devices_more():
			print(constants.CLIENT_VM_DEVICE % (
				device.get("id", "Unknown  "),
				device["device"], device["product"]
			))

		self.monitor.disconnect()


	def command_hostlist(self, args):
		"""
		List USB devices connected to host.
		
		Args:
			args (list): List arguments
		"""
		if not self.monitor.connect():
			print(constants.MONITOR_CANNOT_CONNECT)
			return

		# Display host usb devices
		for device in self.monitor.host_usb_devices_more():
			print(constants.CLIENT_HOST_DEVICE % (
				device.get("id", "Unknown"), device.get("product", "Unknown"),
				constants.CLIENT_DEVICE_CONNECTED if "device" in device else ""
			))

		self.monitor.disconnect()


	def command_add(self, args):
		"""
		Add USB devices.
		
		Args:
			args (list): List arguments
		"""
		# Add all USB devices
		if not args:
			args = [  # Only add devices without the action of "remove only"
				device["id"] for device in self.usb_devices
					if device.get("action") not in self.actions["remove only"]
			]
		else:
			args = self.device_names_to_ids(args)
		
		# Add USB device
		if self.monitor_command(lambda m: m.add_usb(args)):
			print(constants.CLIENT_ADDED % args)
		else:
			print(constants.CLIENT_CANNOT_ADD % args)


	def command_remove(self, args):
		"""
		Remove USB devices.
		
		Args:
			args (list): List arguments
		"""
		# Remove all USB devices
		if not args:
			args = [  # Only add devices without the action of "add only"
				device["id"] for device in self.usb_devices
					if device.get("action") not in self.actions["add only"]
			]
		else:
			args = self.device_names_to_ids(args)

		# Remove USB device
		if self.monitor_command(lambda m: m.remove_usb(args)):
			print(constants.CLIENT_REMOVED % args)
		else:
			print(constants.CLIENT_CANNOT_REMOVE % args)