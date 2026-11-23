import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('selector', ROOT / 'snap/local/bin/select-vdp.py')
selector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(selector)


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.snap = self.root / 'snap'
        self.common = self.root / 'common'
        (self.snap / 'bin').mkdir(parents=True)
        (self.snap / 'firmware').mkdir()
        (self.snap / 'sdcard').mkdir()
        self.common.mkdir()
        for name in ('launch', 'select-vdp.py'):
            shutil.copy2(ROOT / 'snap/local/bin' / name, self.snap / 'bin' / name)
        self.compile(self.snap / 'firmware/vdp_platform.so', selector.REQUIRED)
        shutil.copy2(self.snap / 'firmware/vdp_platform.so', self.snap / 'firmware/vdp_console8.so')
        (self.snap / 'firmware/mos_platform.bin').write_bytes(b'bundled MOS')
        (self.snap / 'sdcard/example.bas').write_bytes(b'PRINT "HELLO"')
        exe = self.snap / 'bin/fab-agon-emulator'
        exe.write_text('#!/usr/bin/python3\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n')
        exe.chmod(0o755)
        self.env = dict(os.environ, SNAP=str(self.snap), SNAP_USER_COMMON=str(self.common))

    def compile(self, path, symbols):
        source = ''.join(f'void {symbol}(void) {{}}\n' for symbol in symbols)
        subprocess.run(['cc', '-shared', '-fPIC', '-x', 'c', '-o', str(path), '-'], input=source, text=True, check=True)

    def launch(self, *args, check=True):
        return subprocess.run(['bash', str(self.snap / 'bin/launch'), *args], env=self.env,
                              capture_output=True, text=True, check=check)

    def snapshot(self):
        return {str(p.relative_to(self.common)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.common.rglob('*') if p.is_file()}

    def seed(self):
        self.launch('--help')
        (self.common / 'firmware/mos_platform.bin').write_bytes(b'custom MOS')
        (self.common / 'sdcard/example.bas').write_bytes(b'custom program')
        (self.common / 'sdcard/my-file').write_bytes(b'keep me')

    def test_fresh_profile_initializes_and_preserves_arguments(self):
        self.assertEqual(json.loads(self.launch('--scale', '2').stdout), ['--scale', '2'])
        self.assertEqual((self.common / 'firmware/mos_platform.bin').read_bytes(), b'bundled MOS')
        self.assertTrue((self.common / 'sdcard/example.bas').exists())

    def test_old_abi_falls_back_without_changing_existing_profile(self):
        self.seed()
        old = self.common / 'firmware/vdp_platform.so'
        self.compile(old, [s for s in selector.REQUIRED if s != 'vdp_set_printer_file'])
        before = self.snapshot()
        for _ in range(2):
            result = self.launch('--scale', '2')
            self.assertEqual(json.loads(result.stdout), ['--vdp', str(self.snap / 'firmware/vdp_platform.so'), '--scale', '2'])
            self.assertIn('incompatible', result.stderr)
            self.assertEqual(self.snapshot(), before)

    def test_compatible_custom_library_is_preserved_and_selected(self):
        self.seed()
        self.compile(self.common / 'firmware/vdp_platform.so', [*selector.REQUIRED, 'custom_marker'])
        before = self.snapshot()
        self.assertEqual(json.loads(self.launch().stdout), [])
        self.assertEqual(self.snapshot(), before)

    def test_explicit_override_and_help_are_unchanged(self):
        self.seed()
        for args in [('--vdp', '/custom/vdp.so'), ('--vdp=/custom/vdp.so',), ('--help',)]:
            self.assertEqual(json.loads(self.launch(*args).stdout), list(args))

    def test_variant_uses_matching_bundled_library(self):
        self.seed()
        self.compile(self.common / 'firmware/vdp_electron.so', [])
        shutil.copy2(self.snap / 'firmware/vdp_platform.so', self.snap / 'firmware/vdp_electron.so')
        args = json.loads(self.launch('--firmware', 'electron').stdout)
        self.assertEqual(args[:2], ['--vdp', str(self.snap / 'firmware/vdp_electron.so')])

    def test_missing_variant_uses_compatible_saved_console8(self):
        self.seed()
        self.assertEqual(json.loads(self.launch('--firmware', 'fb').stdout), ['--firmware', 'fb'])

    def test_broken_bundled_library_fails_without_touching_data(self):
        self.seed()
        for base in (self.common, self.snap):
            for path in (base / 'firmware').glob('vdp_*.so'):
                path.write_bytes(b'not an ELF library')
        before = self.snapshot()
        result = self.launch(check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('No compatible bundled VDP', result.stderr)
        self.assertEqual(self.snapshot(), before)


if __name__ == '__main__':
    unittest.main()
