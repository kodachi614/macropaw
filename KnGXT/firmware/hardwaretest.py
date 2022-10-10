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

import time

from kmk.keys import KC
from kmk.utils import Debug

debug = Debug(__name__)


class HardwareTestRing:
    def __init__(self, pixels):
        self.pixels = pixels

        self.red = KC.NO.clone()
        self.red.after_press_handler(self._red)

        self.green = KC.NO.clone()
        self.green.after_press_handler(self._green)

        self.blue = KC.NO.clone()
        self.blue.after_press_handler(self._blue)

    def _red(self, key, keyboard, *args):
        self.pixels.fill((64, 0, 0))

    def _green(self, key, keyboard, *args):
        self.pixels.fill((0, 64, 0))

    def _blue(self, key, keyboard, *args):
        self.pixels.fill((0, 0, 64))    


class HardwareTestMatrix:
    def __init__(self, pixels):
        self.pixels = pixels
        self.colors = [ (0, 0, 0), (64, 0, 0), (0, 64, 0), (0, 0, 64) ]
        self.indices = [ 0 ] * len(pixels)

        self.keys = [ KC.NO.clone() for i in range(len(pixels)) ]

        for i in range(len(pixels)):
            # This stupid idx=i business is how you do Python lambda
            # closures. I hate it.
            self.keys[i].after_press_handler(
                lambda key, keyboard, *args, idx=i: self._press(idx)
            )

    def _press(self, i):
        self.indices[i] = (self.indices[i] + 1) % len(self.colors)
        color = self.colors[self.indices[i]]
        self.pixels[i] = color


def setup_hardware_test(keyboard):
    for color in [ (64, 0, 0), (0, 64, 0), (0, 0, 64) ]:
        keyboard.leds_ring1.fill(color)
        keyboard.leds_ring2.fill(color)
        keyboard.leds_matrix.fill(color)
    
        time.sleep(1)

    keyboard.leds_ring1.fill((0, 0, 0))
    keyboard.leds_ring2.fill((0, 0, 0))
    keyboard.leds_matrix.fill((0, 0, 0))

    ring1 = HardwareTestRing(keyboard.leds_ring1)
    ring2 = HardwareTestRing(keyboard.leds_ring2)
    matrix = HardwareTestMatrix(keyboard.leds_matrix)

    layer0 = [
        # Encoders: CCW, CW, button
        ring1.red, ring1.green, ring1.blue,
        ring2.red, ring2.green, ring2.blue,
    ] + matrix.keys

    keyboard.keymap = [ layer0 ]
