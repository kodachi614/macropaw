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

import adafruit_pixelbuf

class PixelSlice:
    def __init__(self, parent: adafruit_pixelbuf, offset: int, len: int, mapping=None):
        self.parent = parent
        self.offset = offset
        self.len = len

        self.mapping = mapping or list(range(self.len))

    def fill(self, color):
        # Don't worry about the order mapping here, since we're doing everything.
        self.parent[self.offset:self.offset+self.len] = [color] * self.len

    def show(self):
        self.parent.show()

    def __setitem__(self, k: int, v):
        if (k < 0) or (k >= self.len):
            raise KeyError(f"{k} is out of range [0, {self.len})")

        self.parent[self.mapping[k] + self.offset] = v

    def __getitem__(self, k: int):
        if (k < 0) or (k >= self.len):
            raise KeyError(f"{k} is out of range [0, {self.len})")

        return self.parent[self.mapping[k] + self.offset]

    def __len__(self):
        return self.len

    # def __iter__(self):
    #     yield from self.parent[self.offset:self.len]

    @property
    def auto_write(self):
        return self.parent.auto_write

    @property
    def bpp(self):
        return self.parent.bpp

    @property
    def brightness(self):
        return self.parent.brightness

    @property
    def byteorder(self):
        return self.parent.byteorder
