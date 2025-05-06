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

from math import e, exp, pi, cos

from kmk.extensions.rgb import RGB, AnimationModes
from kmk.utils import Debug

debug = Debug(__name__)

class SimpleTimer:
    def __init__(self):
        self.count = 0
        self.ms = 0
        self.start = 0

    def __enter__(self):
        self.start = supervisor.ticks_ms()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.ms += supervisor.ticks_ms() - self.start
        self.count += 1

    def __str__(self):
        if self.count == 0:
            return "0 ms avg (0 runs)"
        else:
            avg = self.ms / self.count
            return "%.3d ms avg (%d run%s)" % (avg, self.count, "s" if self.count != 1 else "")


class MacroPawRGB(RGB):
    AnimationCycle = [
        AnimationModes.SWIRL, AnimationModes.BREATHING, AnimationModes.RAINBOW,
        AnimationModes.BREATHING_RAINBOW, AnimationModes.KNIGHT
    ]
    animation_index = 0

    def __init__(self, *args, **kwargs):
        new_kwargs = dict(**kwargs)

        self.coord_mapping = None

        if 'coord_mapping' in new_kwargs:
            self.coord_mapping = new_kwargs['coord_mapping']
            del new_kwargs['coord_mapping']

        if ((new_kwargs['animation_mode'] == AnimationModes.USER) and
            not 'user_animation' in new_kwargs):
            new_kwargs['user_animation'] = self.effect_breathmap
            print(f"MPRGB: init, supplied breathmap")

        super().__init__(*args, **new_kwargs)

        try:
            self.animation_index = self.AnimationCycle.index(self.animation_mode)
        except ValueError:
            self.animation_index = -1

        self.update_timer = SimpleTimer()
        self.animation_timer = SimpleTimer()
        self.rescale_timer = SimpleTimer()

    def during_bootup(self, sandbox):
        super().during_bootup(sandbox)

        self.max_key_usage = 0
        print(f"MPRGB: during_bootup, num_pixels {self.num_pixels}")
        self.key_usage = [ 0 ] * self.num_pixels
        self.refresh_count = 0
        self.rescale_count = 0

        # This is partly ripped off from KMK's effect_breathing (which seems
        # to have been at least partly inspired by the stuff in
        # https://thingpulse.com/breathing-leds-cracking-the-algorithm-behind-our-breathing-pattern/,
        # though KMK itself lists QMK and a 404'd link as sources?), but is
        # heavily heavily reworked by starting with exp(sin(theta)) as in the
        # post above, then playing with the Apple graphing calculator and
        # thinking about what I want.
        #
        # In particular, exp(sin(theta)) takes the sine curve and turns it
        # into a frankly pretty elegant curve that's not unlike the way a
        # breathing human doesn't exhale and inhale at the same rate. However,
        # some annoyances with that: if you let it directly drive brightness,
        # the LEDs will be dim more often than bright, so I wanted to flip it,
        # and also the sine curve starts and ends it cycles at 0, which is
        # great mathematically but puts the peak of the brightness cycle a
        # quarter of the way through the cycle, rather than halfway.
        #
        # So. My version uses cos(theta) to start the curve at 1. Since
        # cos(theta) ranges from -1 to 1, exp(cos(theta)) ranges from 1/e to
        # e, or e^-1 to e^1. Dividing that by e is easy (just do
        # exp(cos(theta) - 1)) for a range of e^-2 to e^0 or e^-2 to 1;
        # subtracting that from 1 starts us at 0 and ranges up to (1 - e^-2).
        # Dividing that by (1 - e^-2) gives us a range of 0 to 1.
        #
        # This is a lot of floating point, which can be annoying on an
        # embedded system. On the other hand, we can compute the divisor once,
        # then precompute all the exponentation and cosines, scaling theta to
        # range from 0 to 255 instead of 0 to 2*pi.

        start_ms = supervisor.ticks_ms()

        self.breath_table = []
        divisor = 1 - exp(-2)                       # As described above.

        for pos in range(256):
            theta = (pi * pos) / 128                # This is 2*pi*pos / 256.
            numerator = 1 - exp(cos(theta)-1)       # As described above.
            y = 1 - (numerator / divisor)
            self.breath_table.append(y)

        table_ms = supervisor.ticks_ms()

        # Default the coord_mapping if needed.
        if self.coord_mapping is None:
            self.coord_mapping = list(range(self.num_pixels))

        if len(self.coord_mapping) != self.num_pixels:
            print(f"MPRGB: coord_mapping {len(self.coord_mapping)} != num_pixels {self.num_pixels}")
            self.coord_mapping = list(range(self.num_pixels))

        # Invert the coordinate mapping for faster lookups.
        self.inv_coord_mapping = {}

        for i in range(len(self.coord_mapping)):
            c = self.coord_mapping[i]

            if c in self.inv_coord_mapping:
                print(f"MPRGB: coord_mapping {i} -> {c} already set to {self.inv_coord_mapping[c]}")

            self.inv_coord_mapping[c] = i

        end_ms = supervisor.ticks_ms()

        print(f"MPRGB: during_bootup, {len(self.breath_table)} entries in {table_ms - start_ms} ms, coord_mapping in {end_ms - table_ms} ms")

    def handle_update(self, update):
        with self.update_timer:
            key = update.key_number
            i = self.inv_coord_mapping.get(key, None)

            if i is not None:
                pressed = update.pressed

                # print(f"MPRGB: {key} {'pressed' if pressed else 'released'}, index {i}")

                if i < self.num_pixels:
                    if pressed:
                        self.key_usage[i] += 1
                        self.max_key_usage = max(self.max_key_usage, self.key_usage[i])

                        # print(f"MPRGB: pressed {key} ({self.key_usage[i]} / {self.max_key_usage})")
            #         else:
            #             print(f"MPRGB: released {key}, index {i}")
            else:
                print(f"MPRGB: {key} not in coord_mapping?")

    def effect_breathmap(self, parent):
        with self.animation_timer:
            for i in range(0, self.num_pixels):
                scaled = 0

                if self.key_usage[i] > 0:
                    # We're going to use the key usage to pick the maximum brightness for this
                    # key, from 128 to 255.
                    maxval = (127 * (self.key_usage[i] / self.max_key_usage)) + 128

                    # Then we use the animation position to curve that brightness, from 64 to
                    # maxval.
                    scaled = int(64 + (self.breath_table[self.pos] * (maxval - 64)) + 0.5)

                self.set_hsv(self.hue, self.sat, scaled, i)

            # Show final results
            self.disable_auto_write = False  # Resume showing changes
            self.show()

            # Finally, update the animation position.
            self.pos = (self.pos + self._step) % 256

        # Every second (more or less), we'll also rescale all the usages.
        self.refresh_count += 1

        if self.refresh_count >= self.refresh_rate:
            self.refresh_count = 0
            self.rescale_count += 1

            new_max = min(self.max_key_usage, 100)

            if new_max != self.max_key_usage:
                with self.rescale_timer:
                    # print(f"MPRGB: rescaling from {self.max_key_usage} to {new_max}: {' '.join([ str(x) for x in self.key_usage ])}")

                    for i in range(0, self.num_pixels):
                        old = self.key_usage[i]

                        if self.key_usage[i]:
                            s1 = ((self.key_usage[i] * new_max) + self.max_key_usage - 1) // self.max_key_usage
                            s2 = (s1 + 1) // 2

                            self.key_usage[i] = s2

                            if self.key_usage[i] < 1:
                                print("MPRGB: rescaling %d from %d got %d, forcing to 1" % (i, old, self.key_usage[i]))
                                self.key_usage[i] = 1

                            if self.key_usage[i] > self.max_key_usage:
                                print("MPRGB: rescaling %d from %d got %d, forcing to %d" % (i, old, self.key_usage[i], self.max_key_usage))
                                self.key_usage[i] = self.max_key_usage

                    self.max_key_usage = new_max // 2

                    # print(f"MPRGB: rescaled: {' '.join([ str(x) for x in self.key_usage ])}")
                # else:
                #     print(f"MPRGB: no rescaling needed")

        # # Every 10 (potential) rescales, dump the timers:
        # if self.rescale_count >= 10:
        #     self.rescale_count = 0
        #     print(f"MPRGB: updates   {self.update_timer}")
        #     print(f"MPRGB: animation {self.animation_timer}")
        #     print(f"MPRGB: rescales  {self.rescale_timer}")

    def after_matrix_scan(self, sandbox):
        if sandbox.matrix_update:
            self.handle_update(sandbox.matrix_update)

        if sandbox.secondary_matrix_update:
            self.handle_update(sandbox.secondary_matrix_update)

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
