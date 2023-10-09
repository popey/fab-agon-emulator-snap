# fab-agon-emulator-snap


## Snap of the Fab Agon Emulator

[![fab-agon-emulator](https://snapcraft.io/fab-agon-emulator/badge.svg)](https://snapcraft.io/fab-agon-emulator)
[![fab-agon-emulator](https://snapcraft.io/fab-agon-emulator/trending.svg?name=0)](https://snapcraft.io/fab-agon-emulator)

![Alt](https://repobeats.axiom.co/api/embed/4a799dbf2b41eef17c9a19115972ec36355ca9cb.svg "Repobeats analytics image")

This repo contains the build recipe to compile [fab-agon-emulator](https://github.com/tomm/fab-agon-emulator).

This will build stable releases when upstream release new versions of the emulator. It also builds (~daily) 'edge' builds of main.

They're pushed to the edge channel in the Snap Store. 

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/fab-agon-emulator)

## Install

Install on any [supported Linux](https://snapcraft.io/docs/installing-snapd) distribution easily via:-

`snap install fab-agon-emulator`

## Command line options

```

The Fabulous Agon Emulator!

USAGE:
  fab-agon-emulator [OPTIONS]

OPTIONS:
  -d, --debugger        Enable the eZ80 debugger
  -b, --breakpoint      Set a breakpoint before starting
  -z, --zero            Initialize ram with zeroes instead of random values
  -f, --fullscreen      Start in fullscreen mode
  -h, --help            Prints help information
  -u, --unlimited-cpu   Don't limit eZ80 CPU frequency
  --firmware 1.03       Use 1.03 firmware (default is 1.04)
  --sdcard <path>       Sets the path of the emulated SDCard
  --scale <max-height>  Use perfect (integer) video mode scaling, up to
                        a maximum window height of <max-height>

ADVANCED:
  --mos PATH            Use a different MOS.bin firmware
  --vdp PATH            Use a different VDP dll/so firmware
```