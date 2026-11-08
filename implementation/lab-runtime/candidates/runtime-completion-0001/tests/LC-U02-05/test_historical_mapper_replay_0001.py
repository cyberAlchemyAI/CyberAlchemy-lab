"""Pure/synthetic contract checks. Never invoke Bubblewrap or native code."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from t35_external_v1.phase_scoped_v2 import historical_mapper_replay_0001 as replay


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


class HistoricalMapperReplayContract(unittest.TestCase):
    def test_exact_two_call_argv_and_no_extra_mount(self):
        scratch = Path('/tmp/lc-u02-05-historical-mapper-replay-synthetic')
        first = replay.replay_argv(scratch)
        second = replay.replay_argv(scratch)
        self.assertEqual(first, second)
        replay.validate_replay_argv(scratch, list(first))
        self.assertEqual(first.count('--ro-bind'), 5)
        self.assertEqual(first[-3:], ('/work/package/semantic',
                                      '/work/package/governance',
                                      '/work/package/request.json'))
        self.assertNotIn('--bind', first)
        self.assertNotIn('--dev-bind', first)
        self.assertNotIn('--proc', first)
        for extra in ('--ro-bind-try', '--proc', '--bind'):
            changed = list(first)
            changed.insert(4, extra)
            with self.assertRaises(replay.ContractError):
                replay.validate_replay_argv(scratch, changed)
        with self.assertRaises(replay.ContractError):
            replay.replay_argv(Path('/home/operator/scratch'))

    def test_output_parity_and_closed_process_required(self):
        raw = b'{"synthetic":true}\n'
        with mock.patch.multiple(replay, EXPECTED_STDOUT_BYTES=len(raw),
                                 EXPECTED_STDOUT_SHA256=digest(raw)):
            good = dict(first_closed=True, second_closed=True,
                        first_forced=False, second_forced=False)
            replay.validate_replays(raw, raw, b'', b'', 0, 0, **good)
            cases = [
                (raw, raw + b' ', b'', b'', 0, 0, good),
                (raw, raw, b'error', b'', 0, 0, good),
                (raw, raw, b'', b'', 1, 0, good),
                (raw, raw, b'', b'', 0, 0,
                 dict(good, second_closed=False)),
                (raw, raw, b'', b'', 0, 0,
                 dict(good, first_forced=True)),
            ]
            for first, second, err1, err2, rc1, rc2, flags in cases:
                with self.subTest(case=(err1, err2, rc1, rc2, flags)):
                    with self.assertRaises(replay.ContractError):
                        replay.validate_replays(first, second, err1, err2,
                                                rc1, rc2, **flags)

    def test_synthetic_inventory_closure_and_mutation(self):
        with tempfile.TemporaryDirectory(prefix='mapper-replay-contract-') as tmp:
            root = Path(tmp)
            package = root / 'package'
            package.mkdir(mode=0o700)
            for name in ('semantic', 'governance'):
                (package / name).mkdir(mode=0o700)
            runtime = root / 'runtime'
            runtime.write_bytes(b'fake-runtime')
            runtime.chmod(0o500)
            request = {'selector': {'semantic_cursor': 25},
                       'governance_cursor': 25}
            output = {'cut': {'semantic_cursor': 25},
                      'governance_cursor': 25,
                      'authority_effect': 'none',
                      'governed_nodes': [{}] * 15}
            rows = []
            for name in sorted(replay.expected_names()):
                path = package / name
                if name == 'request.json':
                    raw = json.dumps(request).encode()
                elif name == 'native-output.json':
                    raw = json.dumps(output).encode()
                else:
                    raw = name.encode()
                path.write_bytes(raw)
                path.chmod(0o600)
                rows.append([name, len(raw), digest(raw)])
            inventory = (json.dumps(rows, separators=(',', ':'),
                                    ensure_ascii=True) + '\n').encode()
            options = dict(PACKAGE=package,
                           SELECTED_RUNTIME={runtime: (12, 0o500,
                                                       digest(b'fake-runtime'))},
                           PACKAGE_INVENTORY_SHA256=digest(inventory),
                           PACKAGE_TOTAL_BYTES=sum(row[1] for row in rows),
                           REQUEST_SHA256=digest((package / 'request.json').read_bytes()),
                           EXPECTED_STDOUT_SHA256=digest(
                               (package / 'native-output.json').read_bytes()),
                           EXPECTED_STDOUT_BYTES=(package / 'native-output.json').stat().st_size)
            with mock.patch.multiple(replay, **options):
                self.assertEqual(replay.static_preflight()['package_file_count'], 55)
                (package / 'semantic/00000001.json').write_bytes(b'changed')
                with self.assertRaises(replay.ContractError):
                    replay.static_preflight()
                (package / 'semantic/00000001.json').write_bytes(
                    b'semantic/00000001.json')
                (package / 'extra.json').write_bytes(b'extra')
                with self.assertRaises(replay.ContractError):
                    replay.static_preflight()


if __name__ == '__main__':
    unittest.main()
