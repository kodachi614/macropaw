This is the MacroPaw keypad project:

KnGXT: First version of the MacroPaw, ID KnGXT. Mostly a proof-of-concept for
       an RP2040-based USB keyboard with rotary encoders and lights.

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
[CircuitPython] and the [NeoPixelBackground] class. The MacroPaw firmware
uses modified versions of all of these: see BUILDING.md in the firmware
directory for more. You can also simply flash your MacroPaw with the
[KnGXT.uf2] file from this repo.

[KMK Firmware]: https://github.com/KMKfw/kmk_firmware/
[CircuitPython]: https://circuitpython.org/
[NeoPixelBackground]: https://learn.adafruit.com/intro-to-rp2040-pio-with-circuitpython/advanced-using-pio-to-drive-neopixels-in-the-background
[KnGXT.uf2]: https://raw.githubusercontent.com/kodachi614/macropaw/main/KnGXT.uf2

## 3D Models

The `models` directory within some boards' directories includes the 3D models
for cases, etc., for the board. Boards without a `models` directory haven't
had models made yet!

The models are also licensed under the CERN Open Hardware License, version 2.0
or higher, Strongly Reciprocal.