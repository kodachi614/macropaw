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

from macropawrgb import MacroPawRGB

from kmk.extensions.rgb import AnimationModes
from kmk.utils import Debug

debug = Debug(__name__)


class RingElement:
    def __init__(self, direction, position, pos_limit, neg_limit, color):
        self.direction = direction
        self.position = position
        self.positive_limit = pos_limit or  99999999
        self.negative_limit = neg_limit or -99999999
        self.color = color

    def __bool__(self):
        return (self.position < self.positive_limit) and (self.position > self.negative_limit)

    def __str__(self):
        return "<El %X> @%d moving %d" % (id(self), self.position, self.direction)


class RingRGB(MacroPawRGB):
    def __init__(self, *args, name=None, pixels=None, tail=3, **kwargs):
        super().__init__(*args,
                         pixel_pin=None, pixels=(pixels,),
                         user_animation=self._animate,
                         animation_mode=AnimationModes.USER,
                         animation_speed=1,
                         **kwargs)
        self._name = name
        self._pixels = pixels
        self._elements = []
        self._tail = tail

        if self._debug:
            debug("RingRGB: pixels: %s, tail: %s" % (self.num_pixels, self._tail))

    def during_bootup(self, sandbox):
        self.set_rgb_fill((0, 0, 0))
        return super().during_bootup(sandbox)

    def _add_element(self, direction):
        el = None

        if len(self._elements) > 4:
            self._elements.pop(0)

        if direction == -1:
            el = RingElement(direction, self.num_pixels - 1,
                             None,                         (-1 * self._tail) - 1,
                             (64, 0, 0))
        elif direction == 1:
            el = RingElement(direction, 0,
                             self.num_pixels + self._tail, None,
                             (0, 64, 0))
        else:
            raise Exception("direction must either 1 or -1")

        if self._debug:
            debug(f"RingRGB: append {el}")

        self._elements.append(el)

    def inject_cw(self, key, keyboard, *args):
        self._add_element(1)

    def inject_ccw(self, key, keyboard, *args):
        self._add_element(-1)

    def inject_fan(self, key, keyboard, *args):
        if (self.num_pixels % 2) == 0:
            # Even number of pixels. Use the middle two.
            p1 = (self.num_pixels // 2) - 1
            p2 = p1 + 1
        else:
            # Odd number of pixels. Use the middle one.
            p1 = self.num_pixels // 2
            p2 = p1


        self._elements.append(RingElement(-1, p1,
                                          None,                         (-1 * self._tail) - 1,
                                          (0, 0, 64)))
        self._elements.append(RingElement( 1, p2,
                                          self.num_pixels + self._tail, None,
                                          (0, 0, 64)))

    def handle_update(self, update):
        pass

    @staticmethod
    def _animate(self):
        if not self._elements:
            return

        # Is it time to step?
        if self._step < 1.0:
            return

        # Disable automatic updates, and clear the array.
        self.disable_auto_write = True

        frame = [[0, 0, 0]] * self.num_pixels
        still_active = []

        if self._debug:
            debug(f"STEP: element count {len(self._elements)}")

        while self._step >= 1.0:
            for element in self._elements:
                if self._debug:
                    debug(f"  {element}:")

                p = element.position

                for i in range(3):
                    if (p >= 0) and (p < self.num_pixels):
                        prev = frame[p]
                        updated = [
                            prev[0] + (element.color[0] >> i),
                            prev[1] + (element.color[1] >> i),
                            prev[2] + (element.color[2] >> i)
                        ]

                        if self._debug:
                            debug(f"    pixel {p} {prev} => {updated}")

                        frame[p] = updated

                    p -= element.direction

                element.position += element.direction

                if element:
                    still_active.append(element)
                else:
                    if self._debug:
                        debug(f"  drop {element}")

            self._step -= 1.0

        if self._debug:
            debug(f"frame: {frame}")

        for i, updated in enumerate(frame):
            self.set_rgb(updated, i)

        self._elements = still_active
        self.disable_auto_write = False
        self.show()
