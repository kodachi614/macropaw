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


class HardwareTestMatrix:
    def __init__(self, pixels):
        self.pixels = pixels
        self.colors = [ (32, 32, 32), (64, 0, 0), (0, 64, 0), (0, 0, 64), (0, 0, 0) ]
        self.indices = [ 0 ] * len(pixels)

        self.keys = [ KC.NO.clone() for i in range(len(pixels)) ]

        for i in range(len(pixels)):
            # This stupid idx=i business is how you do Python lambda
            # closures. I hate it.
            self.keys[i].after_press_handler(
                lambda key, keyboard, *args, idx=i: self._press(idx)
            )

            self.pixels[i] = self.colors[0]

    def _press(self, i):
        self.indices[i] = (self.indices[i] + 1) % len(self.colors)
        color = self.colors[self.indices[i]]
        self.pixels[i] = color


def setup_hardware_test(keyboard):
    matrix = HardwareTestMatrix(keyboard.leds_matrix)

    keyboard.keymap = [ matrix.keys ]
