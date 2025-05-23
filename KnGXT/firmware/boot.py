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

# CircuitPython's supervisor will use the RGBs to signal very low-level
# status, but if we leave the brightness at the default of 255, it's
# pretty blinding. Crank that down.
supervisor.runtime.rgb_status_brightness = 16

import board

from firstboot import FirstBoot
from bootmanager import BootManager, TriggerRowCombo

# Start by assuming that nothing special is going on.
enable_hardware_test = False
enable_mass_storage = False

firstboot = FirstBoot()

# Use the first LED ring for boot status.
bootmgr = BootManager(8,
    # Mass storage: hold down the left- & rightmost keys on the top row.
    TriggerRowCombo(board.ROW0, board.COL1, board.COL3),

    # Hardware test: hold down the left- & rightmost keys on the bottom row.
    # COL2 is NOT A TYPO: the rightmost key on the bottom row is the 2U key.
    TriggerRowCombo(board.ROW4, board.COL1, board.COL2),
)

if firstboot.check():
    # First boot. Enable hardware test mode.
    enable_hardware_test = True

# Next up, check key combinations. The BootManager will also handle using the
# LEDs to indicate what mode you're in.

if bootmgr.check_mass_storage():
    enable_mass_storage = True

if bootmgr.check_hardware_test():
    enable_hardware_test = True

# Actually take action on the special modes.
bootmgr.set_hardware_test(enable_hardware_test)
bootmgr.set_mass_storage(enable_mass_storage, enable_hardware_test)

bootmgr.wait_for_release()
bootmgr.deinit()
