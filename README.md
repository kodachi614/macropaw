This is the MacroPaw keypad project:

KnGXT: First version of the MacroPaw, ID KnGXT. Mostly a proof-of-concept for
       an RP2040-based USB keyboard with rotary encoders and lights.

Both the hardware and the firmware of the MacroPaw are **open source**.

## Hardware

The hardware is licensed under the CERN Open Hardware License, version 2.0
or higher, Strongly Reciprocal.

The `hardware` directory within each board's directory includes the KiCad 6.0
design files for the hardware, the fabrication outputs used for the official
production runs of the hardware, and of course the hardware license
(in `hardware/LICENSE`).

## kicad_libraries

The `kicad_libraries` directory (at toplevel) has KiCad footprints and symbols from
the following sources:

- `JLCPCB_LEDs`: hand-generated KiCad footprints for some WS2812B devices available
  from JLCPCB. These are licensed under the CERN Open Hardware License, version 2.0
  or higher, Strongly Reciprocal.

- `RP_Silicon_KiCad`: RP2040 and related symbols and footprints from [HeadBoffin].
  These were directly pulled from the Raspberry Pi publications.

[HeadBoffin]: https://github.com/HeadBoffin/RP_Silicon_KiCad
