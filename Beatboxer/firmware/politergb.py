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

from kmk.extensions.rgb import RGB, AnimationModes
from kmk.utils import Debug

debug = Debug(__name__)

class MacroPawRGB(RGB):
    AnimationCycle = [
        AnimationModes.SWIRL, AnimationModes.BREATHING, AnimationModes.RAINBOW,
        AnimationModes.BREATHING_RAINBOW, AnimationModes.KNIGHT
    ]
    animation_index = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.animation_index = self.AnimationCycle.index(self.animation_mode)
        except ValueError:
            self.animation_index = -1

    def during_bootup(self, sandbox):
        super().during_bootup(sandbox)

    def next_animation(self, key, keyboard, *args):
        if self.animation_index >= 0:
            self.animation_index += 1
            self.animation_index %= len(self.AnimationCycle)
            self.animation_mode = self.AnimationCycle[self.animation_index]
            self.effect_init = True

    def _stop(self, color):
        self._saved_animation = self.animation_mode
        self.animation_mode = AnimationModes.STATIC_STANDBY
        self.set_rgb_fill(color)

    def _start(self, color):
        self.set_rgb_fill(color)
        self.animation_mode = self._saved_animation

    def on_powersave_enable(self, sandbox):
        # debug(f"{self}: powersave enabled")
        self._stop((0, 0, 0))
        return super().on_powersave_enable(sandbox)

    def on_powersave_disable(self, sandbox):
        # debug(f"{self}: powersave disabled")
        self._start((0, 0, 0))
        return super().on_powersave_disable(sandbox)
