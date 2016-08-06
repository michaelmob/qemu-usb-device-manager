# QEMU USB Device Manager

QEMU USB Device Manager is a very limited QEMU monitor wrapper. The main purpose is to have a safe method for adding and removing devices quickly from both the host and virtual machine.

Most useful when paired with a hotkey manager.

##### How it works
This limited monitor wrapper connects to a QEMU monitor through a Telnet socket per command. When adding a USB device it is made sure that the device ID is not already connected to the device. It also gives the ability to remove devices by their vendor:product ID and by specified name. Along that, it shows detailed information about USB devices connected to the host machine, and virtual machine, making it a breeze to figure out which devices to add.

## Getting Started
1. Clone this repository somewhere on your host machine and virtual machine. Or preferably into a shared directory.
2. Modify config.json to your likings.
3. Run `run.py` with desired arguments.

##### Arguments
* `--name [name]` use config for this virtual machine  
* `--config [filepath]` use config located elsewhere  
* `--localhost [ip/"gateway"]` replace localhost with IP or gateway IP (useful on virtual machines)  
* `--command [COMMAND [COMMAND ...]]` run commands

##### Console Commands
Type `help` in console for a list of console commands
* `exit` - Exit limited monitor
* `wait [seconds]` - Wait for an amount of time
* `reload` - Reload config file
* `monitor` - Show monitor information
* `list` - List USB devices connected to virtual machine
* `hostlist` - List USB devices connected to host
* `set` - Show available virtual machines
* `set [name]` - Set active machine by name
* `add` - Add all USB devices
* `add [id]` - Add USB device by id
* `add [name]` - Add USB device by specified name
* `remove` - Remove all USB devices
* `remove [id]` - Remove USB device by id
* `remove [name]` - Remove USB device by specified name

##### Examples
######Configuration
```json
{
	"usb-devices": {
		"#inactive-item": "1d33:d622",
		"keyboard": "1b1c:1b09",
		"mouse": "046d:c52b"
	},

	"virtual-machines": {
		"windows-vm-1": {
			"monitor": "127.0.0.1:7101"
		}
	}
}
```

Add all usb-devices, except for :inactive-item" since it starts with a #
`run.py --name windows-vm-1 --localhost gateway --command add exit`

Remove all usb-devices, except for "inactive-item" since it starts with a pound sign
`run.py --name windows-vm-1 --command remove exit`

Only add mouse to virtual machine
`run.py --name windows-vm-1 --command "add mouse" exit`

Add device by vendor:product id
`run.py --name windows-vm-1 --command "add 046d:c52b" exit`

Without `exit` at the end, the console will be left open in interactive mode allowing you to enter more commands.
