# MacroPaw User Guide

The MacroPaw keypads are a line of small yet fully-customizable mechanical
keyboards. (The name was originally from my son, years ago when he was young,
and the "paw" motif has kinda stuck.) The core of the MacroPaws is a Raspberry
Pi RP2040 with 16MiB of flash memory, a USB-C connector, and an attached key
matrix and RGB LEDs (which may or may not be under the keys). Some MacroPaws
have more capability than others; all are crazy customizable by writing Python
code. (Yes. Python. On a keyboard. It's insane and wonderful to live in the
future.)

This guide covers the MacroPaw Beatboxer KnH0F board. There is a [separate
guide] for the MacroPaw KnGXT and KnGYT boards.

[separate guide]: USERGUIDE.md

## Overview

The MacroPaw Beatboxer KnH0F has 8 RGB LEDs on the front of the board, for
debugging, and an 8x8 key matrix that's normally mechanically set up as a 16x4
grid of arcade buttons. It also has three small buttons on the front of the board: `USB BOOT`, `HWTEST`, and `RESET`.

The default firmware (available at https://www.kodachi.com/firmware) for both
boards supports a normal keyboard mode in which each of the 8x8 grid of
buttons sends a separate USB key, a hardware test mode to make sure everything
is working, and of course the ability to fully reprogram the firmware.

## Normal Operation

After a MacroPaw Beatboxer KnH0F has been flashed and tested, when you plug it
in it will act like a keyboard. The default firmware uses the following
layout:

| Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 | Col 7 | Col 8 |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| a | b | c | d | e | f | g | h |
| i | j | k | l | m | n | o | p |
| q | r | s | t | u | v | w | x |
| A | B | C | D | E | F | G | H |
| I | J | K | L | M | N | O | P |
| Q | R | S | T | U | V | W | X |
| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| - | = | . | , | / | ; | space | enter |

## Special Operation Modes

### First Use

The very first time a MacroPaw is booted, it will launch in USB Boot mode to
be flashed with new firmware. See the [Flashing](#flashing) section below for
details on how to do this.

### Flashing

To flash the firmware, the MacroPaw must be in USB Boot mode, where it will appear as a USB Mass Storage device called `RPI-RP2`. The first time a MacroPaw is booted, it will automatically enter USB Boot mode. If you need to reenter USB Boot mode, hold down the `USB BOOT` button while either plugging in the MacroPaw or pressing the `RESET`.

You can flash new firmware in this mode by copying a `macropaw-Beatboxer.uf2` file to the `RPI-RPI2` volume. This may take 30-60 seconds; this is normal. After flashing, the `RPI-RPI2` volume will disappear, and the MacroPaw will reboot into hardware test mode.

### Hardware Test Mode

In hardware test mode, the MacroPaw will _not_ act like a keyboard. It first
light all the LEDs in red, then green, then blue, then dim white. After that,
it will turn off the LEDs and starting monitoring key presses. For each key
press, it will light the LED for that key's row in red, and for that key's
column in blue (keys on the diagonal will led a single LED in purple, since
the same LED will be lit both red and blue).

Once all the keys have been pressed, the LEDs will flash green and the board will reboot into normal operation, as a keyboard. (If the LEDs light red, there is a problem.)

To reenter hardware test mode later, hold the `HWTEST` button while either
plugging in the MacroPaw or pressing the `RESET` button. The MacroPaw will show a countdown on the LEDs; keep holding the `HWTEST` button until the countdown is over, then let go. The board will reboot into hardware test mode.

## Resetting

To reset a Beatboxer board, either unplug and replug it, or hold the RESET
button for a second or two, then let go. When you let go, the board will
reset.

## Mass Storage Mode

To enter mass storage mode - where the MacroPaw will appear as a USB mass
storage device called `MACROPAW`, and you can edit the firmware files live -
hold down the `HWTEST` button while plugging in the MacroPaw or pressing the
`RESET` button. The board will show a countdown on the LEDs; let go before the
countdown ends, and the board will reboot into mass storage mode.

### Serial Debugging

While the mass storage device is present (see above), the MacroPaw will also
present a USB-serial interface that you can use as a CircuitPython console.
