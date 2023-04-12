This is the MacroPaw keypad project:

KnGXT: First version of the MacroPaw, ID KnGXT. Mostly a proof-of-concept for
       an RP2040-based USB HID: it has 14 hotswappable MX keyswitches in a 3x5
       layout like a number pad (including one 2U key, which is why it's 14
       instead of 15), two rotary encoders with pushbuttons, and a bunch of
       RGB LEDs.

KnGYT: Mostly a proof-of-concept for double-sided assembly. It has ten
       hotswappable MX keyswitches in a 5x2 grid, ten RGB LEDs, and no rotary
       encoders. It's _much_ smaller that its sibling the KnGXT. You'll note
       it's also missing its firmware; that's because we're waiting for the
       first build of the hardware to come back!

Both the hardware and the firmware of the MacroPaw are **open source**.

## Hardware

The hardware is licensed under the CERN Open Hardware License, version 2.0
or higher, Strongly Reciprocal.

The `hardware` directory within each board's directory includes the KiCad 7
design files for the hardware, the fabrication outputs used for the official
production runs of the hardware, and of course the hardware license
(in `hardware/LICENSE`).

## Firmware

The firmware is licensed under the GNU General Public License, version 3.0.

The `firmware` directory within each board's directory includes the firmware
source code firmware and the firmware license (in `firmware/LICENSE`).

The MacroPaw firmware is based on the [KMK Firmware], and on Adafruit's
[CircuitPython] and the [NeoPixelBackground] class. The MacroPaw firmware uses
modified versions of all of these: to build your own copy, just clone this
repo and run `make` on a Mac or Linux box (you will need to `brew install
dosfstools` on your Mac, and then make sure that `/opt/homebrew/sbin` is in
your `PATH`, for this to work).

Alternately, you can grab prebuilt firmware for the [MacroPaw KnGXT].

[KMK Firmware]: https://github.com/KMKfw/kmk_firmware/
[CircuitPython]: https://circuitpython.org/
[NeoPixelBackground]: https://learn.adafruit.com/intro-to-rp2040-pio-with-circuitpython/advanced-using-pio-to-drive-neopixels-in-the-background
[MacroPaw KnGXT]: https://www.kodachi.com/firmware/macropaw-KnGXT.uf2

## 3D Models

The `models` directory within some boards' directories includes the 3D models
for cases, etc., for the board. Boards without a `models` directory haven't
had models made yet!

The models are also licensed under the CERN Open Hardware License, version 2.0
or higher, Strongly Reciprocal.