# Building

This document describes how to build the MacroPaw firmware from source. This
should Just Work on MacOS and Linux; it probably has a fighting chance with
WSL2 on Windows, but that's untested.

If you're just trying to flash a MacroPaw board, you probably don't need this
document: check out the [README.md](README.md) or maybe the [User
Guide](USERGUIDE.md) instead.

## Overview

When a MacroPaw board boots, what's actually getting booted is
[CircuitPython]; in turn, CircuitPython loads up the MacroPaw's `boot.py` and
`code.py` files to make things actually happen.
([BOOT-DETAILS.md](BOOT-DETAILS.md) has a lot more detail on this.)

Given all of this, to build the firmware for a MacroPaw board you must:

1. Have a working CircuitPython base image. This is the CircuitPython code with
   board-specific support code, but nothing about KMK or the MacroPaw code
   itself: it's just CircuitPython. Loading the base image onto a MacroPaw
   board will give you the ability to run Python code, but it won't give you a
   working keyboard.

   **You don't have to build this yourself** unless you need to change it. The
   build process knows how to fetch a prebuilt version for you.

2. Have a working KMK base image. This is the CircuitPython code that provides
   the ability for a board to act like a USB HID keyboard. This is the only
   piece of the firmware that isn't board-specific.

   **You don't have to build this yourself** unless you need to change it. The
   build process knows how to fetch a prebuilt version for you.

3. Take the MacroPaw code and the KMK code, load them into a FAT filesystem
   image, and then combine that with the base CircuitPython image so that
   CircuitPython finds the FAT with the MacroPaw code when it boots.

The output of this process is a single .UF2 file that you can flash to your
MacroPaw board. The Makefile here knows how to do all of this, but the real
magic mostly happens in `tools/build-uf2` and `tools/flash`.

**This is version 0.5.2 of the MacroPaw firmware.** It is based on

