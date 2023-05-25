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

supervisor.runtime.next_stack_limit = 16384
supervisor.runtime.rgb_status_brightness = 16

from adafruit_neopixelbackground import NeoPixelBackground

import digitalio
import board
import os
import storage
import usb_cdc
import time

row0 = digitalio.DigitalInOut(board.ROW0)
row0.direction = digitalio.Direction.OUTPUT

row4 = digitalio.DigitalInOut(board.ROW4)
row4.direction = digitalio.Direction.OUTPUT

col1 = digitalio.DigitalInOut(board.COL1)
col1.direction = digitalio.Direction.INPUT

col2 = digitalio.DigitalInOut(board.COL2)
col2.direction = digitalio.Direction.INPUT

col3 = digitalio.DigitalInOut(board.COL3)
col3.direction = digitalio.Direction.INPUT

bootpixel = NeoPixelBackground(board.NEOPIXEL, 1, pixel_order="GRB", brightness=0.125)
bootpixel[0] = (0, 0, 0)

enable_hardware_test = False
enable_mass_storage = False

def check_row0():
    rc = False
    row0.value = True

    if col1.value and col3.value:
        rc = True

    row0.value = False
    return rc

def check_row4():
    rc = False
    row4.value = True

    if col1.value and col2.value:
        rc = True

    row4.value = False
    return rc

storage.remount("/", readonly=False)

try:
    open("/firstboot", "r")
    enable_hardware_test = True

    # Leave /firstboot in place here. Hardware test will remove it after
    # everything's OK.
except:
    pass

color = [0, 0, 0]

if check_row0():
    enable_mass_storage = True
    color[2] = 64

if check_row4():
    enable_hardware_test = True
    color[0] = 64

bootpixel[0] = tuple(color)

if enable_hardware_test:
    with open("/hardware_test", "w") as f:
        f.write("1")
else:
    try:
        os.remove("/hardware_test")
    except:
        pass

try:
    storage.remount("/", readonly=True)
except Exception as e:
    print(f"could not remount /: {e}")

if not enable_mass_storage:
    # Disable mass storage and USB serial.
    storage.disable_usb_drive()
    usb_cdc.disable()

while check_row0() or check_row4():
    time.sleep(0.01)

bootpixel[0] = (0, 0, 0)
bootpixel._sm.deinit()

row0.deinit()
row4.deinit()
col1.deinit()
col2.deinit()
col3.deinit()
