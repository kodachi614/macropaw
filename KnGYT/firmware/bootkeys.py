# SPDX-FileCopyrightText: 2025 Kodachi 6 14
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2025 Kodachi 6 14
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

# BootKeys handles checking for key combinations that trigger special boot
# modes. For the KnGYT:
#
# - If you hold down the left- & right-most keys on the bottom row, you get
#   hardware test mode.
# - If you hold down the left- & right-most keys on the top row, you get mass
#   storage.

import digitalio
import board
import time

from adafruit_neopixelbackground import NeoPixelBackground


class BootKeys:
    def __init__(self):
        # We're not going to do a matrix scan, but we still need to drive
        # rows and read columns to check for the special keys.
        self.row0 = digitalio.DigitalInOut(board.ROW0)
        self.row0.direction = digitalio.Direction.OUTPUT

        self.row1 = digitalio.DigitalInOut(board.ROW1)
        self.row1.direction = digitalio.Direction.OUTPUT

        self.col0 = digitalio.DigitalInOut(board.COL0)
        self.col0.direction = digitalio.Direction.INPUT

        self.col4 = digitalio.DigitalInOut(board.COL4)
        self.col4.direction = digitalio.Direction.INPUT

        # Finally, we use the first pixel to indicate if you're doing anything
        # special during boot. We use an array of R, G, B values to make it
        # easy to play with the individual elements.a
        self.bootpixel = NeoPixelBackground(board.NEOPIXEL, 1, pixel_order="GRB",
                                            brightness=0.125)
        self.color = [0, 0, 0]
        self.show()

    def show(self):
        self.bootpixel.fill(self.color)
        self.bootpixel.show()

    def check_row0(self) -> bool:
        rc = False
        self.row0.value = True

        if self.col0.value and self.col4.value:
            rc = True

        self.row0.value = False

        return rc

    def check_row1(self) -> bool:
        rc = False

        self.row1.value = True

        if self.col0.value and self.col4.value:
            rc = True

        self.row1.value = False

        return rc

    def check_mass_storage(self) -> bool:
        rc = self.check_row0()

        if rc:
            # Mass storage is enabled, so add blue to our pixel color.
            self.color[2] = 64
            self.show()

        return rc

    def check_hardware_test(self) -> bool:
        rc = self.check_row1()

        if rc:
            # Hardware test is enabled, so add red to our pixel color.
            self.color[0] = 64
            self.show()

        return rc

    def wait_for_release(self):
        while self.check_row0() or self.check_row1():
            time.sleep(0.01)

    def deinit(self):
        self.row0.deinit()
        self.row1.deinit()
        self.col0.deinit()
        self.col4.deinit()

        # Deinit the boot pixel.
        self.color = [0, 0, 0]
        self.show()
        self.bootpixel._sm.deinit()
