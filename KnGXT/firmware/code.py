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
    ring_color = (0, 0, 64) if debug.enabled else (0, 64, 0)

    rgb_ring1 = RingRGB(name="RING1", pixels=keyboard.leds_ring1)
    rgb_ring1.set_rgb_fill(ring_color)

    print("RING1")
    time.sleep(.25)

    rgb_ring2 = RingRGB(name="RING2", pixels=keyboard.leds_ring2)
    rgb_ring2.set_rgb_fill(ring_color)

    print("RING2")
    time.sleep(.25)

    rgb_matrix = PoliteRGB(pixel_pin=None, pixels=(keyboard.leds_matrix,),
                           animation_mode=AnimationModes.SWIRL,
                           animation_speed=4)
    rgb_matrix.set_rgb_fill(( 0, 0, 64 ))

    print("MATRIX")
    time.sleep(.25)

    keyboard.extensions.append(rgb_matrix)
    keyboard.extensions.append(rgb_ring1)
    keyboard.extensions.append(rgb_ring2)
    keyboard.extensions.append(MediaKeys())

    key_AnimationCycle = KC.NO.clone()
    key_AnimationCycle.after_press_handler(rgb_matrix.next_animation)

    key_VolDown = KC.VOLD.clone()
    key_VolDown.after_press_handler(rgb_ring1.inject_ccw)

    key_VolUp = KC.VOLU.clone()
    key_VolUp.after_press_handler(rgb_ring1.inject_cw)

    key_Mute = KC.MUTE.clone()
    key_Mute.after_press_handler(rgb_ring1.inject_fan)

    key_PrevTrack = KC.MRWD.clone()
    key_PrevTrack.after_press_handler(rgb_ring2.inject_ccw)

    key_NextTrack = KC.MFFD.clone()
    key_NextTrack.after_press_handler(rgb_ring2.inject_cw)

    key_Play = KC.MPLY.clone()
    key_Play.after_press_handler(rgb_ring2.inject_fan)

    keyboard.keymap = [
        [
            # Encoders: CCW, CW, button
            key_VolDown,   key_VolUp,          key_Mute,
            key_PrevTrack, key_NextTrack,      key_Play,

            # Main key matrix
            KC.RGB_AND,    key_AnimationCycle, KC.RGB_ANI,
            KC.N7,         KC.N8,              KC.N9,
            KC.N4,         KC.N5,              KC.N6,
            KC.N1,         KC.N2,              KC.N3,
            KC.SPACE,               KC.N0,
        ]
    ]

    keyboard.modules.append(USBDisconnect())


if __name__ == '__main__':

    from macropaw import Main


    Main(__name__, setup_macropaw)
