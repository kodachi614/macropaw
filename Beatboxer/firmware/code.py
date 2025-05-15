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

import supervisor

boot_time = supervisor.ticks_ms()

from kmk.extensions.rgb import AnimationModes
# from kmk.modules.usb_disconnect import USBDisconnect
# from kmk.modules.layers import Layers as _Layers
# from kmk.modules.holdtap import HoldTap

from macropaw import log_time

log_time(f"code.py start", boot_time)
log_time(f"code.py imports done")

#### USE THIS TO PICK YOUR KEYMAP ####
# An annoying thing about keyboards is that you have to match up with
# the keymap being used on the OS side. We look at the "/keymap" file
# to choose a Keymapper ("QWERTY" or "Dvorak") from keymapper.py. If
# the file isn't present or has an invalid map, we default to QWERTY.
#
# You can define your own in keymapper.py if you want to.

from keymapper import FSKeymapper as KC

log_time(f"import FSKeymapper (got {KC.__class__.__name__})")

def LS(key):
    return KC.LSFT(key)

def setup_macropaw(debug, kbd):
    kbd.setup_animation(ring_color=(0,0,0),
                        animation_mode=AnimationModes.BREATHING,
                        hue_default=128,
                        val_default=64,
                        animation_speed=2)

    kbd.setup_mapswitchers()

    kbd.keymap = [
        # 0: Main layer (default)
        [
            KC.A,     KC.B,     KC.C,     KC.D,     KC.E,     KC.F,     KC.G,     KC.H,
            KC.I,     KC.J,     KC.K,     KC.L,     KC.M,     KC.N,     KC.O,     KC.P,
            KC.Q,     KC.R,     KC.S,     KC.T,     KC.U,     KC.V,     KC.W,     KC.X,

            LS(KC.A), LS(KC.B), LS(KC.C), LS(KC.D), LS(KC.E), LS(KC.F), LS(KC.G), LS(KC.H),
            LS(KC.I), LS(KC.J), LS(KC.K), LS(KC.L), LS(KC.M), LS(KC.N), LS(KC.O), LS(KC.P),
            LS(KC.Q), LS(KC.R), LS(KC.S), LS(KC.T), LS(KC.U), LS(KC.V), LS(KC.W), LS(KC.X),

            KC.N0,    KC.N1,    KC.N2,    KC.N3,    KC.N4,    KC.N5,    KC.N6,    KC.N7,
            KC.MINUS, KC.EQUAL, KC.DOT,   KC.COMMA, KC.SLASH, KC.SCLN,  KC.SPACE, KC.ENTER,
        ],
    ]


if __name__ == '__main__':
    log_time("main start")

    from macropaw import Main

    log_time("import Main")

    Main(__name__, setup_macropaw)
