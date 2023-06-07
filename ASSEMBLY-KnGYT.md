# MacroPaw KnGYT Assembly Guide

The MacroPaw KnGYT was produced as a fully-assembled two-sided PCB board:
everything except keyswitches was assembled at the factory. To assemble a
KnGYT you need to put the PCB into its case and install keyswitches.

- Install switches
- Factory reset (optional with a new board)
- Install firmware
- Hardware test
- Install into case

## Install Switches

Since the KnGYT has its hotswap sockets in place from the factory, there's no
reason not to install the switches before anything else, to be able to do a
proper hardware test. The easiest way to install the switches into a KnGYT is
to set the switch plate on top of the PCB (make sure the notch in the plate is
at the upper left of the board, when viewing the PCB from the top with the USB
port on the left), then **carefully** insert switches one at a time through
the plate into the hotswap sockets.

Install all ten switches before proceeding.

## Factory Reset

To completely reset a KnGYT to new-out-of-the-factory condition, you need to
wipe its onboard flash memory. **WARNING: this will, of course, erase any
customization you've done.**

1. Grab David Welch's `flash_nuke.uf2` from
   https://github.com/dwelch67/raspberrypi-pico. This is a minimal RP2040
   program to completely wipe the attached flash.

   ```bash
   curl -o /tmp/flash_nuke.uf2 https://github.com/dwelch67/raspberrypi-pico/raw/main/flash_nuke.uf2
   ```

2. If your KnGYT doesn't already show up as the `RPI_RP2` volume when you plug
   it in, hold down the USB_BOOT button on the MacroPaw KnGYT board and plug
   it into your computer with a USB-C cable. (If it's already plugged in,
   press and release the RESET button while still holding USB_BOOT, then
   release USB_BOOT.) The KnGYT should appear as a USB Mass Storage device
   named `RPI_RP2` on your computer.

3. Copy `flash_nuke.uf2` to the `RPI_RP2` volume. On a Mac, this is most simply done with

   ```bash
   cp /tmp/macropaw-KnGYT.uf2 /Volumes/RPI_RP2
   ```

4. The `RPI_RP2` volume will vanish while `flash_nuke` runs, then return once it's done.

## Install Firmware

1. Grab the most recent MacroPaw KnGYT firmware from www.kodachi.com:

   ```bash
   curl -o /tmp/macropaw-KnGYT.uf2 https://www.kodachi.com/firmware/macropaw-KnGYT.uf2
   ```

   (Alternately, you can build your own firmware: follow the docs in [BUILDING.md].)

2. If your KnGYT doesn't already show up as the `RPI_RP2` volume when you plug
   it in, hold down the USB_BOOT button on the MacroPaw KnGYT board and plug
   it into your computer with a USB-C cable. (If it's already plugged in,
   press and release the RESET button while still holding USB_BOOT, then
   release USB_BOOT.) The KnGYT should appear as a USB Mass Storage device
   named `RPI_RP2` on your computer.

3. Copy the firmware to the `RPI_RP2` volume. On a Mac, this is most simply done with

   ```bash
   cp /tmp/macropaw-KnGYT.uf2 /Volumes/RPI_RP2
   ```

   **This step can take awhile**; 30-60 seconds is not unusual.

4. Wait for the KnGYT to reboot into hardware test mode.

## Hardware Test

The first time a MacroPaw is booted after new firmware is installed, it will
launch in _hardware test mode_. This mode doesn't function as a keyboard:
instead, it lets you verify that the LEDs, keyswitches, and rotary encoders on
the board work.

When booting in hardware test mode, all the lights will flash yellow at
startup. The LEDs should then cycle through red, green, and blue, then end up
all at a dim white.

Once all the LEDs are dim white, pressing a key should change its LED to red.
Repeated presses should turn it green, then blue, then off. When you've cycled
all the LEDs have gone through all their colors, you should see all the LEDs
turn green again. Press the RESET button on the MacroPaw to exit hardware
test.

## Install into Case

Installing the KnGYT into its case is fairly straightforward.

- Lay the MacroPaw into the bottom half of the case, switches up, USB port to
  the left.

- Lay the top half of the case over the MacroPaw and switch plate.

- Slide the end caps onto the ends of the case. Make sure you use the end cap
  with a port on the USB-port side of the MacroPaw. (Obviously, you'll need to
  unplug the MacroPaw to do this.)

- Plug the board back in!

## Using Your MacroPaw

After leaving hardware test mode, your MacroPaw should be a real keyboard. It
should flash all its lights yellow when first booting, then start a blue
"breathing" animation with the LEDs under the keys repeatedly cycling across
brightnesses. Check out the [User Guide] for more on using your MacroPaw.

[BUILDING.md]: BUILDING.md
[User Guide]: USERGUIDE.md
