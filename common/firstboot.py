# SPDX-FileCopyrightText: 2025 Kodachi 6 14
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2025 Kodachi 6 14
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

import errno
import os
import storage

class FirstBoot:
    def __init__(self):
        pass

    def check(self) -> bool:
        # Is this, in fact, the first boot?
        try:
            open("/firstboot", "r")

            # Yup.
            return True
        except OSError as e:
            pass

        # Nope, not the first boot.
        return False

    def clear(self) -> bool:
        # Clear the firstboot flag.
        try:
            storage.remount("/", readonly=False)
        except Exception as e:
            print(f"FirstBoot: can't clear, error remounting /: {e}")
            return False

        rc = True

        try:
            os.remove("/firstboot")
        except Exception as e:
            if e.errno != errno.ENOENT:
                print(f"FirstBoot: can't clear, error removing /firstboot: {e} ")
                rc = False

        storage.remount("/", readonly=True)

        return rc