- CircuitPython 9.2.7 built from commit `a87b74cd54` on the
  `flynn/kodachi-ports-9.2.7` branch of
  [kodachi614/circuitpython](https://github.com/kodachi614/circuitpython)

- KMK built from commit `e176c41b1d` on the `flynn/dev/macropaw-2` branch of
  [kodachi614/kmk_firmware](https://github.com/kodachi614/kmk_firmware)

Again, **you do not have to build either of these yourself.** The build
process knows how to fetch prebuilt versions from
<https://www.kodachi.com/firmware> for you; you only _need_ to build them
yourself if you're trying to make changes in them.

[KMK Firmware]: https://github.com/KMKfw/kmk_firmware/
[CircuitPython]: https://circuitpython.org/

## Tools You'll Need

- Python 3.10 or later

   On MacOS, you can use `brew install python` for this: the system Python is
   not likely to work.

- `mkfs.vfat`

   Part of the build process involves creating a FAT filesystem image; to do
   that, we need `mkfs.vfat`. On MacOS, get this with `brew install
   dosfstools` (and make sure that `/opt/homebrew/sbin` is in your `PATH`).

- GNU `make`

   Install GNU `make` on MacOS with `brew install make` and use that (it'll
   install as `gmake`). The Makefile here won't work with the system `make`.

- `mpy-cross`

   Finally, in a perfect world you'll have `mpy-cross` somewhere on your
   `PATH`. `mpy-cross` is a tool from CircuitPython that reads .py files and
   outputs `.mpy` files, which contain Python bytecode: this is a win because
   it lets CircuitPython just load the bytecode instead of having to parse the
   Python source at boot time. On a KnGXT, this cuts startup time from about
   three seconds to under half a second.

   At the moment, the only way to get `mpy-cross` is to build CircuitPython.
   There are [great directions for this] but it would be lovely if there were
   an easier way. **If you build `mpy-cross`, pay attention to the version of
   CircuitPython you use.** You **must** use the same version of CircuitPython
   that the MacroPaw firmware is built with.

[great directions for this]: https://docs.circuitpython.org/en/latest/BUILDING.html

## The Basic Build Process

Given the prerequisites above, just clone this repo and run `make` on a Mac or
Linux box. You'll get a bunch of `macropaw-$boardID.uf2` files in the root of
the repo.

To make a single board, run `make $boardID` instead. For example, to build
just the firmware for the KnGXT, run `make KnGXT`.

### Testing Tweaks

If you're actively testing tweaks to the MacroPaw code itself, don't bother
constantly rebuilding the code. Instead, check your board to find out how to
get it into mass storage mode, where it'll show up as a mountable USB drive.
In that mode, you can just copy the new code over to the board and it'll
automagically reboot into your new code. It will also present a serial port in
this mode, which you'll definitely want to connect to so you can see debug
logs, error reports, etc.

Of course, when you're done testing, you'll probably be best off building a
new firmware UF2 to flash to the board. This is especially true if you want to
distribute the firmware to others, or if you want to make sure that the
firmware is in a known-good state.

## The Complete Build Process

So... what if you _do_ want to add support for a new kind of MacroPaw board,
or you want to upgrade KMK? Three repos work together for this:
`kodachi614/circuitpython`, `kodachi614/kmk_firmware`, and
`kodachi614/macropaw`:

1. `kodachi614/circuitpython` is what you'll use to build the CircuitPython
   base image. This is the CircuitPython code with board-specific support
   code, but nothing about KMK or the MacroPaw code itself.

2. `kodachi614/kmk_firmware` is what you'll use to get the KMK base tarfile.
   This is CircuitPython code that provides the ability for a board to act
   like a USB HID keyboard. This is the only piece of the firmware that isn't
   board-specific.

3. Finally, `kodachi614/macropaw` (this repo) is the MacroPaw code itself.
   This is CircuitPython code that uses KMK to make a MacroPaw board act like
   a MacroPaw: it defines the keymap, how the LEDs get handled, and so on.

**Note: Firmware is board-specific.**

You'll be building firmware _for a specific board_. We'll show how to build
for the MacroPaw KnGXT here.

Again, **you don't need to do this if you're only touching the MacroPaw files
in this repository**. If that's you, go up to the "The Basic Build Process"
section.

### 1. The CircuitPython Base Image

Remember that **the CircuitPython base image is board-specific** because it
contains information about which specific pins on the RP2040 are used for
which functions. Every board has its own base image.

In the `kodachi614/circuitpython` repo, you'll find board definitions for each
MacroPaw. To build the base image for a KnGXT:

- `cd ports/raspberrypi` in your clone of `kodachi614/circuitpython`
- `make BOARD=kodachi_macropaw_kngxt clean`
- `make BOARD=kodachi_macropaw_kngxt`

The built base image will be in `build-kodachi_macropaw_kngxt/firmware.uf2`.
Copy that into `tools/base-firmware-KnGXT.uf2` in your clone of
`kodachi614/macropaw` for later use.

(If you don't have a `base-firmware-KnGXT.uf2` file in your `macropaw/tools`
directory, the build process will pull it from
<http://www.kodachi.com/firmware/circuitpython-kodachi-$version-g$commit-$boardID>
where `$version` and `$commit` have defaults set in the Makefile, and
`$boardID` is e.g. `KnGXT`.)

### 2. The KMK Base Tarfile

Given the CircuitPython base image, you next need the KMK firmware. This is
the CircuitPython code that provides the ability for a board to act like a USB
HID keyboard. This is the only piece of the firmware that isn't
board-specific.

From the `kodachi614/kmkfw` repo, just run `MOUNTPOINT=/tmp make tar` to tar
up everything you need into `kmk-$SHA.tgz`. Copy that into
`macropaw/tools` without changing its name.

(If you don't have a `kmk-$SHA.tgz` file in your `macropaw/tools` directory,
the build process will pull it from
<http://www.kodachi.com/firmware/kmk-$SHA.tgz> where, again, `$SHA` has a
default set by the Makefile.)

### 3. The MacroPaw Code

Finally, you need the MacroPaw code itself. This is CircuitPython code that
uses KMK to make a MacroPaw board act like a MacroPaw: it defines the
keymap, how the LEDs get handled, and so on.

To build the MacroPaw code after you have the base image and the KMK tarfile,
just go to the top level of your clone of the `kodachi614/macropaw` repo and run
`make`. This will build firmware for all supported boards and leave the
resulting UF2 images in `macropaw-$boardID.uf2` files in the root of the repo.

To build just the firmware for a single board, run `make $boardID` instead.
For example, to build just the firmware for the KnGXT, run `make KnGXT`.

## Flashing the Firmware

To flash the firmware, put the MacroPaw board into bootloader mode. How you do
this depends on the board you have, but it's generally a matter of holding
down some BOOT button while plugging it into your computer. Once it's in
bootloader mode, it should show up as a USB drive called "RPI_RP2".

Once you have `RPI_RP2` mounted, run `tools/flash $boardID` (e.g. `tools/flash
KnGXT`). This will erase your board, then flash your board with
`macropaw-$boardID.uf2` (and note that `$boardID` can be kind of fluid, so if
you have a `macropaw-KnGXT-v0.5.0.uf2` for some reason, you could `tools/flash
KnGXT-v0.5.0`).

During the flashing process, you'll see status for what's going on, and on
MacOS you'll also see complaints about `RPI_RP2` being disconnected without
being properly ejected. **This is normal**; there's just no way to get the
disk ejected in time while the board is being flashed.

Once flashing is complete, your board will reboot into its hardware test mode;
follow the directions for your board to complete the hardware test and have it
reboot into being a keyboard!


