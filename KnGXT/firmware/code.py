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



from kmk.extensions.rgb import AnimationModes
from kmk.modules.usb_disconnect import USBDisconnect




def setup_macropaw(debug, kbd):
    ring_color = (0, 0, 64) if debug.enabled else (0, 64, 0)
    kbd.setup_animation(ring_color=ring_color,
                        animation_mode=AnimationModes.BREATHING,
                        hue_default=128,
                        animation_speed=2)

    layers = Layers()
    layers.rgb = kbd.rgb_matrix

    kbd.modules.append(USBDisconnect())



    keyboard.keymap = [
        [
            # Encoders: CCW, CW, button
            kbd.KeyVolDown,    kbd.KeyVolUp,     kbd.KeyMute,
            kbd.KeyPrevTrack,  kbd.KeyNextTrack, kbd.KeyPlay,

            # Main key matrix
            KC.RGB_AND,    key_AnimationCycle, KC.RGB_ANI,
            KC.N7,         KC.N8,              KC.N9,
            KC.N4,         KC.N5,              KC.N6,
            KC.N1,         KC.N2,              KC.N3,
            KC.SPACE,               KC.N0,
        ]
    ]


if __name__ == '__main__':

    from macropaw import Main


    Main(__name__, setup_macropaw)
