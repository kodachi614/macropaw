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

from macropawrgb import MacroPawRGB
from keymapper import Keymapper

from kmk.keys import KC, Key, make_key
from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners import DiodeOrientation
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


def internal_key(name, on_press=None, on_release=None) -> Key:
    """
    A Key is the KMK representation of a key on the keyboard. internal_key
    creates a Key with a name and optional press/release handlers that doesn't
    do anything except call the handlers -- so it doesn't actually send any
    keycodes to the host. This is useful for keys that are used to control
    things about the keyboard itself, like switching layers, keymaps, or
    animations.

    For a key that needs to send a keycode, see chained_key.
    """
    return make_key(names=[name], on_press=on_press, on_release=on_release)

def chained_key(name, original_key, on_press=None, on_release=None) -> Key:
    """
    A Key is the KMK representation of a key on the keyboard. chained_key
    takes some existing Key and creates a new Key that does exactly what that
    key does, but calls the given press/release handlers after the existing
    Key's press/release handlers.

    This is useful for keys that _do_ need to send a keycode, but that also
    need to mess with the state of the keyboard itself, like sending "Volume
    Up" but _also_ triggering an animation.

    Really this should be built into KMK...
    """

    def __press_handler(key, keyboard, kc, coord_int):
        original_key.on_press(keyboard, coord_int)

        if on_press is not None:
            on_press(key, keyboard, kc, coord_int)

    def __release_handler(key, keyboard, kc, coord_int):
        original_key.on_release(keyboard, coord_int)

        if on_release is not None:
            on_release(key, keyboard, kc, coord_int)

    return make_key(names=[name], on_press=__press_handler, on_release=__release_handler)


class MacroPawKeyboard(KMKKeyboard):
    """
    The MacroPawKeyboard defines the bare-bones hardware of the MacroPaw
    Beatboxer KnH0F, which is to say 64 keyswitches and 8 WS28128B-compatible
    RGB LEDs.

    The keyswitches are on board.ROW0-7 and board.COL0-7. They're arranged in
    an 8x8 matrix.

          COL0  COL1  COL2  COL3  COL4  COL5  COL6  COL7
    ROW0  Key1  Key2  Key3  Key4  Key5  Key6  Key7  Key8
    ROW1  Key9  Key10 Key11 Key12 Key13 Key14 Key15 Key16
    ROW2  Key17 Key18 Key19 Key20 Key21 Key22 Key23 Key24
    ROW3  Key25 Key26 Key27 Key28 Key29 Key30 Key31 Key32
    ROW4  Key33 Key34 Key35 Key36 Key37 Key38 Key39 Key40
    ROW5  Key41 Key42 Key43 Key44 Key45 Key46 Key47 Key48
    ROW6  Key49 Key50 Key51 Key52 Key53 Key54 Key55 Key56
    ROW7  Key57 Key58 Key59 Key60 Key61 Key62 Key63 Key64

    The RGB LEDs are connected to board.NEOPIXEL. Since there are only eight
    of them, they obviously aren't next to the keys: instead, they're set up
    in a 4x2 grid on the left side of the keyboard, as a debugging aid:

    NP1 -> NP2 -> NP3 -> NP4 ->
    NP5 -> NP6 -> NP7 -> NP8

    The MacroPawKeyboard class for the KnH0F creates a NeoPixelBackground
    object called leds_matrix for the LEDs. (Unlike most of the other
    MacroPaws, we don't need to use a PixelSlice because the electrical
    order matches the logical order.)
    """
    def __init__(self):
        super().__init__()

        # Pins to use when scanning keys
        self.col_pins = (board.COL0, board.COL1, board.COL2, board.COL3,
                         board.COL4, board.COL5, board.COL6, board.COL7)
        self.row_pins = (board.ROW0, board.ROW1, board.ROW2, board.ROW3,
                         board.ROW4, board.ROW5, board.ROW6, board.ROW7)
        self.diode_orientation = DiodeOrientation.ROW2COL

        # self.allpixels is the underlying LED array of the hardware.
        self.leds_matrix = NeoPixelBackground(board.NEOPIXEL, 8, pixel_order="GRB",
                                              brightness=0.125)

        # self.extensions.append(MediaKeys())

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

        # Nothing fancy about the coordinate mapping for the KnH0F, it's
        # just linear.
        self.coord_mapping = list(range(64))

    # def switch_to_Dvorak(self, key, keyboard, *args):
    #     self.switch_to("Dvorak")

    # def switch_to_QWERTY(self, key, keyboard, *args):
    #     self.switch_to("QWERTY")

    # def switch_to(self, keymap):
    #     status, msg = Keymapper.switch_to(keymap)

    #     flashcolor = (0, 64, 0)

    #     if status:
    #         # The switch went OK.
    #         if msg != "OK":
    #             # Something weird still happened, though.
    #             flashcolor = (0, 0, 64)
    #             print(f"Map switch to {keymap} OK, but: {msg}")
    #     else:
    #         # Didn't work.
    #         flashcolor = (64, 0, 0)
    #         print(f"Map switch to {keymap} failed: {msg}")

    #     self.rgb_matrix.set_rgb_fill((0, 0, 0))
    #     time.sleep(0.25)
    #     self.rgb_matrix.set_rgb_fill(flashcolor)
    #     time.sleep(0.25)

    #     if status:
    #         supervisor.reload()

    def setup_mapswitchers(self):
        pass
        # # Keys to switch to a different keymap
        # self.SwitchToDvorak = internal_key("SW_Dvorak", on_press=self.switch_to_Dvorak)
        # self.SwitchToQWERTY = internal_key("SW_QWERTY", on_press=self.switch_to_QWERTY)

    def setup_animation(self, ring_color, **kwargs):
        self.rgb_matrix = MacroPawRGB(pixel_pin=None, pixels=(self.leds_matrix,), **kwargs)
        self.rgb_matrix.set_rgb_fill(ring_color)

        time.sleep(0.25)

        self.extensions.append(self.rgb_matrix)

        self.KeyAnimationCycle = internal_key("NextAnim",
                                            on_press=self.rgb_matrix.next_animation)


def Main(name, user_setup):
    log_time("Main start")

    debug = Debug(name)

    log_time("Debug")

    if False and usb_cdc.console:
        debug.enabled = True
        print("Debugging enabled")

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
