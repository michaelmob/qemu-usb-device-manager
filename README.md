 # QEMU USB Device Manager
 
 QEMU USB Device Manager is a limited wrapper of the QEMU monitor for USB management.
 
 **What is the purpose?**  
 The purpose of this project is to create a safe and stable way of adding and removing USB devices to and fro a host and virtual machine. The USB devices are passed through to the virtual machine, essentially, making them native input.
 
 **How does this compare to ...?**  
 This project's method is a software-alternative to a [KVM switch](https://en.wikipedia.org/wiki/KVM_switch).  It also differs from network KVM solutions, such as [Synergy](https://symless.com/synergy), as the USB devices are passed through to the virtual machine and, therefore, input is not subject to network latency.
 
 **Why not use the built-in USB device manager in a VM manager?**  
1. Can add and remove USB devices from within the virtual machine.
2. Addition/removal can be ran from inside of a script.
3. Can be tied to a hotkey (by your WM/DE) for addition/removal in a single keypress.

## Requirements
* Python 3.4 or higher
* QEMU 2.10.0 or higher

## Setup
**Host machine setup**
You must include the monitor flag in your QEMU command, or the equivalent in your Libvirt config.
```
-monitor telnet:0.0.0.0:7101,server,nowait,nodelay
```

**Installation method**  
*Installing with escalated privilege (e.g. sudo) creates a quick access executable `usb_dm` for convenience.  Otherwise, you will need to find run.py of the qemu-usb-device-manager directory in your Python's site-packages.*  
```sh
# Install with pip.  Recommended: use 'sudo' in your Linux distribution.
pip install https://github.com/PassthroughPOST/qemu-usb-device-manager/archive/master.zip --upgrade

# Create your configuration file.

# Start program in interactive mode.
usb_dm
```

**No installation method**
1. Download and extract a release zip or the master branch zip.
2. Create your configuration file.
3. Execute `run.py` (instead of usb_dm).
 
## Configuration
An example configuration is [located here](https://github.com/PassthroughPOST/qemu-usb-device-manager/blob/master/_qemu_usb_dm_config.yml).

Unless specified by the --config flag, this program will search for `qemu_usb_dm_config.yml` in the following order:
1. Current directory. (pwd)
2. Home directory. (~)
3. Project directory.
4. `QEMU_USB_DEVICE_MANAGER_CONFIG` environment variable.


## Arguments
```
--name, --set, -n, -s | set virtual machine
--command, -c | run command
--config, --conf | specify configuration file path
--log | specify log file path
```

## Commands
```
- help | List commands
- version | Display version
- exit | Exit limited monitor
- wait [seconds] | Wait for an amount of time
- reload | Reload config file
- update | Update config file from 'configuration-url'
- monitor | Show monitor information
- list | List USB devices connected to virtual machine
- hostlist | List USB devices connected to host machine
- set | Show available virtual machines
- set [name] | Set active machine by name
- add | Add all USB devices
- add [id] | Add USB device by id
- add [name] | Add USB device by specified name
- remove | Remove all USB devices
- remove [id] | Remove USB device by id
- remove [name] | Remove USB device by specified name
```

## Examples
```sh
# Note: 'usb_dm' is only available when installed using pip with escalated privileges.
# Otherwise, inside of the project's path 'run.py' must be substituted for 'usb_dm'.

# Start in interactive mode
usb_dm

# Add devices to virtual machine vm-1
usb_dm -n vm-1 -c add

# Remove devices from virtual machine vm-1
usb_dm -n vm-1 -c remove

# Add mouse and keyboard to vm-1
usb_dm -n vm-1 -c "add mouse" "add keyboard"

# Add device by vendor and product id
usb_dm -n vm-1 -c "add 046d:c52b"
```
