"""One selected public-only Docker fixture; never launches Context."""
import hashlib
import json
import os
from pathlib import Path
import time
import types
import sys

HERE = Path(__file__).resolve().parent
ROOT = Path('/tmp/cal-context-public-child-0002')
DRIVER_SHA = 'aa0893779e1dcba35f2d1e8d6d22538ae8de8cf503bf10ac6d31fcc79b7c28fd'
CHILD_SHA = 'ddcc6471219fa9d38cf5b251ab0aa86cf3c4434b146bea63e1a13bc2413b46d9'


def main():
    if ROOT.exists() or ROOT.is_symlink() or (HERE / 'probe-result.json').exists():
        raise RuntimeError('PROBE_ALREADY_CONSUMED')
    raw = (HERE / 'verify_and_test.py').read_bytes()
    if hashlib.sha256(raw).hexdigest() != DRIVER_SHA:
        raise RuntimeError('DRIVER_PREIMAGE')
    driver = types.ModuleType('_selected_probe_verifier')
    driver.__file__ = str(HERE / 'verify_and_test.py')
    exec(compile(raw, driver.__file__, 'exec'), driver.__dict__)
    if not (sys.flags.no_site and sys.dont_write_bytecode and
            sys.executable == '/usr/bin/python3.14' and
            os.environ.get('PYTHONPYCACHEPREFIX') == driver.GUARD and
            Path(driver.GUARD).is_file() and not Path(driver.GUARD).is_symlink()):
        raise RuntimeError('PROBE_RUNTIME')
    selected, retained = driver.verify()
    adapter = types.ModuleType('_selected_synthetic_adapter')
    adapter.__file__ = str(HERE / 'adapter.py')
    exec(compile(retained['adapter.py'], adapter.__file__, 'exec'), adapter.__dict__)
    began = time.monotonic()
    result = adapter.run(ROOT, CHILD_SHA, seconds=25, docker_probe=True,
                         container_name='cal-context-public-child-0002')
    driver.verify()
    report = {'adapter_result': result, 'observer_state': 'PROVISIONAL',
              'duration_seconds': time.monotonic() - began,
              'selection_sha256': driver.SELECTION_SHA, 'selected_inputs_pre_post': len(selected['input_bindings']),
              'claim': 'one_public_synthetic_Docker_fixture_only',
              'private_body_read': False, 'keys_or_grants': False}
    raw = json.dumps(report, sort_keys=True, indent=2).encode() + b'\n'
    directory = os.open(HERE, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        adapter.durable(directory, 'probe-result.json', raw)
    finally:
        os.close(directory)
    adapter.selected(HERE / 'probe-result.json', hashlib.sha256(raw).hexdigest())
    # The retained record is explicitly provisional. Only the returned/printed
    # report after observer close/readback is a complete observer outcome.
    report['observer_state'] = 'COMPLETE'
    report['observer_result'] = result['result']
    print(json.dumps(report, sort_keys=True), flush=True)
    return 0 if result['result'] == 'PASS_SYNTHETIC_ONLY' else 1


if __name__ == '__main__':
    raise SystemExit(main())
