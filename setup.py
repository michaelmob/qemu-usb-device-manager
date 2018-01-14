#!/usr/bin/env python3
from distutils.core import setup


setup(
	name="qemu_usb_device_manager",
	version="1.1",  # Remember to change version in constants.py too!
	description="Limited QEMU Monitor Wrapper for USB management",
	url="https://github.com/PassthroughPOST/qemu-usb-device-manager",
	py_modules=["qemu_usb_device_manager"],
	packages=["qemu_usb_device_manager"],
	license="BSD-2-Clause",
	entry_points={
        "console_scripts": ["usb_dm=qemu_usb_device_manager:run"],
    },
	install_requires=[
		"pyyaml"
	]
)