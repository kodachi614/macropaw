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

import usb_cdc
import time

from politergb import PoliteRGB
from ringrgb import RingRGB

from macropaw import MacroPawKeyboard

from kmk.keys import KC
from kmk.extensions.rgb import AnimationModes
from kmk.extensions.media_keys import MediaKeys
from kmk.modules.usb_disconnect import USBDisconnect
from kmk.utils import Debug

debug = Debug(__name__)


def setup_macropaw(keyboard):
    rgb_matrix = PoliteRGB(pixel_pin=None, pixels=(keyboard.leds_matrix,),
                           animation_mode=AnimationModes.SWIRL,
                           animation_speed=2)
    rgb_matrix.set_rgb_fill(( 0, 0, 64 ))

    keyboard.extensions.append(rgb_matrix)
    keyboard.extensions.append(MediaKeys())

    key_AnimationCycle = KC.NO.clone()
    key_AnimationCycle.after_press_handler(rgb_matrix.next_animation)

    keyboard.keymap = [
        [
            KC.N1, KC.N2, KC.N3, KC.N4, KC.N5,
            KC.N6, KC.N7, KC.N8, KC.N9, KC.N0,
        ]
    ]

    keyboard.modules.append(USBDisconnect())


if __name__ == '__main__':
    if usb_cdc.console:
        debug.enabled = True
        print("Debugging enabled")

    hardware_test = False

    try:
        open("/hardware_test", "r")
        hardware_test = True
    except:
        pass

    keyboard = MacroPawKeyboard()
    print("KEYBOARD!")

    if hardware_test:
        print("Hardware test mode")

        from hardwaretest import setup_hardware_test
        setup_hardware_test(keyboard)
    else:
        setup_macropaw(keyboard)

    keyboard.go()
