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
    The MacroPawKeyboard defines the bare-bones hardware of the MacroPaw:
    - 2 rotary encoders, each of which has a pushbutton as well
    - 14 keyswitches
    - 30 WS28128B RGB LEDs

    The rotary encoders are on board.RT1A, board.RT1B, board.RT2A, and board.RT2B.
    Unfortunately, the KnGXT boards have the A/B pins are backward and need pulldowns
    for the encoders to work properly. This will be fixed in the next revision.

    The keyswitches are on board.ROW0-4 and board.COL0-3. They're arranged as follows:

          COL0    COL1  COL2  COL3
    ROW0          Key0  Key1  Key2
    ROW1  Rotary1 Key3  Key4  Key5
    ROW2          Key6  Key7  Key8
    ROW3  Rotary2 Key9  Key10 Key11
    ROW4          Key12 Key13

    Note that the rotary encoder pushbuttons are mapped to the leftmost column of the
    main matrix. Also note that physically, Key13 is offset so that it takes a 2U
    keycap, but electrically, it's in column 2.

    The RGB LEDs are on board.NEOPIXEL. PAY CAREFUL ATTENTION TO THE LAYOUT BELOW:

           16 21 26
    8-15   17 22 27
           18 23 28
    0-7    19 24 29
           20  25

    0-7 are a ring around Rotary_2_; 8-15 are a ring around Rotary_1_. 16-29 are
    arranged with one LED per keyswitch, but row-major ordering rather than
    column-major ordering. This is because it makes the PCB layout much simpler.
    To cope with this, the MacroPawKeyboard class creates PixelSlices called
    leds_ring1 for the ring around Rotary1, leds_ring2 for the ring around Rotary2,
    and leds_matrix for a column-major slice of the matrix LEDs.

    If necessary, allpixels is the master Neopixel array. It's unlikely that this
    will be useful, though.
    """
    def __init__(self):
        self.col_pins = (board.COL0, board.COL1, board.COL2, board.COL3)
        self.row_pins = (board.ROW0, board.ROW1, board.ROW2, board.ROW3, board.ROW4)
        self.diode_orientation = DiodeOrientation.ROW2COL

        self.allpixels = NeoPixelBackground(board.NEOPIXEL, 30, pixel_order="GRB", brightness=0.125)

        self.leds_ring1 = PixelSlice(self.allpixels, 8, 8)
        self.leds_ring2 = PixelSlice(self.allpixels, 0, 8)
        self.leds_matrix = PixelSlice(self.allpixels, 16, 14,
                                      mapping=[ 0, 5, 10,
                                                1, 6, 11,
                                                2, 7, 12,
                                                3, 8, 13,
                                                4, 9 ])

        # create and register the scanners
        self.matrix = [
            RotaryioEncoder(
                pin_a=board.RT1B,
                pin_b=board.RT1A,
                pull="down",
                divisor=4,
            ),
            RotaryioEncoder(
                pin_a=board.RT2B,
                pin_b=board.RT2A,
                pull="down",
                divisor=4,
            ),
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
            # Rotary 1: top left of the board, pushbutton in the main matrix
            0, 1, 8,

            # Rotary 2: middle left of the board, pushbutton in the main matrix
            2, 3, 16,

            # Main matrix: right side of the board
            # The leftmost column is where the rotary encoder pushbuttons
            # get mapped, so it doesn't appear here.
            5,  6,  7,
            9,  10, 11,
            13, 14, 15,
            17, 18, 19,
            21,   22,
        ]



def Main(name, user_setup):
    debug = Debug(name)

    hardware_test = False

    try:
        open("/hardware_test", "r")
        hardware_test = True
    except:
        pass

    keyboard = MacroPawKeyboard()

    if hardware_test:
        from hardwaretest import setup_hardware_test

        print("Hardware test mode")

        setup_hardware_test(debug, keyboard)
    else:
        user_setup(debug, keyboard)

    keyboard.go()
