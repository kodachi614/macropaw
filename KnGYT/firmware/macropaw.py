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
import usb_cdc
import time
import supervisor

from adafruit_neopixelbackground import NeoPixelBackground
from pixelslice import PixelSlice

from politergb import PoliteRGB
from ringrgb import RingRGB
from keymapper import Keymapper

from kmk.keys import KC
from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners import DiodeOrientation
from kmk.scanners.encoder import RotaryioEncoder
from kmk.scanners.keypad import MatrixScanner
from kmk.extensions.media_keys import MediaKeys
from kmk.utils import Debug


# Debugging assistance: log when something happens. This is a barebones
# trace facility, basically.

times = [ ( supervisor.ticks_ms(), "macropaw.py start" ) ]

def log_time(name, ms=None):
    if ms is None:
        ms = supervisor.ticks_ms()

    times.append( ( ms, name ) )

def dump_times():
    prev_time = None

    for ms, name in sorted(times):
        if prev_time is None:
            prev_time = ms

        delta_s = (ms - prev_time) / 1000

        print("%8.3fs %s" % (delta_s, name))


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
        # Pins to use when scanning keys
        self.col_pins = (board.COL0, board.COL1, board.COL2, board.COL3, board.COL4)
        self.row_pins = (board.ROW0, board.ROW1)
        self.diode_orientation = DiodeOrientation.ROW2COL

        # self.allpixels is the underlying LED array of the hardware.
        self.allpixels = NeoPixelBackground(board.NEOPIXEL, 10, pixel_order="GRB",
                                            brightness=0.125)

        # The ordering of the LEDs in self.allpixels isn't really all that
        # useful, so we create self.leds_matrix with a better ordering.
        self.leds_matrix = PixelSlice(self.allpixels, 0, 10,
                                      mapping=[ 0, 3, 4, 7, 8,
                                                1, 2, 5, 6, 9 ])

        self.extensions.append(MediaKeys())

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

    def switch_to_Dvorak(self, key, keyboard, *args):
        self.switch_to("Dvorak")

    def switch_to_QWERTY(self, key, keyboard, *args):
        self.switch_to("QWERTY")

    def switch_to(self, keymap):
        status, msg = Keymapper.switch_to(keymap)

        flashcolor = (0, 64, 0)

        if status:
            # The switch went OK.
            if msg != "OK":
                # Something weird still happened, though.
                flashcolor = (0, 0, 64)
                print(f"Map switch to {keymap} OK, but: {msg}")
        else:
            # Didn't work.
            flashcolor = (64, 0, 0)
            print(f"Map switch to {keymap} failed: {msg}")

        self.rgb_matrix.set_rgb_fill((0, 0, 0))
        time.sleep(0.25)
        self.rgb_matrix.set_rgb_fill(flashcolor)
        time.sleep(0.25)

        if status:
            supervisor.reload()

    def setup_mapswitchers(self):
        # Keys to switch to a different keymap
        self.SwitchToDvorak = KC.NO.clone()
        self.SwitchToDvorak.after_press_handler(self.switch_to_Dvorak)

        self.SwitchToQWERTY = KC.NO.clone()
        self.SwitchToQWERTY.after_press_handler(self.switch_to_QWERTY)

    def setup_animation(self, ring_color, **kwargs):
        self.rgb_matrix = PoliteRGB(pixel_pin=None, pixels=(self.leds_matrix,), **kwargs)
        self.rgb_matrix.set_rgb_fill(ring_color)

        time.sleep(0.25)

        self.extensions.append(self.rgb_matrix)

        self.KeyAnimationCycle = KC.NO.clone()
        self.KeyAnimationCycle.after_press_handler(self.rgb_matrix.next_animation)


def Main(name, user_setup):
    log_time("Main start")

    debug = Debug(name)

    log_time("Debug")

    # if usb_cdc.console:
    #     debug.enabled = True
    #     print("Debugging enabled")

    hardware_test = False

    try:
        open("/hardware_test", "r")
        hardware_test = True
    except:
        pass

    log_time("Check /hardware_test")

    keyboard = MacroPawKeyboard()

    log_time("MacroPawKeyboard")

    if hardware_test:
        from hardwaretest import setup_hardware_test

        log_time("import hardwaretest")

        print("Hardware test mode")

        setup_hardware_test(debug, keyboard)

        log_time("setup_hardware_test")
    else:
        user_setup(debug, keyboard)
        log_time("user_setup")

    log_time("Main end")
    dump_times()

    keyboard.go()
