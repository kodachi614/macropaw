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

# BootManager handles special boot modes for the MacroPaw, specifically
# hardware test mode and mass storage mode. The various MacroPaw boards each
# have a way to trigger these modes, which are embodied by the various Trigger
# classes.

import board
import digitalio
import os
import storage
import time
import usb_cdc

from adafruit_neopixelbackground import NeoPixelBackground


class Trigger:
    """
    Base class for triggers. Every Trigger has a setup() method that does
    whatever setup is needed once the Trigger's BootManager exists, and a
    check() method that returns a boolean indicating whether the trigger
    condition has been met or not.
    """

    def setup(self, bootmanager):
        """
        Do whatever setup the Trigger needs (if any) once its BootManager
        exists -- for example, this is where setting up DigitalInOuts should
        happen, so that multiple Triggers can share them if needed. This
        method can be ignored if the Trigger doesn't need it.
        """
        pass

    def check(self) -> bool:
        """
        Check the trigger condition. This method should be overridden by
        subclasses.

        The check() method should _poll_ for its trigger condition, rather
        than doing anything too fancy. This is used in boot code, after all.
        """
        raise NotImplementedError("Subclasses must implement check() method.")


class TriggerAlways(Trigger):
    """
    Trigger that is always true. Helpful for testing.
    """
    def check(self) -> bool:
        return True


class TriggerNever(Trigger):
    """
    Trigger that is always false, for testing or for a board that should
    never enter a special mode in the field.
    """
    def check(self) -> bool:
        return False


class TriggerPin(Trigger):
    """
    Trigger when a specific pin has a specific value.
    """
    def __init__(self, pin, value):
        self.pin = pin
        self.value = value

    def setup(self, bootmanager):
        self.io = bootmanager.get_pin(self.pin, digitalio.Direction.INPUT)

    def check(self) -> bool:
        return self.io.value == self.value


class TriggerRowCombo(Trigger):
    """
    Trigger when a certain combination of keys on the same row are pressed.
    """
    def __init__(self, row_pin, *col_pins):
        self.row_pin = row_pin
        self.col_pins = col_pins
        self.row = None
        self.cols = None

    def setup(self, bootmanager):
        # Set up the row pin.
        self.row = bootmanager.get_pin(self.row_pin, digitalio.Direction.OUTPUT)
        self.row.value = False

        # Set up the column pins.
        self.cols = []
        for col_pin in self.col_pins:
            col_io = bootmanager.get_pin(col_pin, digitalio.Direction.INPUT)
            self.cols.append(col_io)

    def check(self) -> bool:
        rc = False
        self.row.value = True

        # Check if all columns are pressed.
        if all(col.value for col in self.cols):
            rc = True

        self.row.value = False
        return rc


class BootManager:
    def __init__(self, pixelcount, mass_storage_trigger, hardware_test_trigger):
        # We're not going to do a matrix scan, but we still need to drive
        # rows and read columns to check for the special keys.
        self.pin_cache = {}

        self.mass_storage_trigger = mass_storage_trigger
        self.mass_storage_trigger.setup(self)

        self.hardware_test_trigger = hardware_test_trigger
        self.hardware_test_trigger.setup(self)

        # Finally, we use the first pixel to indicate if you're doing anything
        # special during boot. We use an array of R, G, B values to make it
        # easy to play with the individual elements.a
        self.bootpixel = NeoPixelBackground(board.NEOPIXEL, pixelcount,
                                            pixel_order="GRB",
                                            brightness=0.125)

        self.color = [0, 0, 0]
        self.show()

    def get_pin(self, pin, direction):
        """
        Get a pin, creating it if it doesn't exist. This is used to cache
        pins so that we don't create them multiple times.
        """
        pin_io = self.pin_cache.get(pin)

        if pin_io is None:
            print(f"BootManager: initializing pin {pin} as {direction}")
            pin_io = digitalio.DigitalInOut(pin)
            pin_io.direction = direction
            self.pin_cache[pin] = pin_io
        else:
            if pin_io.direction != direction:
                raise ValueError(f"BootManager: can't set {pin} {direction}, already in use as {pin_io.direction}")

            print(f"BootManager: reusing pin {pin} as {direction}")

        return pin_io

    def show(self):
        self.bootpixel.fill(self.color)
        self.bootpixel.show()

    def check_mass_storage(self) -> bool:
        rc = self.mass_storage_trigger.check()

        if rc:
            # Mass storage is enabled, so add blue to our pixel color.
            self.color[2] = 64
            self.show()

        return rc

    def check_hardware_test(self) -> bool:
        rc = self.hardware_test_trigger.check()

        if rc:
            # Hardware test is enabled, so add red to our pixel color.
            self.color[0] = 64
            self.show()

        return rc

    def wait_for_release(self):
        while self.check_mass_storage() or self.check_hardware_test():
            time.sleep(0.01)

    def deinit(self):
        # Deinit our pins.
        for pin in self.pin_cache.values():
            pin.deinit()

        # Deinit the boot pixel.
        self.color = [0, 0, 0]
        self.show()

        self.bootpixel._sm.deinit()

    def _manage_semaphore(self, name: str, value: bool):
        """
        Manage a semaphore file.
        """
        try:
            storage.remount("/", readonly=False)
        except Exception as e:
            raise RuntimeError(f"BootManager: could not remount / read-write: {e}")

        semaphore_path = f"/{name}"

        if value:
            try:
                with open(semaphore_path, "w") as f:
                    f.write("1")
            except Exception as e:
                raise RuntimeError(f"BootManager: can't create {semaphore_path}: {e}")
        else:
            try:
                os.remove(semaphore_path)
            except:
                pass

        try:
            storage.remount("/", readonly=True)
        except Exception as e:
            raise RuntimeError(f"BootManager: could not remount / read-only: {e}")

    def set_hardware_test(self, enabled: bool):
        """
        Manage the hardware test mode semaphore.
        """
        self._manage_semaphore("hardware_test", enabled)

    def set_mass_storage(self, enabled: bool, enable_serial: bool=False):
        """
        Manage mass storage mode semaphore.
        """
        if not enabled:
            # Disable mass storage:
            storage.disable_usb_drive()

            if not enable_serial:
                # Disable USB serial.
                usb_cdc.disable()