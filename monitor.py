from time import sleep
from sys import stderr
from telnetlib import Telnet

class Monitor(object):
	"""Monitor class is a very limited wrapper for the QEMU Monitor.
	It connects through telnet to control the virtual machine's monitor.
	"""
	is_connected = False

	def __init__(self, host):
		"""Initializer 
		
		Args:
		    host (str): IP address and Port of Telnet monitor
		"""
		host = host.split(":")
		self.host = (host[0], int(host[1]) if len(host[1]) > 1 else 23)
		

	def connect(self, retry=True, retry_wait=0.25, max_retries=5, _retries=0):
		"""Connect to Telnet monitor 
		
		Args:
		    retry (bool, optional): Attempt retry if connection is not successful
		    retry_wait (float, optional): Amount of time to wait for retrying
		    max_retries (int, optional): Maximum amount of retries
		"""
		if self.is_connected:
			return

		try:
			self.telnet = Telnet(self.host[0], self.host[1])

			if not "QEMU" in self.__read(True):
				if not retry or _retries >= max_retries:
					raise ConnectionAbortedError("Monitor is already in use.")
		
				sleep(retry_wait)
				return self.connect(retry, max_retries, _retries + 1)
			else:
				self.is_connected = True
		except:
			self.is_connected = False

		return self.is_connected


	def disconnect(self):
		"""Close Telnet monitor socket 
		"""
		self.telnet.close()
		self.is_connected = False
		sleep(0.1)
		return self.is_connected


	def __write(self, value):
		"""Write string to monitor 
		
		Args:
		    value (str): Text to write to telnet monitor
		"""
		if not self.is_connected:
			return

		try:
			self.telnet.write(bytes(str(value + "\n").encode("utf-8")))
		except BrokenPipeError:
			self.is_connected = False


	def __read(self, _force_read=False):
		"""Read from monitor 
		"""
		if not self.is_connected and not _force_read:
			return ""

		sleep(0.05)  # Data has a delay
		try:
			return str(self.telnet.read_very_eager().decode("utf-8"))
		except BrokenPipeError:
			self.is_connected = False


	def add_usb(self, device, no_duplicates=True):
		"""Add USB device by vendor:product id 
		
		Args:
		    device (str): Device ID
		    no_duplicates (str): Check that USB device isn't already added
		"""
		if no_duplicates:
			data = self.usb_devices_more()

		result = True

		if type(device) is str:
			device = self.default_usb_type(device)
			if not (no_duplicates and self.id_is_connected(device)):
				self.__write("usb_add %s" % device)
			else:
				return False

		elif type(device) is list:
			for _id in device:
				_id = self.default_usb_type(_id)
				if not (no_duplicates and self.id_is_connected(_id)):
					self.__write("usb_add %s" % _id)
				else:
					result = False

		return (not "could not" in self.__read()) if result else result


	def remove_usb(self, device):
		"""Remove USB device by vendor id 
		
		Args:
		    device (str): Device ID
		"""
		if type(device) is str:
			self.__write("usb_del %s" % self.id_to_device(device))

		elif type(device) is list:
			data = self.usb_devices_more()
			for _id in device:
				self.__write("usb_del %s" % self.id_to_device(_id, data))

		return not "could not" in self.__read()


	def default_usb_type(self, value):
		"""Defaults for usb_type; host:, serial:, disk: etc...

		Values split by semicolon with both elements having 4 characters will
		automatically be prefixed with "host:"
		
		Args:
		    value (str): Device ID
		
		Returns:
		    str: Manipulated device ID
		"""
		if ":" in value:
			_value = value.split(":")
			if not (len(_value) > 2 or _value[0] == "disk"):
				if len(_value[0]) == 4 and len(_value[1]) == 4:
					return "host:" + value
		return value


	def id_to_device(self, value, data=None):
		"""Find device id (0.0) from vendor and product id by comparing
		host device names to connected virtual machine device names.
		
		Args:
		    value (str): Vendor:Product ID
		    data (bool, optional): Prefetched data of .host_usb_devices_more()

		Returns:
			Device if found, otherwise it returns original value
		"""
		if not data:
			data = self.usb_devices_more()

		if value.startswith("host:"):
			value = value[5:]

		return next((d["device"] for d in data if d["id"] == value), value)
		

	def id_is_connected(self, value, data=None):
		"""Find if device is connected by vendor and product id.
		
		Args:
		    value (str): Vendor:Product ID
		    data (bool, optional): Prefetched data of .host_usb_devices_more()

		Returns:
			bool, connected or not
		"""
		if not data:
			data = self.usb_devices_more()

		if value.startswith("host:"):
			value = value[5:]

		return any(d["id"] == value for d in data)
		

	def usb_devices(self):
		"""List USB devices from monitor
		"""
		if not self.is_connected:
			return []

		self.__write("info usb")
		data = self.__read()
		result = []

		if not data:
			return result

		for line in data.splitlines():
			if line[0] != " ":
				continue

			# Split line to harvest info
			line = line.strip().replace(", ", ",").split(",")
			device = {}

			# Add info about device to dict
			for element in line:
				key = element.lower().split(" ")[0]
				device[key] = element[len(key)+1:]

			# Add device to the result
			result.append(device)

		return result


	def usb_devices_more(self):
		"""Show all USB device information from connected devices
		"""
		return [
			device for device in self.host_usb_devices_more()
				if "device" in device
		]


	def host_usb_devices(self):
		"""List USB devices connected to host
		"""
		if not self.is_connected:
			return []

		self.__write("info usbhost")
		data = self.__read()
		result = []

		if not data:
			return result

		for line in data.splitlines():
			if line[0] != " ":
				continue

			line = line.strip().replace(", ", ",").split(",")

			# First line of device info starts with "Bus"
			if line[0][0] == "B":
				# Split line to harvest info
				device = {}

				# Add info about device to dict
				for element in line:
					key = element.lower().split(" ")[0]
					device[key] = element[len(key)+1:]

				# Add device to the result
				result.append(device)

			# Second line of device info starts with "Class"
			elif line[0][0] == "C":
				result[-1]["product"] = line[1]
				result[-1]["id"] = line[0][-9:]

		return result


	def host_usb_devices_more(self):
		"""Show all USB device information
		"""
		host_devices, vm_devices = (self.host_usb_devices(), self.usb_devices())

		# Loop through both: host_device and vm_devices; compare product names
		# and combine dictionaries
		for host_device in host_devices:
			for vm_device in vm_devices:
				if vm_device.get("product", 0) == host_device.get("product", 1):
					host_device.update(vm_device)
		return host_devices