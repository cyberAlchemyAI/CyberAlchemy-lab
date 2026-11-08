"""Challenge extracted-source/config/tool substitution before Cargo dispatch."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import types
import unittest

E = Path('/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U03-02')
PREFIX = E.parent / 'LC-U01-02/python-bytecode-cache-disabled-0002'
DRIVER = None


def sha(raw): return hashlib.sha256(raw).hexdigest()


def read(path, expected):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        st = os.fstat(stream.fileno())
        if not stat.S_ISREG(st.st_mode) or st.st_size > 1024 * 1024:
            raise ValueError('selected regular input required')
        raw = stream.read(1024 * 1024 + 1)
        if sha(raw) != expected:
            raise ValueError('selected input digest')
        return raw


def put(path, value):
    raw = json.dumps(value, sort_keys=True).encode()
    with path.open('xb') as out: out.write(raw)
    return sha(raw)


class BuildInputTests(unittest.TestCase):
    def fixture(self, root):
        (root / 'cargo-home').mkdir();(root / 'archives').mkdir();(root / 'vendor/fixture-1').mkdir(parents=True)
        raw = b'fn main() { /* exact selected build script */ }'
        (root / 'vendor/fixture-1/build.rs').write_bytes(raw)
        (root / 'archives/fixture-1.crate').write_bytes(b'fixture archive')
        config = b'[net]\noffline=true\n'
        (root / 'cargo-home/config.toml').write_bytes(config)
        files = {'build.rs': sha(raw)}
        put(root / 'vendor/fixture-1/.cargo-checksum.json', {'files': files, 'package': sha(b'fixture archive')})
        return put(root / 'dependency-inputs.json', {'schema_version': 'lab-broker-offline-inputs/v1',
            'tools': DRIVER.host_inputs(), 'config_sha256': sha(config), 'packages': [
                {'name': 'fixture', 'version': '1', 'archive_sha256': sha(b'fixture archive'), 'source_files': files}]})

    def test_injected_build_script_and_coherent_checksum_repin_refuse(self):
        with tempfile.TemporaryDirectory(prefix='owned-input-negative-', dir=E) as temp:
            root = Path(temp);pin = self.fixture(root)
            DRIVER.verify_build_inputs(root, pin)
            changed = b'fn main() { panic!("unselected build script"); }'
            (root / 'vendor/fixture-1/build.rs').write_bytes(changed)
            (root / 'vendor/fixture-1/.cargo-checksum.json').write_text(json.dumps(
                {'files': {'build.rs': sha(changed)}, 'package': sha(b'fixture archive')}))
            with self.assertRaises(ValueError): DRIVER.verify_build_inputs(root, pin)

    def test_new_config_and_extra_vendor_source_refuse(self):
        for changed in ('config', 'source'):
            with tempfile.TemporaryDirectory(prefix='owned-input-negative-', dir=E) as temp:
                root = Path(temp);pin = self.fixture(root)
                if changed == 'config':
                    (root / '.cargo').mkdir();(root / '.cargo/config.toml').write_text('[build]\nrustc="unselected"')
                else: (root / 'vendor/fixture-1/extra.rs').write_text('unselected')
                with self.assertRaises(ValueError): DRIVER.verify_build_inputs(root, pin)

    def test_manifest_replacement_and_symlink_refuse(self):
        with tempfile.TemporaryDirectory(prefix='owned-input-negative-', dir=E) as temp:
            root = Path(temp);pin = self.fixture(root)
            manifest = root / 'dependency-inputs.json'
            original = manifest.read_bytes();manifest.write_text('{}')
            with self.assertRaises(ValueError): DRIVER.verify_build_inputs(root, pin)
            manifest.write_bytes(original)
            source = root / 'vendor/fixture-1/build.rs';copy = root / 'copy.rs';copy.write_bytes(source.read_bytes())
            source.unlink();source.symlink_to(copy)
            with self.assertRaises(OSError): DRIVER.verify_build_inputs(root, pin)

    def test_toolchain_binary_drift_refuses(self):
        with tempfile.TemporaryDirectory(prefix='owned-input-negative-', dir=E) as temp:
            root = Path(temp);program = root / 'compiler';program.write_bytes(b'exact inert fixture')
            manifest = root / 'tools.json'
            pin = put(manifest, {'schema_version': 'lab-control-local-toolchain-inputs/v1',
                'locators': [{'path': str(program), 'resolved_path': str(program)}],
                'files': [{'path': str(program), 'sha256': sha(program.read_bytes()), 'size_bytes': program.stat().st_size}]})
            DRIVER.verify_toolchain(manifest, pin)
            program.write_bytes(b'changed inert fixture')
            with self.assertRaises(ValueError): DRIVER.verify_toolchain(manifest, pin)

    def test_unselected_crate_or_control_source_refuses_before_cargo(self):
        for mutation in ('crate-build-script','control-build-script','nested-source','symlink-source'):
            with tempfile.TemporaryDirectory(prefix='owned-input-negative-',dir=E) as temp:
                root=Path(temp);(root/'control_store/src').mkdir(parents=True);(root/'supervisor').mkdir();crate=root/'tests/LC-U03-02';crate.mkdir(parents=True)
                for name in ('Cargo.toml','Cargo.lock'):(root/'control_store'/name).write_bytes(b'fixture')
                for name in ('lib.rs','codec.rs','custody.rs','ledger.rs'):(root/'control_store/src'/name).write_bytes(b'fixture')
                for name in DRIVER.SUPERVISOR_FILES:(root/'supervisor'/name).write_bytes(b'fixture')
                for name in DRIVER.SOURCE_FILES:(crate/name).write_bytes(b'fixture')
                DRIVER.validate_source_inventory(root)
                if mutation=='crate-build-script':(crate/'build.rs').write_text('fn main(){panic!("must never run");}')
                elif mutation=='control-build-script':(root/'control_store/build.rs').write_text('fn main(){panic!("must never run");}')
                elif mutation=='nested-source':(crate/'src').mkdir();(crate/'src/main.rs').write_text('fn main(){}')
                else:(crate/'lib.rs').unlink();(crate/'lib.rs').symlink_to(crate/'tests.rs')
                calls=[];original_s=DRIVER.S;original_popen=DRIVER.subprocess.Popen
                def forbidden(*args,**kwargs):calls.append(True);raise RuntimeError('Cargo unexpectedly invoked')
                DRIVER.S=root;DRIVER.subprocess.Popen=forbidden
                try:
                    with self.assertRaises(ValueError):DRIVER.command(root,{'cargo':'unselected'},['test','--offline','--locked'],'negative')
                    self.assertEqual(calls,[]);self.assertFalse((root/'negative.stdout').exists())
                finally:DRIVER.S=original_s;DRIVER.subprocess.Popen=original_popen


if __name__ == '__main__':
    parser = argparse.ArgumentParser();parser.add_argument('--driver', type=Path, required=True)
    parser.add_argument('--driver-sha', required=True);args = parser.parse_args()
    read(PREFIX, 'a5712f1655f68e6f8fe7cacbfb454dc0be0cd1ad8f22f1788fbad7b8adafae29')
    if os.environ.get('PYTHONPYCACHEPREFIX') != str(PREFIX) or not sys.flags.no_site or not sys.dont_write_bytecode:
        raise ValueError('guarded Python required')
    raw = read(args.driver, args.driver_sha)
    DRIVER = types.ModuleType('selected_build_driver');DRIVER.__file__ = str(args.driver)
    exec(compile(raw, str(args.driver), 'exec'), DRIVER.__dict__)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(BuildInputTests))
    print(json.dumps({'schema_version': 'lab-case-command-result/v1', 'result': 'PASS' if result.wasSuccessful() else 'FAIL',
        'checks': result.testsRun, 'effect_state': 'owned-inert', 'cleanup': 'clean'}))
    raise SystemExit(0 if result.wasSuccessful() else 1)
