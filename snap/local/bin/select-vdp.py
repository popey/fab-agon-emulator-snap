#!/usr/bin/python3
"""Keep saved firmware, falling back to bundled VDP when its ABI is too old."""
import ctypes
import os
from pathlib import Path
import subprocess
import sys

# Symbols required by upstream 1.2.6 src/vdp_interface.rs. Probe in a child:
# loading an old/custom native library must not crash the launcher itself.
REQUIRED = (
    'vdp_setup', 'vdp_loop', 'signal_vblank', 'copyVgaFramebuffer',
    'set_startup_screen_mode', 'z80_uart0_is_cts', 'z80_send_to_vdp',
    'z80_recv_from_vdp', 'sendVKeyEventToFabgl', 'sendPS2KbEventToFabgl',
    'sendHostMouseEventToFabgl', 'setVdpDebugLogging', 'vdp_set_printer_file',
    'getAudioSamples', 'dump_vdp_mem_stats', 'vdp_shutdown',
)


def compatible(path):
    try:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), '--probe', str(path)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def fallback(args, common, bundled):
    # Explicit firmware paths are the user's choice; leave validation to Fab.
    if any(a in ('--vdp', '-h', '--help') or a.startswith('--vdp=') for a in args):
        return None
    variant = 'platform'
    for i, arg in enumerate(args):
        if arg == '--firmware':
            if i + 1 == len(args):
                return None  # Let the emulator report invalid arguments.
            variant = args[i + 1]
        elif arg.startswith('--firmware='):
            variant = arg.split('=', 1)[1]
    if variant not in ('platform', 'console8', 'electron', 'fb', 'quark'):
        return None
    names = list(dict.fromkeys((f'vdp_{variant}.so', 'vdp_console8.so')))
    # Match upstream's selected-variant then console8 fallback order.
    saved = next((common / name for name in names if (common / name).exists()), None)
    if saved is not None and compatible(saved):
        return None
    for name in names:
        candidate = bundled / name
        if candidate.is_file() and compatible(candidate):
            print(f'Fab Agon: saved VDP firmware is missing or incompatible; using {candidate}. '
                  'Saved firmware and SD-card files are unchanged.', file=sys.stderr)
            return candidate
    raise RuntimeError('No compatible bundled VDP firmware; saved files were not changed')


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--probe':
        library = ctypes.CDLL(sys.argv[2])
        for symbol in REQUIRED:
            getattr(library, symbol)
        return
    args = sys.argv[1:]
    snap = Path(os.environ['SNAP'])
    common = Path(os.environ['SNAP_USER_COMMON'])
    selected = fallback(args, common / 'firmware', snap / 'firmware')
    if selected is not None:
        args = ['--vdp', str(selected), *args]
    executable = str(snap / 'bin/fab-agon-emulator')
    os.execv(executable, [executable, *args])


if __name__ == '__main__':
    main()
