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

import microcontroller
import time

from kmk.keys import make_key

from firstboot import FirstBoot


class HardwareTestMatrix:
    def __init__(self, callback, pixels):
        self.callback = callback
        self.pixels = pixels
        self.colors = [ (64, 0, 0), (0, 64, 0), (0, 0, 64), (0, 0, 0) ]
        self.last = len(self.colors) - 1
        self.indices = [ -1 ] * len(pixels)

        self.keys = []

        for i in range(len(pixels)):
            # This stupid idx=i business is how you do Python lambda
            # closures. I hate it.
            self.keys.append(
                make_key(
                    names=[f"HW_matrix_{i}"],
                    on_press=lambda key, keyboard, *args, idx=i: self._press(keyboard, idx)
                )
            )


    def _press(self, keyboard, i):
        self.indices[i] = self.indices[i] + 1

        if self.indices[i] > self.last:
            self.indices[i] = self.last

        color = self.colors[self.indices[i]]
        self.pixels[i] = color

        self.callback(all(map(lambda x: x == self.last, self.indices)))

        return keyboard

class HardwareTestRunner:
    def __init__(self, keyboard, firstboot):
        self.keyboard = keyboard
        self.firstboot = firstboot
        self.matrix_status = False

    def go(self):
        for color in [ (64, 0, 0), (0, 64, 0), (0, 0, 64) ]:
            self.keyboard.leds_matrix.fill(color)

            time.sleep(1)

        self.keyboard.leds_matrix.fill((16, 16, 16))

        self.keyboard.keymap = [
            HardwareTestMatrix(self.matrix, self.keyboard.leds_matrix).keys
        ]

    def matrix(self, status):
        self.matrix_status = status

        self.check_status()

    def check_status(self):
        if self.matrix_status:
            # All done. Kill all the lights...
            self.keyboard.leds_matrix.fill((0, 64, 0))

            # ...and clear firstboot.
            if self.firstboot.clear():
                print("Rebooting...")
                microcontroller.reset()
            else:
                self.keyboard.leds_matrix.fill((64, 0, 0))


def setup_hardware_test(debug, keyboard):
    runner = HardwareTestRunner(keyboard, FirstBoot())
    runner.go()
