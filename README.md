# Lotus LED Matrix Module

It's a 9x34 (306) LED matrix, controlled by RP2040 MCU and IS31FL3741A LED controller.
Connection to the host system is via USB 2.0 and currently there is a USB Serial API to control it without reflashing.

Rust project setup based off of: https://github.com/rp-rs/rp2040-project-template

## Features

- Reset into bootloader when firmware crashes/panics
- API over USB ACM Serial Port - Requires not Drivers on Windows and Linux
  - Display various pre-programmed patterns
  - Light up a percentage of the screen
  - Change brightness
  - Send a black/white image to display
  - Go to sleep
  - Reset into bootloader
  - Scroll and loop the display content vertically
  - A commandline script and graphical application to control it
- Sleep Mode
  - Transition slowly turns off/on the LEDs
  - Current hardware does not have the SLEEP# GPIO connected, can't sleep automatically

Future features:

- API
  - Send a greyscale image to display
  - Read current system state (brightness, sleeping, ...)

## Control from the host

Requirements: Python and [PySimpleGUI](https://www.pysimplegui.org).

Use `control.py`. Either the commandline, see `control.py --help` or the graphical version: `control.py --gui`

```
options:
  -h, --help            show this help message and exit
  --bootloader          Jump to the bootloader to flash new firmware
  --sleep, --no-sleep   Simulate the host going to sleep or waking up
  --brightness BRIGHTNESS
                        Adjust the brightness. Value 0-255
  --animate, --no-animate
                        Start/stop vertical scrolling
  --pattern {full,lotus,gradient,double-gradient,zigzag,panic,lotus2}
                        Display a pattern
  --image IMAGE         Display a PNG or GIF image (black and white only)
  --percentage PERCENTAGE
                        Fill a percentage of the screen
  --clock               Display the current time
  --gui                 Launch the graphical version of the program
  --panic               Crash the firmware (TESTING ONLY)
```

## Building

Dependencies: Rust

Prepare Rust toolchain:

```sh
rustup target install thumbv6m-none-eabi
cargo install flip-link
cargo install elf2uf2-rs --locked
```

Build:

```sh
cargo build
```

Generate UF2 file:

```sh
elf2uf2-rs target/thumbv6m-none-eabi/debug/led_matrix_fw led_matrix.uf2
```

## Flashing

First, put the module into bootloader mode, which will expose a filesystem

This can be done by pressing the bootsel button while plugging it in.

```sh
cargo run
```

Or by copying the above generated UF2 file to the partition mounted when the
module is in the bootloder.

## Panic

On panic the RP2040 resets itself into bootloader mode.
This means a new firmware can be written to overwrite the old one.

Additionally the panic message is written to flash, which can be read as follows:

```sh
sudo picotool save -r 0x15000000 0x15004000 message.bin
strings message.bin | head
```
