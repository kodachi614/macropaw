# MacroPaw Keypads

The MacroPaw keypads are a line of small yet fully-customizable mechanical
keyboards. (The name was originally from my son, years ago when he was young,
and the "paw" motif has kinda stuck.) The core of the MacroPaws is a Raspberry
Pi RP2040 with 16MiB of flash memory, a USB-C connector, and an attached key
matrix and RGB LEDs (which may or may not be under the keys). Some MacroPaws
have more capability than others; all are crazy customizable by writing Python
code. (Yes. Python. On a keyboard. It's insane and wonderful to live in the
future.)

| ![](photos/KnGXT.png) | ![](photos/KnGXT-board-top.png) |
| :-: | :-: |
| _Assembled KnGXT_     | _KnGXT PCB_ |

Currently extant MacroPaw boards include:

| Board ID | Description |
| :-: | :- |
| KnGXT | Mostly a proof-of-concept for an RP2040-based USB HID: it has 14 hotswappable MX keyswitches in a 3x5 layout like a number pad (including one 2U key, which is why it's 14 instead of 15), two rotary encoders with pushbuttons, and a bunch of RGB LEDs under the encoders and keys. |
| KnGYT | Mostly a proof-of-concept for double-sided assembly. It has ten hotswappable MX keyswitches in a 5x2 grid, ten RGB LEDs under the keys, and no rotary encoders. It's _much_ smaller than its sibling the KnGXT, because most of the electronics are on the back of the board. |
| Beatboxer KnH0F | A single-sided embedded keyboard controller for use in a [custom life-sized drum machine]. It has 8 RGB LEDs on the front of the board for hardware test and debugging, and its key matrix is an 8x8 grid that's mechanically arranged as a 16x4 grid of arcade buttons. |

[custom life-sized drum machine]: https://sig.gy/bbox/

Both the firmware and the hardware of the MacroPaws are **open source**.

## Firmware

The firmware is licensed under the GNU General Public License, version 3.0 or
later.

The `firmware` directory within each board's directory includes the firmware
source code firmware and the firmware license (in `firmware/LICENSE`).

The MacroPaw firmware is based on the [KMK Firmware], and on Adafruit's
[CircuitPython] and the [NeoPixelBackground] class. See
[BUILDING.md](BUILDING.md) for details about how to build the firmware,
including information about the versions of CircuitPython and KMK that are
used and how to get them.

Of course, if you don't want to build your own, you can just grab prebuilt
firmware for the [MacroPaw KnGXT], [MacroPaw KnGYT], and [MacroPaw Beatboxer
KnH0F] boards.

[KMK Firmware]: https://github.com/KMKfw/kmk_firmware/
[CircuitPython]: https://circuitpython.org/
[NeoPixelBackground]: https://learn.adafruit.com/intro-to-rp2040-pio-with-circuitpython/advanced-using-pio-to-drive-neopixels-in-the-background
[MacroPaw KnGXT]: https://www.kodachi.com/firmware/macropaw-KnGXT.uf2
[MacroPaw KnGYT]: https://www.kodachi.com/firmware/macropaw-KnGYT.uf2
[MacroPaw Beatboxer KnH0F]: https://www.kodachi.com/firmware/macropaw-Beatboxer.uf2

## Hardware

The hardware is licensed under the CERN Open Hardware License, version 2.0
or higher, Strongly Reciprocal.

The `hardware` directory within each board's directory includes the [KiCad] 7
design files for the hardware, the fabrication outputs used for the official
production runs of the hardware, and of course the hardware license (in
`hardware/LICENSE`).

[KiCad]: https://www.kicad.org/

## 3D Models

The `models` directory within some boards' directories includes the 3D models
for cases, etc., for the board. Boards without a `models` directory haven't
had models made yet!

The models are also licensed under the CERN Open Hardware License, version 2.0
or higher, Strongly Reciprocal.