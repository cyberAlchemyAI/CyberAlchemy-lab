"""Bounded, executable transport check against the selected API40 T06 SDK."""
import argparse
from contextlib import contextmanager
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import sys
import time
import types

ROOT = Path(__file__).resolve().parents[4]
TASK = Path(__file__).resolve().parent
API = 'product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001'
SDK = 'product/lab/release-candidates/v1/interface/composite-operator-v1-current-api40-0001/revision-0001'
PINS = {
    API + '/source-manifest.json': '45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219',
    API + '/contract-profile.json': 'cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614',
    SDK + '/source-manifest.json': 'f123c4e02828c1c3f88dfc4b74adc3bdf1cc2919bc53df8ccf68e00ff677da1e',
    SDK + '/control.py': '55ae5447a6c81125aca5c79dab60d533c170e46c69eae5e4c71830ed548302aa',
    SDK + '/framing.py': '7fb574ea87548a70b3607e0b6b42b04bc3fa49d198c916c634703a0065138317',
}
LIVE = 'implementation/lab-runtime/local-host/t06-api40-rebind-0001/RUN-LIVE-EFFECTS-0002.json'
LIVE_SHA = '7bac9d32cad2aa5081ede012ac3d70b0f139b7c166482638954c9a83902f7d5b'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def exact(root, name, expected):
    """Capture selected regular bytes without following any relative-path link."""
    rel = Path(name)
    if rel.is_absolute() or '..' in rel.parts or rel.as_posix() != name:
        raise ValueError('unsafe selected path')
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('unsafe selected root')
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in rel.parts[:-1]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        leaf = os.open(rel.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            before = os.fstat(leaf)
            if not stat.S_ISREG(before.st_mode):
                raise ValueError('nonregular selected file')
            with os.fdopen(os.dup(leaf), 'rb') as stream:
                raw = stream.read(8 * 1024 * 1024 + 1)
            after = os.fstat(leaf)
            if (len(raw) > 8 * 1024 * 1024 or before.st_size != len(raw) or
                    (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) !=
                    (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) or
                    digest(raw) != expected):
                raise ValueError('selected bytes changed')
            return raw
        finally:
            os.close(leaf)
    except OSError as error:
        raise ValueError('unsafe selected path') from error
    finally:
        os.close(fd)


def selected(root=ROOT):
    raw = {name: exact(root, name, sha) for name, sha in PINS.items()}
    source = json.loads(raw[API + '/source-manifest.json'])
    profile = json.loads(raw[API + '/contract-profile.json'])
    sdk = json.loads(raw[SDK + '/source-manifest.json'])
    if source['profile_binding'] != {'path': API + '/contract-profile.json',
                                      'sha256': PINS[API + '/contract-profile.json']}:
        raise ValueError('source/profile binding differs')
    if len(profile['files']) != 33424 or len({row['path'] for row in profile['files']}) != 33424:
        raise ValueError('selected API40 profile shape differs')
    indexed = {row['path']: row for row in profile['files']}
    if indexed.get(SDK + '/source-manifest.json', {}).get('sha256') != PINS[SDK + '/source-manifest.json']:
        raise ValueError('SDK manifest not selected by API40 profile')
    sdk_names = set(PINS) - {API + '/source-manifest.json', API + '/contract-profile.json'}
    if len(sdk['files']) != 6 or len({row['path'] for row in sdk['files']}) != 6:
        raise ValueError('SDK inventory differs')
    for row in sdk['files']:
        name = row['path']
        if name not in indexed or indexed[name] != row:
            raise ValueError('SDK file not selected by API40 profile')
        if name in sdk_names:
            if row['sha256'] != PINS[name] or len(raw[name]) != row['size_bytes']:
                raise ValueError('SDK file digest/size differs')
        else:
            exact(root, name, row['sha256'])
    live = json.loads(exact(root, LIVE, LIVE_SHA))
    if (live['driver_sha256'] != 'ced8b82be6a6ca77562b1d900b7dca122e3e1ecefbd06e428a5e4c0bd50b7cec' or
            live['profile_sha256'] != PINS[API + '/contract-profile.json'] or
            live['process_exit_code'] != 0 or live['result']['status'] != 'PASS' or
            live['result']['dispatch_operations_executed'] != 7):
        raise ValueError('live T06 predecessor differs')
    obs = live['result']['observations']
    if not (len(obs) == 7 and obs[2]['counter_after'] == obs[3]['counter_after'] == obs[4]['counter_after'] == 1 and
            obs[4]['branch'] == 'actions' and obs[4]['case'] == 'wrong-scope-refusal' and
            obs[4]['operation'] == 'action.dispatch' and obs[4]['reply_kind'] == 'error' and
            obs[4]['code'] == 'unauthorized'):
        raise ValueError('live Action effect/refusal differs')
    return raw


@contextmanager
def selected_modules(raw):
    """Execute exact selected source bytes, restoring process import state."""
    prior = {name: sys.modules.get(name) for name in ('control', 'framing')}
    modules = {}
    try:
        for name in ('control', 'framing'):
            path = SDK + '/' + name + '.py'
            module = types.ModuleType(name)
            module.__file__ = str(ROOT / path)
            sys.modules[name] = module
            exec(compile(raw[path], module.__file__, 'exec'), module.__dict__)
            modules[name] = module
        yield modules
    finally:
        for name, old in prior.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old


def output_budget_case(write):
    output = io.BytesIO()
    try:
        write(output, {'data': 'X' * 100}, 8)
    except ValueError as error:
        if str(error) != 'output frame budget exceeded' or output.getvalue():
            raise ValueError('output budget refusal not causal') from error
        return {'case': 'output-budget', 'effect_calls': 0, 'output_bytes': 0}
    raise ValueError('output budget accepted')


def cases(root=ROOT):
    raw = selected(root)
    with selected_modules(raw) as selected_code:
        framing = selected_code['framing']
        rows = []

        class Service:
            def __init__(self): self.calls = []
            def call(self, request):
                self.calls.append(request)
                return {'kind': 'result', 'request_sha256': digest(request)}

        def refuse(name, wire, *, limit=64, frames=4, bytes_budget=1024, expected):
            service = Service()
            reader = framing.Reader(io.BytesIO(wire), max_frames=frames, max_wire_bytes=bytes_budget)
            output = io.BytesIO()
            try:
                framing.dispatch(service, reader, output, limit, 1024)
            except framing.FrameError as error:
                if error.code != expected or service.calls or output.getvalue():
                    raise ValueError('transport refusal not causal: ' + name)
                rows.append({'case': name, 'code': error.code, 'effect_calls': 0,
                             'wire_sha256': digest(wire), 'output_bytes': 0})
            else:
                raise ValueError('transport accepted: ' + name)

        service = Service()
        wire = b'{"kind":"call", "n":1} \r\n{"kind":"call","n":2}\n'
        output = io.BytesIO()
        if framing.dispatch(service, framing.Reader(io.BytesIO(wire), max_frames=4, max_wire_bytes=1024),
                            output, 64, 1024) != 0:
            raise ValueError('normal dispatch did not finish')
        expected_requests = [b'{"kind":"call", "n":1} \r', b'{"kind":"call","n":2}']
        if service.calls != expected_requests:
            raise ValueError('dispatch changed raw request bytes')
        replies = [json.loads(line) for line in output.getvalue().splitlines()]
        if [row['request_sha256'] for row in replies] != [digest(item) for item in expected_requests]:
            raise ValueError('dispatch response binding differs')
        rows.append({'case': 'exact-raw-dispatch', 'effect_calls': 2,
                     'wire_sha256': digest(wire), 'output_sha256': digest(output.getvalue())})
        refuse('partial-frame', b'{"kind":"call"}', expected='partial-frame')
        refuse('oversized-frame', b'X' * 65 + b'\n', expected='input-too-large')
        refuse('wire-budget', b'{"kind":"call"}\n', bytes_budget=5,
               expected='transport-budget-exhausted')
        service = Service()
        output = io.BytesIO()
        wire = b'{"n":1}\n{"n":2}\n'
        try:
            framing.dispatch(service, framing.Reader(io.BytesIO(wire), max_frames=1,
                                                      max_wire_bytes=1024), output, 64, 1024)
        except framing.FrameError as error:
            if error.code != 'transport-budget-exhausted' or service.calls != [b'{"n":1}'] or len(output.getvalue().splitlines()) != 1:
                raise ValueError('frame budget did not stop second effect')
            rows.append({'case': 'frame-budget', 'code': error.code, 'effect_calls': 1,
                         'wire_sha256': digest(wire), 'output_sha256': digest(output.getvalue())})
        else:
            raise ValueError('second frame accepted')
        read_fd, write_fd = os.pipe()
        try:
            with os.fdopen(read_fd, 'rb', buffering=0) as pending:
                try:
                    framing.Reader(pending, max_frames=4, max_wire_bytes=1024).receive(64, time.monotonic() - 1)
                except framing.FrameError as error:
                    if error.code != 'startup-deadline-exceeded':
                        raise ValueError('past deadline refused for wrong reason')
                    rows.append({'case': 'startup-deadline', 'code': error.code, 'effect_calls': 0,
                                 'output_bytes': 0})
                else:
                    raise ValueError('past startup deadline accepted')
        finally:
            os.close(write_fd)
        # An output budget refusal occurs before writing any response bytes.
        rows.append(output_budget_case(framing.write))
    return rows


def result(root=ROOT):
    rows = cases(root)
    if [row['case'] for row in rows] != ['exact-raw-dispatch', 'partial-frame', 'oversized-frame',
                                        'wire-budget', 'frame-budget', 'startup-deadline', 'output-budget']:
        raise ValueError('case inventory differs')
    return {'schema_version': 'lab-T18-current-T06-framing-slice/v1', 'status': 'PASS',
            'api_source_sha256': PINS[API + '/source-manifest.json'],
            'api_profile_sha256': PINS[API + '/contract-profile.json'],
            'sdk_manifest_sha256': PINS[SDK + '/source-manifest.json'],
            'live_t06_receipt_sha256': LIVE_SHA,
            'runner_sha256': digest((TASK / 'boundary.py').read_bytes()),
            'test_sha256': digest((TASK / 'test_boundary.py').read_bytes()),
            'cases': rows, 'local_framing_slice_passed': True,
            'cross_branch_proof_qualified': False, 'same_family_t18_complete': False,
            'authority_effect': 'none'}


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.write == args.verify: raise ValueError('select --write or --verify')
    output = TASK / 'RESULT-0002.json'
    payload = canonical(result())
    if args.write:
        fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        parent = os.open(TASK, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try: os.fsync(parent)
        finally: os.close(parent)
    else:
        if exact(TASK, 'RESULT-0002.json', digest(payload)) != payload:
            raise ValueError('result differs')
    print('PASS: seven selected T06 framing cases')


if __name__ == '__main__':
    main()
