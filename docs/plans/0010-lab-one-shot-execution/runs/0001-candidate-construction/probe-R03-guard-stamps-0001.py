"""Measure exact stamp equivalence on authentic source and mutable-buffer stress."""
import argparse
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v30'
KERNEL = API.parent / 'guard-stamps-v1/stamps.py'
SOURCE = RUN / 'guard-stamp-probe-source-0001.json'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def freeze():
    parent = RUN / 'current-Agent-development-observation-failed-proof-0003.json'
    prior = json.loads(parent.read_bytes())
    assert prior['result'] == 'FAIL'
    rows = {row['path']: row for row in prior['files']}
    for path in [parent, KERNEL, Path(__file__)]:
        row = bind(path);rows[row['path']] = row
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    put(SOURCE, {
        'schema_version': 'lab-guard-stamp-equivalence-source/v1-candidate',
        'files': [rows[key] for key in sorted(rows)],
        'api_source_binding': bind(API / 'source-manifest.json'),
        'kernel_binding': bind(KERNEL), 'parent_failed_proof_binding': bind(parent),
        'scope': 'Fresh owned read workspace; no host grant, signing key, Session, source modification, parent callback replacement or admission.',
        'authority_effect': 'none', 'actual_owner_outcome': None
    })
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(SOURCE),
                      'files': len(rows)}), flush=True)


def run(pin):
    assert bind(SOURCE)['sha256'] == pin
    selected = json.loads(SOURCE.read_bytes())
    def guard():
        for row in selected['files']:
            assert bind(ROOT / row['path']) == row, row['path']
    guard()
    spec = importlib.util.spec_from_file_location('_cal_stamp_kernel', KERNEL)
    kernel = importlib.util.module_from_spec(spec);spec.loader.exec_module(kernel)
    name = '_cal_stamp_actual_api30'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py',
                                                submodule_search_locations=[str(API)])
    module = importlib.util.module_from_spec(spec);sys.modules[name] = module;spec.loader.exec_module(module)
    protocol = __import__(name + '.protocol', fromlist=['source'])
    with protocol.source.replay_source('custody-participation') as view:
        parent = view.custody_signed_sources
        rows = list(parent.sources.records.values())
        originals = [row.original for row in rows] + [row.revision_witness.enclosing_original
                     for row in rows if row.revision_witness is not None]
        original_bytes = sum(len(raw) for raw in originals)
        unique = {id(raw): raw for raw in originals if type(raw) is bytes}
        start = time.monotonic();old = parent.record_stamp(rows);old_seconds = time.monotonic() - start
        metrics = {};start = time.monotonic()
        new = kernel.record_stamp(rows, protocol.source.encoded, protocol.source.sha, metrics)
        new_seconds = time.monotonic() - start
        assert new == old, 'real stamp changed'
        # Each invocation reads new immutable objects and current mutable buffers.
        first = rows[0]
        changed = SimpleNamespace(artifact=first.artifact, original=first.original + b' ',
                                  posture=first.posture, source_ref=first.source_ref,
                                  revision_witness=first.revision_witness)
        revised = [changed] + rows[1:]
        revised_stamp = kernel.record_stamp(revised, protocol.source.encoded, protocol.source.sha)
        assert revised_stamp != old and revised_stamp == parent.record_stamp(revised)
        def mutable_rows():
            raw = bytearray(b'A')
            row = SimpleNamespace(artifact={}, original=raw, posture='fixture',
                                  source_ref='fixture:mutable-buffer', revision_witness=None)
            yield row
            raw[:] = b'B'
            yield row
        mutable_metrics = {}
        assert kernel.record_stamp(mutable_rows(), protocol.source.encoded, protocol.source.sha,
                                   mutable_metrics) == parent.record_stamp(mutable_rows())
        assert mutable_metrics['digest_calls'] == 2 and mutable_metrics['immutable_reuses'] == 0
        parent.guard()
        result = {
            'schema_version': 'lab-guard-stamp-equivalence-observation/v1-candidate',
            'result': 'PASS', 'source_binding': bind(SOURCE), 'kernel_binding': bind(KERNEL),
            'actual_original_source_records': len(rows),
            'original_digest_work_bytes': original_bytes,
            'distinct_immutable_byte_objects': len(unique),
            'distinct_immutable_bytes': sum(len(raw) for raw in unique.values()),
            'coalesced_metrics': metrics, 'original_seconds': old_seconds,
            'coalesced_seconds': new_seconds,
            'actual_stamp_sha256': hashlib.sha256(old).hexdigest(),
            'original_and_coalesced_bytes_equal': True,
            'new_invocation_observes_changed_bytes': True,
            'mutable_buffers_rehashed_per_occurrence': True,
            'parent_callbacks_replaced': False, 'runtime_integration_qualified': False,
            'authority_effect': 'none', 'actual_owner_outcome': None,
            'task_complete': False, 'goal_complete': False
        }
    guard()
    put(RUN / 'guard-stamp-probe-result-0001.json', result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser();parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--source-sha256');args = parser.parse_args()
    if args.freeze:
        freeze()
    else:
        run(args.source_sha256)
