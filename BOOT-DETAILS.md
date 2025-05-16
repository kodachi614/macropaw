# Boot Details

What MacroPaws actually _run_ is CircuitPython; the MacroPaw firmware is
really a Python program being executed by the Python interpreter that's
started when the board boots.

## The Boot Process

The boot process for CircuitPython will probably seem familiar to anyone who
has worked with embedded systems, and incredibly alien to anyone who hasn't:

- First, the hardware does its cold-start routine. On embedded systems with
  flash memory (like the MacroPaw boards), this is usually some _very_
  bare-bones hardware initialization, followed by a jump to code that's been
  preloaded into the flash. In this case, that's CircuitPython.

- The CircuitPython boot code first sets up everything needed for the Python
  interpreter itself. Much of this is independent of the hardware it's running
  on (for example, initializing the interpreter's data structures) but some of
  it is hardware-specific (for example, setting up the console to use for the
  error output or a REPL).

- Once CircuitPython has the interpreter ready to go, it looks at a predefined
  location in flash to see if there's a FAT filesystem image there. If so,
  CircuitPython mounts it as `/`, then looks for `/boot.py`.  If that's
  present, it runs it. `/boot.py` gets to do certain special things that are
  hard to change in later code, but other than that it's a normal Python
  script.

- After `/boot.py` runs, CircuitPython looks for `/code.py` and runs that.
  This is the main program for the board, and in the case of a MacroPaw board,
  it's where the code that actually makes the board act like a keyboard lives.

**Note**: you can't use `mpy-cross` to precompile `/boot.py` or `/code.py`.

## USB

USB initialization deserves special mention here:

- The USB stack is part of CircuitPython (specifically, it's the [tinyusb]
  stack).

- During CircuitPython initialization, the `supervisor` object is created, and
  by default it is set up to enable a USB mass storage device and a USB serial
  device.

- One of the special things that `/boot.py` can do is modify the `supervisor`
  to _disable_ mass storage and USB serial -- and in fact, the MacroPaw
  `boot.py` normally disables both, since a MacroPaw board should usually appear as a keyboard, not a keyboard + disk + serial device!

  However, all MacroPaws have a (board-specific) way to enter "mass storage
  mode" where `/boot.py` will permit them to stay enabled. This allows easier
  debugging (you can see errors that get thrown, and you can modify code by
  editing files on the mass storage device).

- **After `/boot.py` completes**, CircuitPython looks at the `supervisor`
  object and configures the USB stack to present the devices that are enabled.
  They can't be disabled after this initialization step, which is why
  `/boot.py` needs to be where the MacroPaws decide whether or not special
  boot modes are in play.

- More USB devices _can_ be added after `/boot.py` completes, and KMK uses
  this capability to configure the USB stack to appear as a USB HID, in
  addition to whatever other devices were already enabled. This is the part
  that makes the board actually look like a keyboard.

- Finally, every USB device has to have a vendor ID and a product ID.
  MacroPaws use vendor ID 0x1209 and a product IDs obtained from
  https://pid.codes/.

[tinyusb]: https://docs.tinyusb.org/en/latest/index.html
