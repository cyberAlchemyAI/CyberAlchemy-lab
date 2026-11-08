"""Stage a distinct locally signed Source8-shaped API30 Work family."""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import stat
import tempfile

ROOT = Path(__file__).resolve().parents[4]
TASK = Path(__file__).resolve().parent
FIXTURE = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture'
NATIVE = FIXTURE / 'native_successor.py'
NATIVE_SHA = '5883653789c20468362f89f1ad723c368100f2ea7c6aa3897a569413fe87f11b'
INPUTS = {
    'product/lab/release-candidates/v1/interface/api-integration-v30/source-manifest.json': 'cfd9a932d87c565c22b915234bbf2a18bfed23f163607b95b96f24b2533e3a16',
    'authority/project-state-transitions/current.json': '12937950af2a00ef329deb1a922275250c61ad199b8f6216eab448e06bf49984',
    'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances/project-state.json': 'cccf18d2966cf0dd494f7d88b054243bb635a91bc84fdcbf5c70709b7b6f8793',
    'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/bundle.json': '8eb940493460ea2c10f50f677d5cbfbd5b898625868af036fb0e594ec9b1b220',
    'implementation/lab-runtime/local-host/t22-api30-episode-inspection-0002/RUN-0003.json': '500270b28b5c07ee740a817f4c42afdd3b51226df227c90445fb76e0c04480ae',
}
EVIDENCE = 'implementation/lab-runtime/local-host/t22-api30-episode-inspection-0002/RUN-0003.json'
API30_REF = 'product/lab/release-candidates/v1/interface/api-integration-v30/source-manifest.json'
STATE_REF = 'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances/project-state.json'
REPLACEMENTS = (
    ("work['name'] = 'Read current scoped Project State'",
     "work['name'] = 'Inspect Lab interface API30 current Project State'"),
    ("work_statement='Generate current bounded views and consume them in a fresh Session under independent permission.'",
     "work_statement='Rework R03 episode 0005: inspect Lab interface API30 against the exact current Project State, consume its bounded Context view in a fresh Session, and report source-pinned discrepancies or an evidence-backed none-found result.'"),
    ("direction='Consume trustworthy current candidate Project State through bounded Context and Ontology Views.'",
     "direction='Inspect the source-pinned Lab interface API30 release candidate against current migration Project State through bounded Context and Ontology Views.'"),
    ("goal_id=GOAL, version=VERSION, name='Fresh same-cut context participation'",
     "goal_id=GOAL, version=VERSION, name='Fresh API30 episode-0005 Project State inspection'"),
    ("outcome='A separately owned source branch can supply trustworthy bounded views to a fresh ephemeral consumer.'",
     "outcome='A fresh bounded consumer sees the exact current migration Project State while inspecting the API30 candidate.'"),
    ("purpose='Define relevance for the exact signed fresh reader Work source cut.'",
     "purpose='Define relevance for the exact signed API30 inspection Work and current migration Project State cut.'"),
    ("intended_uses=['Read current scoped Project State']",
     "intended_uses=['Inspect Lab interface API30 against current Project State']"),
)


def sha(raw): return hashlib.sha256(raw).hexdigest()
def canon(value): return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def safe_read(path, expected):
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents) or not path.is_file():
        raise ValueError('selected input unsafe')
    raw = path.read_bytes()
    if sha(raw) != expected: raise ValueError('selected input changed: ' + str(path))
    return raw


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def rewrite_records(raw):
    text = raw.decode()
    for old, new in REPLACEMENTS:
        if text.count(old) != 1: raise ValueError('staged record anchor differs')
        text = text.replace(old, new)
    anchor = "    work['relation_refs'] = [relation_ref('relation.member-of', 'project', scope)]"
    if text.count(anchor) != 1: raise ValueError('staged Work evidence anchor differs')
    evidence = [API30_REF, STATE_REF, EVIDENCE]
    text = text.replace(anchor, "    work['evidence_refs'] = " + repr(evidence) + "\n" + anchor)
    # The source body must name the exact selected candidate/State bytes, not
    # merely a generic Work statement or an unbound report locator.
    marker = "work['payload'].update(project_ref=scope"
    if text.count(marker) != 1: raise ValueError('staged Work payload anchor differs')
    text = text.replace(marker, "work['claim_ceiling'] = CLAIM + ' API30 manifest cfd9a932d87c565c22b915234bbf2a18bfed23f163607b95b96f24b2533e3a16; current State cccf18d2966cf0dd494f7d88b054243bb635a91bc84fdcbf5c70709b7b6f8793.'\n    " + marker)
    inputs = "input_refs=[INTENT + '@' + VERSION]"
    if text.count(inputs) != 1: raise ValueError('staged Work input anchor differs')
    exact_inputs = [
        'sha256:' + INPUTS[API30_REF] + ':' + API30_REF,
        'sha256:' + INPUTS[STATE_REF] + ':' + STATE_REF,
    ]
    text = text.replace(inputs, "input_refs=[INTENT + '@' + VERSION, " + ', '.join(repr(item) for item in exact_inputs) + "]")
    ast.parse(text)
    return text.encode()


def replace_staged(path, old_sha, new_raw):
    safe_read(path, old_sha)
    temp = path.with_name(path.name + '.t22-' + secrets.token_hex(4))
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(new_raw); stream.flush(); os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists(): temp.unlink()


