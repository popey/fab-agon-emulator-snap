#!/usr/bin/python3
"""Exercise the installed snap with an incompatible saved VDP in a disposable VM."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time

assert Path.home() == Path('/home/ubuntu') and Path('/bin/ghvmctl-runner').exists(), 'Disposable ghvmctl guest required'
name = 'fab-agon-emulator'
common = Path.home() / 'snap' / name / 'common'
installed = Path('/snap') / name / 'current'
report = Path.cwd() / 'artifacts/upgrade'
report.mkdir(parents=True, exist_ok=True)
# Initialize a fresh profile if CI has not launched yet.
subprocess.run(['/snap/bin/' + name, '--help'], check=True, stdout=subprocess.DEVNULL)

def snapshot():
    return {str(p.relative_to(common)): hashlib.sha256(p.read_bytes()).hexdigest()
            for area in ('firmware', 'sdcard') for p in (common / area).rglob('*') if p.is_file()}

before = snapshot()
vdppath = common / 'firmware/vdp_platform.so'
original = vdppath.read_bytes()
assert b'vdp_set_printer_file' in original
# Rename the exported symbol in an otherwise real VDP library. This reproduces
# the old ABI without fetching or redistributing a user's saved firmware.
stale = original.replace(b'vdp_set_printer_file', b'old_set_printer_file')
assert len(stale) == len(original)
marker = common / 'sdcard/.upgrade-preservation-check'
assert not marker.exists()
process = None
try:
    vdppath.write_bytes(stale)
    marker.write_bytes(b'User SD-card content must survive an emulator upgrade.\n')
    profile = snapshot()
    probe = subprocess.run(['/usr/bin/python3', str(installed / 'bin/select-vdp.py'), '--probe', str(vdppath)], capture_output=True)
    assert probe.returncode != 0 and b'vdp_set_printer_file' in probe.stderr, 'Old ABI fixture did not reproduce the missing symbol'
    for launch in (1, 2):
        with (report / f'launch-{launch}.log').open('w') as log:
            process = subprocess.Popen(['/snap/bin/' + name], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            for _ in range(15):
                time.sleep(1)
                assert process.poll() is None, 'Installed emulator exited with saved old firmware'
            # Europa supplies GNOME focus/capture checks; CI also verifies the
            # real emulator survives startup, unlike the pre-fix ABI panic.
            gnome = Path('/home/ubuntu/gnome-window.py')
            if gnome.exists():
                for script, args in ((gnome, []), (gnome, ['--screenshot']), (Path('/home/ubuntu/render-check.py'), [])):
                    subprocess.run(['/usr/bin/python3', str(script), *args], check=True, timeout=120)
                shutil.copy2('/home/ubuntu/window.png', report / f'window-{launch}.png')
                shutil.copy2('/home/ubuntu/window.json', report / f'window-{launch}.json')
                shutil.copy2('/home/ubuntu/render.json', report / f'render-{launch}.json')
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=30)
            process = None
        assert 'saved VDP firmware is missing or incompatible' in (report / f'launch-{launch}.log').read_text()
        assert snapshot() == profile, 'Launch modified saved firmware or SD-card content'
    (report / 'result.json').write_text(json.dumps({'old_abi_reproduced': True, 'launches': 2, 'saved_files_unchanged': True, 'gnome_render_checks': Path('/home/ubuntu/gnome-window.py').exists()}, indent=2))
    print('Installed old-VDP upgrade and reopen checks passed; saved firmware and SD-card files unchanged')
finally:
    if process is not None and process.poll() is None:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=30)
    vdppath.write_bytes(original)
    marker.unlink(missing_ok=True)
assert snapshot() == before, 'Test did not restore the original disposable profile'
