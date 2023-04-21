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

import board

from adafruit_neopixelbackground import NeoPixelBackground
from pixelslice import PixelSlice

from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners import DiodeOrientation
from kmk.scanners.encoder import RotaryioEncoder
from kmk.scanners.keypad import MatrixScanner

class MacroPawKeyboard(KMKKeyboard):
    """
    The MacroPawKeyboard defines the bare-bones hardware of the MacroPaw KnGYT,
    which is to say 10 keyswitches and 10 WS28128B-compatible RGB LEDs.

    The keyswitches are on board.ROW0-1 and board.COL0-4. They're arranged as follows:

          COL0  COL1  COL2  COL3  COL4
    ROW0  Key1  Key2  Key3  Key4  Key5
    ROW1  Key6  Key7  Key8  Key9  Key10

    The RGB LEDs are connected to board.NEOPIXEL, and while the labels of the LEDs
    match the keys they're next to, the wiring is a zig-zag pattern:

    NP1 -> NP6 -> NP7 -> NP2 -> NP3 -> NP8 -> NP9 -> NP4 -> NP5 -> NP10

    because that makes the PCB layout much simpler.

    The MacroPawKeyboard class for the KnGYT creates a PixelSlice called leds_matrix
    mapped in logical order, such that leds_matrix[0] is NP1, leds_matrix[1] is NP2,
    etc. The NeoPixelBackground object allpixels has all the LEDs in _keyswitch_ order.
    You'll probably never use that.
    """
    def __init__(self):
        self.col_pins = (board.COL0, board.COL1, board.COL2, board.COL3, board.COL4)
        self.row_pins = (board.ROW0, board.ROW1)
        self.diode_orientation = DiodeOrientation.ROW2COL

        self.allpixels = NeoPixelBackground(board.NEOPIXEL, 10, pixel_order="GRB",
                                            brightness=0.125)

        self.leds_matrix = PixelSlice(self.allpixels, 0, 10,
                                      mapping=[ 0, 3, 4, 7, 8,
                                                1, 2, 5, 6, 9 ])

        # create and register the scanners
        self.matrix = [
            MatrixScanner(
                # required arguments:
                column_pins = self.col_pins,
                row_pins = self.row_pins,
                columns_to_anodes=self.diode_orientation,
                # optional arguments with defaults:
                interval=0.02,
                max_events=64
            )
        ]

        # NOQA
        # flake8: noqa
        self.coord_mapping = [
            0, 1, 2, 3, 4,
            5, 6, 7, 8, 9
        ]
