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
from ringrgb import RingRGB
from keymapper import Keymapper

from kmk.keys import KC, Key, make_key
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
        super().__init__()

        # Pins to use when scanning keys
        self.col_pins = (board.COL0, board.COL1, board.COL2, board.COL3)
        self.row_pins = (board.ROW0, board.ROW1, board.ROW2, board.ROW3, board.ROW4)
        self.diode_orientation = DiodeOrientation.ROW2COL

        # self.allpixels is the underlying LED array of the hardware.
        self.allpixels = NeoPixelBackground(board.NEOPIXEL, 30, pixel_order="GRB", brightness=0.125)

        # The ordering of the LEDs in self.allpixels isn't really all that
        # useful, so we slice it up in a few different ways. First, the two
        # LED rings around the rotary encoders -- self.leds_ringX are slices
        # out of self.allpixels, and self.rgb_ringX are RingRGB objects to
        # support nicer animations for them.
        self.leds_ring1 = PixelSlice(self.allpixels, 8, 8)
        self.leds_ring2 = PixelSlice(self.allpixels, 0, 8)
        self.leds_matrix = PixelSlice(self.allpixels, 16, 14,
                                      mapping=[ 0, 5, 10,
                                                1, 6, 11,
                                                2, 7, 12,
                                                3, 8, 13,
                                                4, 9 ])

        self.extensions.append(MediaKeys())

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
        self.SwitchToDvorak = internal_key("SW_Dvorak", on_press=self.switch_to_Dvorak)
        self.SwitchToQWERTY = internal_key("SW_QWERTY", on_press=self.switch_to_QWERTY)

    def setup_animation(self, ring_color, **kwargs):
        self.rgb_ring1 = RingRGB(name="RING1", pixels=self.leds_ring1)
        self.rgb_ring1.set_rgb_fill(ring_color)

        self.rgb_ring2 = RingRGB(name="RING2", pixels=self.leds_ring2)
        self.rgb_ring2.set_rgb_fill(ring_color)

        # Explicitly hand in the coordinate mapping of the main matrix.
        self.rgb_matrix = MacroPawRGB(pixel_pin=None, pixels=(self.leds_matrix,),
                                      coord_mapping=[ 5,  6,  7,  9, 10, 11,
                                                     13, 14, 15, 17, 18, 19, 21, 22 ],
                                      **kwargs)
        self.rgb_matrix.set_rgb_fill(ring_color)

        time.sleep(0.25)

        self.extensions.append(self.rgb_matrix)
        self.extensions.append(self.rgb_ring1)
        self.extensions.append(self.rgb_ring2)

        self.KeyAnimationCycle = internal_key("NextAnim",
                                            on_press=self.rgb_matrix.next_animation)

        self.KeyVolDown = chained_key("KeyVolDown", KC.VOLD,
                                      on_press=self.rgb_ring1.inject_ccw)

        self.KeyVolUp = chained_key("KeyVolUp", KC.VOLU,
                                    on_press=self.rgb_ring1.inject_cw)

        self.KeyMute = chained_key("KeyMute", KC.MUTE,
                                   on_press=self.rgb_ring1.inject_fan)

        self.KeyPrevTrack = chained_key("KeyPrevTrack", KC.MRWD,
                                        on_press=self.rgb_ring2.inject_ccw)

        self.KeyNextTrack = chained_key("KeyNextTrack", KC.MFFD,
                                        on_press=self.rgb_ring2.inject_cw)

        self.KeyPlay = chained_key("KeyPlay", KC.MPLY,
                                   on_press=self.rgb_ring2.inject_fan)


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
