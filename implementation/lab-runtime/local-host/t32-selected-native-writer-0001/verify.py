#!/usr/bin/env python3
"""Read-only cold verifier for the frozen selected-writer interruption run."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUNNER = '847515e5f767c907bd0c0ee1afd9ff71d0bfb126cfa8e3dbd50983eb5800c8b1'
LAUNCHER = '5d2b0b43640711b3f9af6c1c8d06cd6022d73d188a588d6d2435e822d8953fe1'
RECEIPTS = {'RESULT-0002.json': '7da4b39b1f993781c6ece28ba72ffece11123151f0e8b6aa24f4d4bfb419e0c3',
            'RESULT-OPT-0002.json': 'bdf376884077a5e677aea5d144a1d2c747895cbc407123c50d6ff8259cb66f41'}
SOURCES = {
    'implementation/lab-runtime/local-host/t32-selected-native-writer-0001/run.py': RUNNER,
    'implementation/lab-runtime/local-host/t32-selected-native-writer-0001/launch.py': LAUNCHER,
    'implementation/lab-runtime/local-host/t32-selected-native-writer-0001/capabilities.py': '9293f3bdb9aefde1e569803140195a457b051115522af2fde6c2593bbe16f944',
    'product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001/fixtures.py': '34b260f26d21166b14298d7535e18ad39d60676c08f1590d246e20a03b9f2cbf',
    'product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001/bin-production/lab-ontology-native': '57416d01d3479238f9e76a967c0275f1af04466efeb130fc0125bcb94e3a3399',
    'product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001/build-observer/debug/lab-ontology-native': '19cc878e98357a0e23136979c470ef21cf9479287047b8ebfee8139dd5f676d4',
    'implementation/lab-ontology/candidates/v1/adapters/lifecycle/native_store.py': '8d61ae200155fefe4e87c3d303e03a6314465d639089708cef91174efa556138',
    'implementation/lab-ontology/candidates/v1/adapters/represented_subjects.py': '8aea7147b349a73beebcaefe9bf8fa3ac7e5083ca74bb52962e6e604fd02d9c1',
    'implementation/lab-ontology/candidates/v1/adapters/lifecycle/translation.py': 'ee12db294bbf4deff637107635b95ab9f71924f1ae47bc556785875f6798d585',
    'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-original55-execution-preparation-0002/factory/__init__.py': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-original55-execution-preparation-0002/factory/private_io.py': 'b970a0ff9b56f03499f5fb7feb88974a90a029d080a185b417dcb1d03e7b16ec',
    'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-original55-execution-preparation-0002/factory/generation_store.py': '18166ca54455cdaa0005113c07c8e0eabb5369d8431daa204595d5aa0c1e8982',
    'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-original55-execution-preparation-0002/factory/selected_store.py': '4d8f345cd7d4eb27e7dd291bc039197fc90471f1ab762bfa8fba319ffa7487bd',
}
CASES = [(family, stage) for family in ('semantic', 'governance')
         for stage in ('after-lock', 'after-first-link', 'before-cleanup')]
CASES += [('none', 'before-head-commit'), ('none', 'after-head-commit')]


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    need(path.is_file() and not path.is_symlink(), 'regular unlinked selected file required: ' + str(path))
    return path.read_bytes()


def assess(raw, expected_sha):
    need(sha(raw) == expected_sha, 'selected receipt bytes changed')
    value = json.loads(raw)
    need(type(value) is dict and set(value) == {'authority_effect', 'capabilities_sha256', 'cases',
         'fixture_sha256', 'generation_store_sha256', 'limits', 'observer_executable_sha256',
         'original_native_store_sha256', 'production_executable_sha256', 'result',
         'runner_sha256', 'scope', 'selected_factory_sha256'}, 'receipt shape differs')
    need(value['result'] == 'PASS' and value['authority_effect'] == 'none'
         and value['scope'] == 'selected native lifecycle append and detached recovery technical fixture',
         'receipt outcome or scope differs')
    for field, expected in (
        ('runner_sha256', RUNNER), ('capabilities_sha256', SOURCES['implementation/lab-runtime/local-host/t32-selected-native-writer-0001/capabilities.py']),
        ('fixture_sha256', SOURCES['product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001/fixtures.py']),
        ('generation_store_sha256', SOURCES['docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-original55-execution-preparation-0002/factory/generation_store.py']),
        ('selected_factory_sha256', SOURCES['docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-original55-execution-preparation-0002/factory/selected_store.py']),
        ('original_native_store_sha256', SOURCES['implementation/lab-ontology/candidates/v1/adapters/lifecycle/native_store.py']),
        ('production_executable_sha256', SOURCES['product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001/bin-production/lab-ontology-native']),
        ('observer_executable_sha256', SOURCES['product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001/build-observer/debug/lab-ontology-native'])):
        need(value[field] == expected, 'receipt source binding differs: ' + field)
    need(type(value['cases']) is list and len(value['cases']) == 8, 'eight selected kills required')
    for row, (family, stage) in zip(value['cases'], CASES):
        need(type(row) is dict and set(row) == {'stage', 'family', 'child_exit', 'old_head_sha256',
             'new_head_sha256', 'control_sha256', 'semantic_events', 'governance_events',
             'foreign_preserved', 'foreign_residue_refusal', 'production_cold_read',
             'exact_retry_idempotent'}, 'case shape differs')
        need(row['family'] == family and row['stage'] == stage and row['child_exit'] == -9
             and row['semantic_events'] == row['governance_events'] == 2
             and row['foreign_preserved'] is True and row['production_cold_read'] is True
             and row['exact_retry_idempotent'] is True, 'selected kill result differs')
        for field in ('old_head_sha256', 'new_head_sha256', 'control_sha256'):
            digest = row[field]
            need(type(digest) is str and len(digest) == 64
                 and all(char in '0123456789abcdef' for char in digest), 'case digest differs')
        need(row['old_head_sha256'] != row['new_head_sha256'], 'native commit did not advance HEAD')
        refusal = row['foreign_residue_refusal']
        if stage == 'after-head-commit':
            need(refusal is None, 'post-commit foreign residue claim differs')
        else:
            need(refusal == {'type': 'ValueError', 'message': 'unknown generation file'},
                 'foreign residue refusal differs')
    need(value['limits'] == ['No real source/issuer grant', 'No real rich translation',
         'No API ontology.project writer claim', 'No host power-loss simulation'],
         'receipt limits differ')
    return value


def verify():
    for relative, digest in SOURCES.items():
        need(sha(read(ROOT / relative)) == digest, 'selected code or executable changed: ' + relative)
    results = []
    for name, digest in RECEIPTS.items():
        results.append(assess(read(HERE / name), digest))
    return {'result': 'PASS', 'receipts': len(results), 'cases_per_receipt': 8,
            'selected_sources': len(SOURCES)}


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True))
