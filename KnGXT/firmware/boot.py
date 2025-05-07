# SPDX-FileCopyrightText: 2022 Kodachi 6 14
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2022 Kodachi 6 14
#
# This file is part of the MacroPaw firmware.
#
# The MacroPaw firmware is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or any
# later version.
#
# The MacroPaw firmware is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the MacroPaw firmware. If not, see <https://www.gnu.org/licenses/>.

import supervisor

# CircuitPython's supervisor will use the RGBs to single very low-level
# status, but if we leave the brightness at the default of 255, it's
# pretty blinding. Crank that down.
supervisor.runtime.rgb_status_brightness = 16

import os
import storage
import usb_cdc

from firstboot import FirstBoot
from bootkeys import BootKeys

# Start by assuming that nothing special is going on.
enable_hardware_test = False
enable_mass_storage = False

firstboot = FirstBoot()
bootkeys = BootKeys()

if firstboot.check():
    # First boot. Enable hardware test mode.
    enable_hardware_test = True

# Next up, check key combinations. BootKeys will also handle using the LEDs to
# indicate what mode you're in.

if bootkeys.check_mass_storage():
    enable_mass_storage = True

if bootkeys.check_hardware_test():
    enable_hardware_test = True

# Manage the /hardware_test file depending on whether we're in
# hardware test mode or not.

try:
    storage.remount("/", readonly=False)
except Exception as e:
    print(f"boot: could not remount / read-write: {e}")

if enable_hardware_test:
    try:
        with open("/hardware_test", "w") as f:
            f.write("1")
    except Exception as e:
        print(f"boot: can't create /hardware_test: {e}")
else:
    try:
        os.remove("/hardware_test")
    except:
        pass

try:
    storage.remount("/", readonly=True)
except Exception as e:
    print(f"boot: could not remount / read-only: {e}")

if not enable_mass_storage:
    # Disable mass storage:
    storage.disable_usb_drive()

    if not enable_hardware_test:
        # Disable USB serial.
        usb_cdc.disable()

bootkeys.wait_for_release()
bootkeys.deinit()
