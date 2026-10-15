"""Root metadata review; never imports the capture writer or Lab runtime."""
import hashlib
import json
import os
from pathlib import Path
import stat
from jsonschema import Draft202012Validator

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
BASE = RUN / 'T07/final-capture5-inputs-proposal-0001'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
held = {}

def read(row):
    path = Path(row['path'])
    path = path if path.is_absolute() else ROOT / path
    assert path.is_relative_to(ROOT) and path.resolve() == path
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        a = os.fstat(fd)
        assert stat.S_ISREG(a.st_mode)
        parts = []
        while block := os.read(fd, 1024 * 1024):
            parts.append(block)
        body = b''.join(parts)
        b = os.fstat(fd)
        signature = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_mode)
        assert signature(a) == signature(b) == signature(path.stat(follow_symlinks=False))
        assert len(body) == a.st_size and sha(body) == row['sha256'], str(path)
        name = path.relative_to(ROOT).as_posix()
        assert name not in held or held[name] == row['sha256']
        held[name] = row['sha256']
        return body
    finally:
        os.close(fd)

def load(row):
    return json.loads(read(row))

def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}

hh = load({'path': str(BASE / 'HANDOFF.json'), 'sha256': 'dce6d5be23dbc4b32e844468ec53c5f16c6427800f9eed607e4cdde1fa7f6007'})
inputs = load(hh['inputs_binding'])
assert hh['inputs_binding']['sha256'] == '060bec056eec49e0d41296f2086008ff545d08079631ebb380bb5e1d85b1d42e'
assert len(inputs['component_manifests']) == 19 and len(inputs['direct_inputs']) == 115
assert len(inputs['api_expected_files']) == 165 and len(inputs['helper_expected_files']) == 7 and len(inputs['helper_roots']) == 3
assert len(inputs['replacement_bindings']) == 7 and inputs['profile_updates'] == []
for row in inputs['api_expected_files'] + inputs['helper_expected_files'] + inputs['direct_inputs']:
    read(row)
for component in inputs['component_manifests']:
    manifest = load(component)
    for row in manifest['files']:
        path = Path(row['path'])
        path = path if path.is_absolute() else ROOT / component['base'] / path
        read({'path': str(path), 'sha256': row['sha256']})

lineage = load({'path': str(RUN/'T07/api17-task-local-capture-0004/lineage.json'), 'sha256': 'c13bc99371a65b0f0a39aa1418c0eb4c476b05fc94610128840500c9d0d442f1'})
old_source = json.loads((RUN/'T07/api17-task-local-capture-0004/preimage/source-manifest.json').read_bytes())
old_rows = {r['path']: r for r in old_source['files']}
assert len(old_rows) == 27400
overlay = load({'path': str(RUN/'T02/composite-merge-preparation-0004/application-receipt.json'), 'sha256':'3076ebbddd92c3a9f582adbb1dc5cb72b47e0a4b62ae75a1e204f259b229c705'})
selector = load({'path': str(RUN/'T02/selector-merge-0005/application-receipt.json'), 'sha256':'71877e214513ea86b1d963d5e48c2fb49577172ec37a1ececef19688948308f0'})
for pair in inputs['replacement_bindings']:
    old, new = pair['preimage_binding'], pair['postimage_binding']
    assert old['path'] == new['path'] and old_rows[old['path']] == old and old != new
    read(new)

family = inputs['active_family']
runtime = load(family['descriptor_binding'])
assert family['descriptor_binding']['sha256'] == '589d36bce32cfef590e0a01c9fd9ea8873cc16eede8f20e9adb1686f1423deff'
assert family['descriptor_keys'] == sorted(runtime) and runtime['instance'] == 'optimized-0005'
actual = load(family['actual_family_selection_binding'])
assert family['actual_family_selection_binding']['sha256'] == '73a6c61200f4a3489b43d3c6262a675478a752f90da10cdc5d0e62fd9b8b8aa4'
assert actual['family_bindings'] == family['family_bindings'] and actual['phase_reports'] == family['phase_report_bindings']
for key, row in family['family_bindings'].items():
    assert runtime[key] == row
    read(row)
assert len(family['phase_report_bindings']) == 5 and len(family['family_bindings']) == 9
for row in family['phase_report_bindings']:
    report = load(row)
    assert str(report.get('result', '')).startswith('PASS'), row['path']
for pair in family['template_preimages']:
    assert pair['original_binding']['sha256'] == pair['snapshot_binding']['sha256']
    read(pair['snapshot_binding'])
assert family['template_preimages'] == runtime['original_template_preimages']
accepted = load(family['pre_source_acceptance_binding'])
assert family['pre_source_acceptance_binding']['sha256'] == '70b6c59ea26430b02dc5645b72063c7ca1602197153396abefa254e57279dd16'
assert load(accepted['independent_review_binding'])['result'].startswith('PASS')
assert inputs['public_software_manifest_binding']['sha256'] == '5bdd8adba0ffd73ea2ab5121e6a52ce232c86bf398b1ed25c233b7f3bd3e9081'
software = load(inputs['public_software_manifest_binding'])
assert len(software['files']) == 16
for row in software['files']:
    read(row)
assert inputs['guard_binding']['sha256'] == '65ba71adb3b885f6fedc268be29f982f1f03139265f00a7e9ed08ff19b6adeb3'
read(inputs['guard_binding'])
packet = load(hh['Root_packet_template'])
assert packet['status'] is None and packet['inputs'] == inputs
for row in packet['merged_receipt_bindings']:
    read(row)
packet['status'] = 'Root-reviewed-merged-native-family5-ready-for-capture'
schema = json.loads((RUN/'T07/api17-task-local-capture-0005/root-input-packet.schema.json').read_bytes())
Draft202012Validator(schema).validate(packet)
target = RUN/'T00/final-capture5-input-packet-0001.json'
with target.open('x') as stream:
    stream.write(json.dumps(packet, sort_keys=True, indent=2) + '\n')
report = {'schema_version':'lab-T00-capture5-input-root-review/v1-candidate','result':'PASS-selected-input-metadata-and-byte-correspondence','authority_effect':'none','root_packet_binding':binding(target),'proposal_handoff_binding':binding(BASE/'HANDOFF.json'),'selected_public_unique_files_freshly_checked':len(held),'component_manifests':19,'current_API_files':165,'helper_files':7,'same_origin_replacements':7,'original_parent_body_full_guard_performed':False,'limitations':['Independent exact Root packet peer required before capture selection.','Capture writer still must freshly verify every original/current retained body and publish full schema/profile/accounting/source.','No runtime/lease/native/authority qualification.']}
report_path=RUN/'T00/final-capture5-input-root-review-0001.json'
with report_path.open('x') as stream:
    stream.write(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({'result':report['result'],'root_packet_binding':report['root_packet_binding'],'review_binding':binding(report_path),'unique_files':len(held)}))
