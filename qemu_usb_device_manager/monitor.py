from time import sleep
from sys import stderr
from telnetlib import Telnet
from . import constants



class Monitor(object):
	"""
	Monitor class is a very limited wrapper for the QEMU Monitor.
	It connects through telnet to control the virtual machine's monitor.
	"""

	def __init__(self, host):
		"""
		Initialize Monitor class.
		
		Args:
			host (str): IP address and Port of Telnet monitor
		"""
		host = host.split(":")
		port = int(host[1]) if host[1].isnumeric() else 23

		self.host = (host[0], port)
		self.is_connected = False


	def connect(self, retry=True, retry_wait=0.25, max_retries=5, _retries=0):
		"""
		Connect to Telnet monitor.
		
		Args:
			retry (bool, optional): Attempt retry if connection is not successful
			retry_wait (float, optional): Amount of time to wait for retrying
			max_retries (int, optional): Maximum amount of retries
		"""
		if self.is_connected:
			return

		try:
			self.telnet = Telnet(*self.host)

			if not "QEMU" in self.__read(True):
				if not retry or _retries >= max_retries:
					raise ConnectionAbortedError(constants.MONITOR_IN_USE)
		
				sleep(retry_wait)
				return self.connect(retry, max_retries, _retries + 1)
			else:
				self.is_connected = True
		except:
			self.is_connected = False

		return self.is_connected


	def disconnect(self):
		"""
		Close Telnet monitor socket.
		"""
		self.telnet.close()
		self.is_connected = False
		sleep(0.1)
		return not self.is_connected


	def __write(self, value):
		"""
		Write string to monitor.
		
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
		"""
		Read from monitor.
		"""
		if not self.is_connected and not _force_read:
			return ""

		sleep(0.05)  # Data has a delay
		try:
			return str(self.telnet.read_very_eager().decode("utf-8"))
		except BrokenPipeError:
			self.is_connected = False


	def add_usb(self, device):
		"""
		Add USB device by vendor:product id.
		Verify that device is not already added.
		
		Args:
			device (Union[str, list]): Device ID
		"""
		result = True

		# Single device
		if type(device) is str:
			if not self.id_is_connected(device):
				args = "usb-host,vendorid=0x%s,productid=0x%s,id=%s" % (
					self.device_ids(device)
				)
				self.__write("device_add " + args)
			else:
				return False

		# Multiple devices
		elif type(device) is list:
			devices = device
			for device in devices:
				if not self.add_usb(device):
					result = False

		return (not "could not" in self.__read()) if result else result


	def remove_usb(self, device):
		"""
		Remove USB device by vendor id.
		
		Args:
			device (Union[str, list]): Device ID
		"""

		# Single device
		if type(device) is str:
			# Prefer removing by user-supplied ID
			args = self.device_to_userid(device)
			if args is None:
				args = self.device_ids(device)[2]
			self.__write("device_del " + args)

		# Multiple devices
		elif type(device) is list:
			devices = device
			for device in devices:
				self.remove_usb(device)

		return not "could not" in self.__read()


	def device_ids(self, value):
		"""
		Split vendor id and product id.

		Args:
			value (str): device vendor and product id

		Returns:
			tuple: (vendor id, product id, cosmetic id)
		"""
		vendor_id, product_id = tuple(value.split(":")[-2:])
		cosmetic_id = "device-%s-%s" % (vendor_id, product_id)
		return (vendor_id, product_id, cosmetic_id)


	def device_to_userid(self, value):
		"""
		Find user-supplied ID (if any) from vendor and product id
		
		Args:
			value (str): Vendor:Product ID
		Returns:
			User ID if found, otherwise it returns None
		"""
		data = self.usb_devices_more()

		if value.startswith("host:"):
			value = value[5:]

		return next((d.get("userid", None) for d in data if d["id"] == value), None)


	def id_is_connected(self, value):
		"""
		Test if device is connected by vendor and product id.
		
		Args:
			value (str): Vendor:Product ID

		Returns:
			bool, connected or not
		"""
		data = self.usb_devices_more()

		if value.startswith("host:"):
			value = value[5:]

		return any(d["id"] == value for d in data)


	def usb_devices(self):
		"""
		List USB devices from monitor.
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

				# ID: means the device has user-supplied ID on the host
				if key == "id:":
					device["userid"] = element[4:]
				else:
					device[key] = element[len(key)+1:]

			# Add device to the result
			result.append(device)

		return result


	def usb_devices_more(self):
		"""
		Show all USB device information from connected devices.
		"""
		return [
			device for device in self.host_usb_devices_more()
				if "device" in device
		]


	def host_usb_devices(self):
		"""
		List USB devices connected to host.
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
		"""
		Show all USB device along with their details.
		"""
		host_devices, vm_devices = self.host_usb_devices(), self.usb_devices()

		# Loop through both: host_device and vm_devices; compare product names
		# and combine dictionaries
		for host_device in host_devices:
			for vm_device in vm_devices:
				if vm_device.get("product", 0) == host_device.get("product", 1):
					host_device.update(vm_device)

		return host_devices