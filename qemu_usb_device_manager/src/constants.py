VERSION = "1.1.0"  # Remember to change version in setup.py too!


# Monitor
MONITOR_NOT_SET = "No monitor set."
MONITOR_IN_USE = "Monitor is already in use."
MONITOR_CANNOT_CONNECT = "Could not connect to monitor."


# Client
CLIENT_NO_VM_SET = "No virtual machine is set. Set one with the 'set' command."
CLIENT_INVALID_VM = "Invalid virtual machine."
CLIENT_SET_ACTIVE = "'%s' set as active virtual machine."
CLIENT_CURRENT_VM = "Currently set Virtual Machine: %s"
CLIENT_VMS = "Virtual Machines: "
CLIENT_VM_DEVICE = "- ID: %s / Device: %s / %s"
CLIENT_HOST_DEVICE = "- ID: %s / %s %s"
CLIENT_DEVICE_CONNECTED = "[Connected]"
CLIENT_UNKNOWN_COMMAND = "Unknown command. Type 'help' for a list of commands."
CLIENT_CANNOT_ADD = "Could not add device(s): %s"
CLIENT_CANNOT_REMOVE = "Could not remove device(s): %s"
CLIENT_WELCOME = \
"""
Limited QEMU Monitor Wrapper for USB management
Type 'help' for a list of commands.
""".strip()
CLIENT_HELP = \
"""
- help - List commands
- exit - Exit limited monitor
- wait [seconds] - Wait for an amount of time
- reload - Reload config file
- update - Update config file from 'configuration-url'
- monitor - Show monitor information
- list - List USB devices connected to virtual machine
- hostlist - List USB devices connected to host
- set - Show available virtual machines
- set [name] - Set active machine by name
- add - Add all USB devices
- add [id] - Add USB device by id
- add [name] - Add USB device by specified name
- remove - Remove all USB devices
- remove [id] - Remove USB device by id
- remove [name] - Remove USB device by specified name
""".strip()


# Config
CONFIG_DOES_NOT_EXIST = "Configuration file (%s) does not exist."
CONFIG_CANNOT_LOAD = "Cannot load configuration.\n%s"
CONFIG_CANNOT_LOAD_NEW = "Cannot load new configuration."
CONFIG_CANNOT_RELOAD = "Could not reload configuration file."
CONFIG_RELOAD = "Reloaded configuration file."
CONFIG_MISSING_ELEMENT = "Element '%s' missing from config."
CONFIG_CANNOT_REWRITE = "Cannot rewrite configuration."
CONFIG_URL_NOT_SET = "No configuration url set."
CONFIG_UPDATED_FROM_URL = "Updated configuration from url."
CONFIG_REWRITE_MESSAGE = \
"""
Adding required elements. Please modify them in your config.
Reload by typing 'reload' after you are finished.
""".strip()


# Utils
UTIL_GATEWAY_UNSUPPORTED = "get_gateway() is currently only supported on Windows."