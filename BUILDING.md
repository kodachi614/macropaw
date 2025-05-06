# Building

This document describes how to build the MacroPaw firmware from source.

## Testing Tweaks

If you're still testing tweaks to the MacroPaw code itself, don't bother
constantly rebuilding the code: instead, check your board to see if there's a
way to get it into developer mode where it shows up as a mountable USB drive.
If so, you can just copy the new code over to the board and reboot it.

Of course, when you're done testing, you'll probably be best off building a
new firmware UF2 to flash to the board. This is especially true if you want to
distribute the firmware to others, or if you want to make sure that the
firmware is in a known-good state.

## Building The Firmware The Simple Way

If all you've done is to the MacroPaw code itself, and you don't need to
either add support for a new kind of MacroPaw board or upgrade the version of
KMK in use, just clone this `kodachi614/macropaw` repo and run `make` in it.
This will build firmware for all supported boards and leave the resulting UF2
images in `macropaw-$boardID.uf2` files in the root of the repo.

To make a single board, run `make $boardID` instead. For example, to build
just the firmware for the KnGXT, run `make KnGXT`.

## The Complex Way

So... what if you _do_ want to add support for a new kind of MacroPaw board,
or you want to upgrade KMK? Three repos work together for this:
`kodachi614/circuitpython`, `kodachi614/kmk_firmware`, and
`kodachi614/macropaw`:

1. First, you need the CircuitPython base image. This is the CircuitPython code
   with board-specific support code, but nothing about KMK or the MacroPaw
   code itself: it's just CircuitPython. Loading the base image onto a MacroPaw
   board will give you the ability to run Python code, but it won't give you a
   working keyboard.

2. Next, you need the KMK base tarfile. This is CircuitPython code that
   provides the ability for a board to act like a USB HID keyboard. This is
   the only piece of the firmware that isn't board-specific.

3. Finally, you need the MacroPaw code itself. This is CircuitPython code that
   uses KMK to make a MacroPaw board act like a MacroPaw: it defines the
   keymap, how the LEDs get handled, and so on.

**Note: Firmware is board-specific.**

You'll be building firmware _for a specific board_. We'll show how to build
for the MacroPaw KnGXT here.

As a rule of thumb, if you aren't trying to modify a particular layer of
software, you shouldn't need to build it. For example, if you haven't touched
CircuitPython itself, you don't need to build the base CircuitPython base
image yourself: the build process knows how to grab the one published at
www.kodachi.com.

### 1. The CircuitPython Base Image

The CircuitPython base image has CircuitPython with board-specific support
code, but nothing about KMK or the MacroPaw code itself: it's just
CircuitPython. Loading the base image onto a MacroPaw board will give you the
ability to run Python code, but it won't give you a working keyboard.

**The CircuitPython base image is board-specific** because it contains
information about which specific pins on the RP2040 are used for which
functions. Every board has its own base image.

In the `kodachi614/circuitpython` repo, you'll find board definitions for each
MacroPaw. To build the base image for a KnGXT:

- `cd ports/raspberrypi` in your clone of `kodachi614/circuitpython`
- `make BOARD=kodachi_macropaw_kngxt clean`
- `make BOARD=kodachi_macropaw_kngxt`

The built base image will be in `build-kodachi_macropaw_kngxt/firmware.uf2`.
Copy that into `tools/base-firmware-KnGXT.uf2` in your clone of
`kodachi614/macropaw` for later use.

To publish this base image for others to use, shove it into
`kflynn.github.io/firmware` as
`circuitpython-kodachi-$version-g$commit-$boardID`, then push the GitHub Pages
repo. For example, if you're building the base image for the KnGXT using
CircuitPython 10.0.0 at commit 62e602c3d3, you'd call it
`circuitpython-kodachi-10.0.0-g62e602c3d3-KnGXT.uf2`.

### 2. The KMK Base Tarfile

Given the CircuitPython base image, you next need the KMK firmware. This is
the CircuitPython code that provides the ability for a board to act like a USB
HID keyboard. This is the only piece of the firmware that isn't
board-specific.

From the `kodachi614/kmkfw` repo, just run `MOUNTPOINT=/tmp make tar` to tar
up everything you need into `kmk-$SHA.tgz`. Copy that into
`macropaw/tools` without changing its name.

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

Once you have `RPI_RP2` mounted, on MacOS run `tools/flash $boardID` (e.g.
`tools/flash KnGXT`. If you're not on MacOS, `cp tools/flash_nuke.uf2` to the
RPI-RP2 volume, then once the board reboots, `cp macropaw-$boardID.uf2` to the
RPI-RP2 volume. The board will reboot into its hardware test mode; follow the
directions for your board to complete the hardware test and have it reboot
into being a keyboard!
