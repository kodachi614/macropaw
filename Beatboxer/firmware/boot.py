# SPDX-FileCopyrightText: 2025 Kodachi 6 14
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2022-2025 Kodachi 6 14
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
import digitalio
import time

from firstboot import FirstBoot
from bootmanager import BootManager, Trigger

# Fun fact about the Beatboxer: where most of the MacroPaw boards are used in
# environments where it's trivial to hold down keys while booting, the
# Beatboxer is not, so key combinations to access special modes aren't the
# best idea. Instead, the KnH0F v1 has a dedicated HWTEST button... but, uh,
# it doesn't have a dedicated MASS_STORAGE button, d'oh!
#
# In practice, mass storage mode will likely be used more often in the field
# than hardware test mode, so we'll use the HWTEST button for both modes: when
# it's pressed while booting, we start a countdown on the LEDs. If you let go
# of the button before the countdown is over, we enter mass storage mode. If
# you hold it down all the way through the countdown, we enter hardware test
# mode.
#
# This requires some custom logic for the BootManager triggers.


class BeatboxerMassStorageTrigger(Trigger):
    def __init__(self, mgr):
        self._mgr = mgr

    def check(self) -> bool:
        return self._mgr.check_mass_storage()


class BeatboxerHardwareTestTrigger(Trigger):
    def __init__(self, mgr):
        self._mgr = mgr

    def check(self) -> bool:
        return self._mgr.check_hardware_test()


class BeatboxerManager(BootManager):
    def __init__(self):
        # The Beatboxer has 8 LEDs, and we'll always use our special
        # triggers.
        super().__init__(8,
            BeatboxerMassStorageTrigger(self),
            BeatboxerHardwareTestTrigger(self),
        )

        self.bootpixel.fill((0, 0, 64))
        self.bootpixel.show()

        time.sleep(0.25)

        self.bootpixel.fill((0, 0, 0))
        self.bootpixel.show()

        # Assume that no special modes will be triggered.
        self._mass_storage = False
        self._hardware_test = False

        # Set up to read our GPIO pin. It has a hardware pullup, so it
        # will be low when pressed.
        self.hwtest = self.get_pin(board.HWTEST, digitalio.Direction.INPUT)

        if self.hwtest.value:
            # HWTEST is not pressed, so no special modes will be triggered,
            # so we're done.
            print("HWTEST not pressed, continuing normal boot")
            return

        # HWTEST is pressed, so we need to do the whole countdown thing. Since
        # we don't really want to mess with tasks or anything in boot code,
        # we'll cheat massively and just block here until either the button is
        # released or the countdown is over.

        print("Countdown starting")

        countdown = 8

        while countdown >= 0:
            countdown -= 1
            self.bootpixel.fill((0, 0, 0))

            if countdown < 0:
                # The countdown is over, so we'll enter hardware test mode.
                print("Countdown complete: enabling hardware test mode.")
                self._hardware_test = True
                self.bootpixel.show()
                break

            # Go ahead and light the correct LED for the countdown...
            self.bootpixel[countdown] = (0, 0, 64)
            self.bootpixel.show()

            # ...and wait for a second.
            time.sleep(1)

            # Is the button still pressed?
            if self.hwtest.value:
                # Nope: we'll enter mass storage mode.
                print("Button released during countdown: enabling mass storage mode.")
                self._mass_storage = True
                break

    def check_mass_storage(self) -> bool:
        # Check if the mass storage trigger is active.
        return self._mass_storage

    def check_hardware_test(self) -> bool:
        # Check if the hardware test trigger is active.
        return self._hardware_test

    def wait_for_release(self):
        # We already did all our waiting.
        return


# Start by assuming that nothing special is going on.
enable_hardware_test = False
enable_mass_storage = False

firstboot = FirstBoot()

# Fire up the BeatboxerManager to figure out if we need to enter any
# special boot modes.
bootmgr = BeatboxerManager()

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
