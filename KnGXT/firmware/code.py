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
from kmk.modules.layers import Layers as _Layers
from kmk.modules.holdtap import HoldTap

#### USE THIS TO PICK YOUR KEYMAP ####
# An annoying thing about keyboards is that you have to match up with
# the keymap being used on the OS side. We look at the "/keymap" file
# to choose a Keymapper ("QWERTY" or "Dvorak") from keymapper.py. If
# the file isn't present or has an invalid map, we default to QWERTY.
#
# You can define your own in keymapper.py if you want to.

from keymapper import FSKeymapper as KC

# Layers is here to change the LED matrix color depending on what layer
# is active. This isn't necessarily the best way to do this, mind you.
class Layers(_Layers):
    last_top_layer = 0
    hues = [128, 0, 64, 96]
    rgb = None

    def after_hid_send(self, kbd):
        if self.rgb is not None:
            if kbd.active_layers[0] != self.last_top_layer:
                self.last_top_layer = kbd.active_layers[0]
                self.rgb.hue = self.hues[self.last_top_layer]


def setup_macropaw(debug, kbd):
    ring_color = (0, 0, 64) if debug.enabled else (0, 64, 0)
    kbd.setup_animation(ring_color=ring_color,
                        animation_mode=AnimationModes.BREATHING,
                        hue_default=128,
                        animation_speed=2)

    layers = Layers()
    layers.rgb = kbd.rgb_matrix

    kbd.modules.append(HoldTap())
    kbd.modules.append(layers)
    kbd.modules.append(USBDisconnect())

    # DaVinci Resolve keybindings
    key_PrevMark = KC.LSFT(KC.UP)
    key_NextMark = KC.LSFT(KC.DOWN)
    key_PrevEdit = KC.UP
    key_NextEdit = KC.DOWN
    key_PlayReverse = KC.J
    key_PlayForward = KC.L
    key_PlayPause = KC.SPACE
    key_MarkIn = KC.I
    key_Mark = KC.M
    key_MarkOut = KC.O
    key_Razor = KC.LGUI(KC.B)
    key_RippleDelete = KC.LSFT(KC.LGUI(KC.X))
    key_Cut = KC.LGUI(KC.X)
    key_PrevFrame = KC.LEFT
    key_NextFrame = KC.RIGHT
    key_Undo = KC.LGUI(KC.Z)
    key_Redo = KC.LSFT(KC.LGUI(KC.Z))
    key_Save = KC.LGUI(KC.S)
    key_None = KC.NO

    key_PlusMinus = KC.HT(KC.PLUS, KC.MINUS)
    key_StarSlash = KC.HT(KC.ASTERISK, KC.SLASH)
    key_PeriodEqual = KC.HT(KC.DOT, KC.EQUAL)
    key_SevenOrParen = KC.HT(KC.N7, KC.LEFT_PAREN)
    key_NineOrParen = KC.HT(KC.N9, KC.RIGHT_PAREN)
    key_EightOrBS = KC.HT(KC.N8, KC.BSPC)

    kbd.keymap = [
        # 0: Function key layer (default)
        [
            # Encoders: CCW, CW, button
            kbd.KeyVolDown,    kbd.KeyVolUp,     kbd.KeyMute,
            kbd.KeyPrevTrack,  kbd.KeyNextTrack, kbd.KeyPlay,

            # Main key matrix
            KC.F1,             KC.F2,            KC.F3,
            KC.F4,             KC.F5,            KC.F6,
            KC.F7,             KC.F8,            KC.F9,
            KC.F10,            KC.F11,           KC.F12,
            KC.F13,                KC.LT(1, KC.F14),
        ],

        # 1: Layer-switching layer
        [
            # Encoders: CCW, CW, button
            KC.NO,             KC.NO,            KC.NO,
            KC.NO,             KC.NO,            KC.NO,

            # Main key matrix
            KC.NO,             KC.NO,            KC.NO,
            KC.NO,             KC.NO,            KC.NO,
            KC.NO,             KC.NO,            KC.NO,
            KC.TO(2),          KC.TO(3),         KC.NO,
            KC.TO(0),              KC.NO,
        ],

        # 2: Da Vinci Resolve layer
        [
            # Encoders: CCW, CW, button
            key_PrevMark,      key_NextMark,     key_Mark,
            key_PlayReverse,   key_PlayForward,  key_PlayPause,

            # Main key matrix
            key_PrevEdit,      key_Mark,         key_NextEdit,
            key_Razor,         key_RippleDelete, key_Cut,
            key_PrevFrame,     key_MarkIn,       key_NextFrame,
            key_Undo,          key_MarkOut,      key_Redo,
            key_None,              KC.LT(1, key_Save),
        ],

        # 3: Number pad layer
        [
            # Encoders: CCW, CW, button
            kbd.KeyVolDown,    kbd.KeyVolUp,     kbd.KeyMute,
            kbd.KeyPrevTrack,  kbd.KeyNextTrack, kbd.KeyPlay,

            # Main key matrix
            key_SevenOrParen,  key_EightOrBS,    key_NineOrParen,
            KC.N4,             KC.N5,            KC.N6,
            KC.N1,             KC.N2,            KC.N3,
            key_PeriodEqual,   KC.N0,            key_StarSlash,
            key_PlusMinus,         KC.LT(1, KC.ENTER),
        ]
    ]


if __name__ == '__main__':

    from macropaw import Main


    Main(__name__, setup_macropaw)
