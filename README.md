# fab-agon-emulator-snap
[![fab-agon-emulator](https://github.com/popey/fab-agon-emulator-snap/actions/workflows/test-snap-can-build.yml/badge.svg)](https://github.com/popey/fab-agon-emulator-snap/actions)
## Snap of the Fab Agon Emulator

[![fab-agon-emulator](https://snapcraft.io/fab-agon-emulator/badge.svg)](https://snapcraft.io/fab-agon-emulator)
[![fab-agon-emulator](https://snapcraft.io/fab-agon-emulator/trending.svg?name=0)](https://snapcraft.io/fab-agon-emulator)

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

### Saved firmware after an emulator update

The launcher keeps your writable firmware and SD-card files in
`~/snap/fab-agon-emulator/common/`. If a saved VDP library cannot provide the
interface required by the emulator, the launcher uses the matching bundled VDP
for that run and prints a diagnostic. It does not overwrite the saved library,
MOS firmware, or SD-card files. Compatible custom VDP libraries remain in use.
An explicit `--vdp PATH` override is passed through unchanged.

Launcher regressions: `python3 -m unittest discover -s tests -v` (requires a C
compiler). The installed upgrade regression runs only in a disposable ghvmctl
VM; it simulates the missing `vdp_set_printer_file` export and checks two real
launches while verifying saved-file hashes.
