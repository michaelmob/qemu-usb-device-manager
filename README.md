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
...
 
## Configuration
...

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
```
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