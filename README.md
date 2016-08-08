# QEMU USB Device Manager

QEMU USB Device Manager is a very limited QEMU monitor wrapper. The main purpose is to have a safe method for adding and removing devices quickly from both the host and virtual machine.

Most useful when paired with a hotkey manager.

##### How it works
This limited monitor wrapper connects to a QEMU monitor through a Telnet socket per command. When adding a USB device it is made sure that the device ID is not already connected to the device. It also gives the ability to remove devices by their vendor:product ID and by specified name. Along that, it shows detailed information about USB devices connected to the host machine, and virtual machine, making it a breeze to figure out which devices to add.

## Getting Started
1. Clone this repository somewhere on your host machine and virtual machine. Or preferably into a shared directory.
2. Modify your QEMU command or libvirt config to use a telnet server as its monitor. \*\*
3. Modify config.json to your likings.
4. Run `run.py` with desired arguments.

\*\* `-monitor telnet:0.0.0.0:7101,server,nowait,nodelay`

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
// Python's JSON Decoder is VERY strict, look at _config.json for a working
// configuration without comments
{
	"usb-devices": {
		"disabled-device": {
			"id": "1d33:d622", // Vendor:Product ID, can also include "host:"
			"action": "disabled" // Device will be ignored
		},
		"keyboard": {
			"id": "1b1c:1b09"
		},
		"mouse": {
			"id": "046d:c52b"
		},
		"mic": {
			"id": "17a0:0310",
			"action": "add only" // Only added; must be removed manually
		}
	},

	"virtual-machines": {
		"windows-vm-1": {
			"monitor": "127.0.0.1:7101" // Telnet server
		}
	}
}
```

Add all usb-devices, except for "disabled-item"  
`run.py --name windows-vm-1 --localhost gateway --command add exit`

Remove all usb-devices, except for "mic" which "action" is "add only"  
`run.py --name windows-vm-1 --command remove exit`

"add only" actioned devices can be removed manually  
`run.py --name windows-vm-1 --command "remove mic" exit`

Only add mouse to virtual machine  
`run.py --name windows-vm-1 --command "add mouse" exit`

Add device by vendor:product id  
`run.py --name windows-vm-1 --command "add 046d:c52b" exit`

Without `exit` at the end, the console will be left open in interactive mode allowing you to enter more commands.
