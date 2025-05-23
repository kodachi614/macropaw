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

class HardwareTestRing:
    def __init__(self, callback, pixels):
        self.callback = callback
        self.pixels = pixels

        self.red = make_key(names=["HW_red"], on_press=self._red)
        self.green = make_key(names=["HW_green"], on_press=self._green)
        self.blue = make_key(names=["HW_blue"], on_press=self._blue)

        self._shown = [False, False, False]

    def _red(self, key, keyboard, *args):
        self.pixels.fill((64, 0, 0))
        self.shown(0)

    def _green(self, key, keyboard, *args):
        self.pixels.fill((0, 64, 0))
        self.shown(1)

    def _blue(self, key, keyboard, *args):
        if self._shown[2]:
            self.pixels.fill((0, 0, 0))
        else:
            self.pixels.fill((0, 0, 64))

        self.shown(2)

    def shown(self, i):
        self._shown[i] = True

        self.callback(all(self._shown))


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

        self.ring1_status = False
        self.ring2_status = False
        self.matrix_status = False

    def go(self):
        for color in [ (64, 0, 0), (0, 64, 0), (0, 0, 64) ]:
            self.keyboard.leds_ring1.fill(color)
            self.keyboard.leds_ring2.fill(color)
            self.keyboard.leds_matrix.fill(color)

            time.sleep(1)

        self.keyboard.leds_ring1.fill((16, 16, 16))
        self.keyboard.leds_ring2.fill((16, 16, 16))
        self.keyboard.leds_matrix.fill((16, 16, 16))

        ring1 = HardwareTestRing(self.ring1, self.keyboard.leds_ring1)
        ring2 = HardwareTestRing(self.ring2, self.keyboard.leds_ring2)
        matrix = HardwareTestMatrix(self.matrix, self.keyboard.leds_matrix)

        layer0 = [
            # Encoders: CCW, CW, button
            ring1.red, ring1.green, ring1.blue,
            ring2.red, ring2.green, ring2.blue,
        ] + matrix.keys

        self.keyboard.keymap = [ layer0 ]

    def ring1(self, status):
        self.ring1_status = status

        self.check_status()

    def ring2(self, status):
        self.ring2_status = status

        self.check_status()

    def matrix(self, status):
        self.matrix_status = status

        self.check_status()

    def check_status(self):
        if self.ring1_status and self.ring2_status and self.matrix_status:
            # All done. Kill all the lights...
            self.keyboard.leds_ring1.fill((0, 64, 0))
            self.keyboard.leds_ring2.fill((0, 64, 0))
            self.keyboard.leds_matrix.fill((0, 64, 0))

            # ...and clear firstboot.
            if self.firstboot.clear():
                print("Rebooting...")
                microcontroller.reset()
            else:
                self.keyboard.leds_ring1.fill((64, 0, 0))
                self.keyboard.leds_ring2.fill((64, 0, 0))
                self.keyboard.leds_matrix.fill((64, 0, 0))


def setup_hardware_test(debug, keyboard):
    runner = HardwareTestRunner(keyboard, FirstBoot())
    runner.go()