def load_native():
    safe_read(NATIVE, NATIVE_SHA)
    spec = importlib.util.spec_from_file_location('t22_native_constructor_selected', NATIVE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stage():
    for name, pin in INPUTS.items(): safe_read(ROOT / name, pin)
    native = load_native()
    instance = 'legacy-local-' + secrets.token_hex(8)
    private_home = Path(tempfile.mkdtemp(prefix='cal-T22-api30-source8-', dir='/tmp'))
    if stat.S_IMODE(private_home.stat().st_mode) != 0o700: raise ValueError('private fixture home mode differs')
    base = native.stage(instance, private_home)
    family = Path(base['family'])
    selection_path = family / 'construction-selection.json'
    selection = json.loads(selection_path.read_bytes())
    record_path = family / 'source/records.py'
    row = next((row for row in selection['template_rows'] if row['new']['path'] == record_path.relative_to(ROOT).as_posix()), None)
    if row is None: raise ValueError('staged records selection absent')
    updated_records = rewrite_records(safe_read(record_path, row['new']['sha256']))
    replace_staged(record_path, row['new']['sha256'], updated_records)
    row['new'] = binding(record_path)
    episode_path = family / 'source/episode-contract.json'
    episode = json.loads(episode_path.read_bytes())
    if episode['purpose'] != 'Distinct independently signed legacy diagnostic family; no old identity, Assignment or grant renewal.':
        raise ValueError('staged episode purpose differs')
    episode['purpose'] = 'R03 episode 0005 rework: locally signed API30 current Project State inspection; no original Assignment or grant renewal.'
    replace_staged(episode_path, selection['episode_binding']['sha256'], canon(episode))
    selection['episode_binding'] = binding(episode_path)
    extra = {'schema_version': 'lab-T22-api30-native-source-input/v1', 'work': 'R03 episode 0005 API30 Project State inspection',
             'api30_source_binding': {'path': next(iter(INPUTS)), 'sha256': INPUTS[next(iter(INPUTS))]},
             'current_project_state_binding': {'path': 'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances/project-state.json',
                                               'sha256': INPUTS['authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances/project-state.json']},
             'inspection_receipt_binding': {'path': EVIDENCE, 'sha256': INPUTS[EVIDENCE]},
             'contest_outcome': None, 'lesson_outcome': None, 'authority_effect': 'none'}
    input_path = family / 'source/t22-episode-input.json'
    fd = os.open(input_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(canon(extra)); stream.flush(); os.fsync(stream.fileno())
    selection['t22_episode_input_binding'] = binding(input_path)
    rows = {row['path']: row for row in selection['current_runtime_input_bindings']}
    for name, pin in INPUTS.items():
        value = {'path': name, 'sha256': pin}
        if name in rows and rows[name] != value: raise ValueError('conflicting current source input')
        rows[name] = value
    rows[input_path.relative_to(ROOT).as_posix()] = binding(input_path)
    author_binding = binding(Path(__file__))
    rows[author_binding['path']] = author_binding
    selection['t22_author_binding'] = author_binding
    selection['current_runtime_input_bindings'] = [rows[name] for name in sorted(rows)]
    replace_staged(selection_path, sha(selection_path.read_bytes()), canon(selection))
    receipt = {'schema_version': 'lab-T22-native-source8-stage/v1', 'status': 'STAGED',
               'instance': instance, 'family': family.relative_to(ROOT).as_posix(),
               'source_name': base['source_name'], 'not_before': base['not_before'],
               'expires_at': base['expires_at'], 'constructor_sha256': NATIVE_SHA,
               'construction_selection_binding': binding(selection_path),
               'records_binding': binding(record_path), 'episode_binding': binding(episode_path),
               'episode_input_binding': binding(input_path),
               'private_home_locator_sha256': sha(str(private_home).encode()),
               'source_built': False, 'reader_built': False, 'mapper_built': False,
               'context_built': False, 'native_session_consumed': False,
               'authority_effect': 'none', 'original_t22_complete': False}
    out = TASK / 'STAGE-0001.json'
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(canon(receipt)); stream.flush(); os.fsync(stream.fileno())
    return receipt


def verify():
    raw = (TASK / 'STAGE-0001.json').read_bytes(); row = json.loads(raw)
    if row['status'] != 'STAGED' or row['source_built'] or row['native_session_consumed']:
        raise ValueError('stage receipt state differs')
    family = ROOT / row['family']
    for key in ('construction_selection_binding', 'records_binding', 'episode_binding', 'episode_input_binding'):
        binding_row = row[key]
        safe_read(ROOT / binding_row['path'], binding_row['sha256'])
    selection = json.loads((family / 'construction-selection.json').read_bytes())
    pins = {item['path']: item['sha256'] for item in selection['current_runtime_input_bindings']}
    if not all(pins.get(name) == pin for name, pin in INPUTS.items()):
        raise ValueError('source capture input selection differs')
    if selection['t22_episode_input_binding'] != row['episode_input_binding']:
        raise ValueError('episode input binding differs')
    author_binding = binding(Path(__file__))
    if selection['t22_author_binding'] != author_binding or pins.get(author_binding['path']) != author_binding['sha256']:
        raise ValueError('author code binding differs')
    records = (family / 'source/records.py').read_text()
    if ('Inspect Lab interface API30 current Project State' not in records or
            INPUTS[next(iter(INPUTS))] not in records or INPUTS['authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances/project-state.json'] not in records):
        raise ValueError('source Work meaning differs')
    return row


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--stage', action='store_true');parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.stage == args.verify: raise ValueError('choose one command')
    value = stage() if args.stage else verify()
    print(json.dumps({'status': value['status'], 'instance': value['instance'], 'family': value['family']}, sort_keys=True))


if __name__ == '__main__': main()
