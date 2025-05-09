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

import microcontroller
import time

from kmk.keys import make_key

from firstboot import FirstBoot


class HardwareTestMatrix:
    """
    Test the hardware of the keyswitch matrix. Every time a key is pressed,
    the LED in its row position gets red, and the LED in its column position
    gets blue. The test is complete when you've cycled through all the LEDs.
    """
    def __init__(self, callback, pixels):
        self.callback = callback
        self.pixels = pixels
        self.checked = [ False ] * 64  # 64 keys for a KnH0F

        self.keys = []

        for row in range(8):
            for col in range(8):
                # This stupid row=row, col=col business is how you do Python
                # lambda closures. I hate it.
                self.keys.append(
                    make_key(
                        names=[f"HW_matrix_R{row}_C{col}"],
                        on_press=lambda key, keyboard, *args, row=row, col=col: self._press(keyboard, row, col)
                    )
                )

    def _press(self, keyboard, row, col):
        idx = row * 8 + col

        status = "unpressed" if not self.checked[idx] else "pressed"

        print(f"Got {status} key R{row} C{col} => SW{idx+1}")

        self.checked[idx] = True

        for i in range(8):
            color = [0, 0, 0]
            if i == row:
                color[0] = 64

            if i == col:
                color[2] = 64

            self.pixels[i] = tuple(color)

        self.callback(all(self.checked))

        return keyboard

class HardwareTestRunner:
    def __init__(self, keyboard, firstboot):
        self.keyboard = keyboard
        self.firstboot = firstboot
        self.matrix_status = False

    def go(self):
        for color in [ (64, 0, 0), (0, 64, 0), (0, 0, 64), (16, 16, 16) ]:
            self.keyboard.leds_matrix.fill(color)

            time.sleep(1)

        print("Clearing LEDs...")
        self.keyboard.leds_matrix.fill((0, 0, 0))

        self.keyboard.keymap = [
            HardwareTestMatrix(self.matrix, self.keyboard.leds_matrix).keys
        ]

    def matrix(self, status):
        self.matrix_status = status

        self.check_status()

    def check_status(self):
        if self.matrix_status:
            # All done. Kill all the lights...
            self.keyboard.leds_matrix.fill((0, 64, 0))

            # ...and clear firstboot.
            if self.firstboot.clear():
                print("Rebooting...")
                microcontroller.reset()
            else:
                self.keyboard.leds_matrix.fill((64, 0, 0))


def setup_hardware_test(debug, keyboard):
    runner = HardwareTestRunner(keyboard, FirstBoot())
    runner.go()
