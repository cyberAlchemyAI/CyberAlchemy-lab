"""Stage one fresh technical Source family with an Agent challenge contract.

This stages a separate locally signed family. It neither authorizes a challenge
API call nor changes the selected T22 Session family or repository authority.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import secrets
import stat
import tempfile
import types

ROOT = Path(__file__).resolve().parents[4]
TASK = Path(__file__).resolve().parent
FIXTURE = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture'
PREDECESSOR = ROOT / 'implementation/lab-runtime/local-host/t22-native-source8-successor-0004/author.py'
PREDECESSOR_SHA = '571cda2950b6fb82adf005950692d4f6fdb149a8dcdcfc0f0f6b431e1b9c68ec'
FOUNDATION = 'authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/challenge-contract.json'
SCHEMA = 'authority/artifact-types/challenge-contract/v1/schema.json'
SESSION = 'implementation/lab-runtime/local-host/t22-native-source8-successor-0004/LIVE-SESSION-0002.json'
INPUTS = {
    FOUNDATION: '4676fef673b07d876a8fe3928b2e69cc8a8f509539b87fc7ebc2f77953b04d1d',
    SCHEMA: '11b325313331223aecd408aba0f23f2ec20f4914e134a2efb23103b2e2dd8322',
    SESSION: 'ff8a148e377df505d0d24f67d3f3348e174401c9ba2f2814a4bd032116edd645',
}

def sha(raw): return hashlib.sha256(raw).hexdigest()
def canon(value): return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()

def safe_read(path, expected):
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents) or not path.is_file():
        raise ValueError('selected input unsafe')
    raw = path.read_bytes()
    if sha(raw) != expected: raise ValueError('selected input changed: ' + str(path))
    return raw

def selected_predecessor():
    raw = safe_read(PREDECESSOR, PREDECESSOR_SHA)
    module = types.ModuleType('t22_selected_predecessor_author')
    module.__file__ = str(PREDECESSOR)
    exec(compile(raw, str(PREDECESSOR), 'exec'), module.__dict__)
    return module

CONTRACT_CODE = '''    contract = common('challenge-contract', 'challenge-contract:' + PREFIX + '-agent-contest', scope)
    contract['name'] = 'Fresh API30 Work Agent contest contract'
    contract['lifecycle_state'] = 'candidate'
    contract['challenge_route'] = 'route:repository-owner-review'
    contract['claim_ceiling'] = 'Locally signed candidate contract for one fresh Work contest. No challenge submission, response, resolution, owner decision, or authority effect is implied.'
    contract['evidence_refs'] = [
        'product/lab/release-candidates/v1/interface/api-integration-v30/source-manifest.json',
        'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances/project-state.json',
        'implementation/lab-runtime/local-host/t22-native-source8-successor-0004/LIVE-SESSION-0002.json']
    contract['relation_refs'] = [relation_ref('relation.governed-by', 'policy', POLICY)]
    contract['payload'].update(
        policy_ref=POLICY,
        challengeable_subject_kinds=['work'],
        eligible_challenger_kinds=['agent-instance'],
        grounds=['evidence-conflict', 'scope-error', 'stale-projection'],
        required_evidence_kinds=['source', 'validation-receipt', 'decision'],
        response_modes=['evidence', 'contradiction', 'revision', 'owner-review'],
        owner_route='route:repository-owner-review',
        resolution_gate_ref='gate:explicit-owner-decision',
        response_period='before-dependent-admission-or-on-next-state-transition',
        unresolved_residue_route='route:R03-0005-agent-contest-residue')
'''

def rewrite_records(raw, predecessor):
    text = predecessor.rewrite_records(raw).decode()
    anchor = "    return {'principal': principal, 'principal-reference': principal_reference, 'intent': intent, 'goal': goal, 'work': work, 'agent-profile': profile,"
    if text.count(anchor) != 1: raise ValueError('contract insertion anchor differs')
    text = text.replace(anchor, CONTRACT_CODE + anchor.replace("'agent-profile': profile,", "'challenge-contract': contract, 'agent-profile': profile,"))
    ast.parse(text)
    return text.encode()

BUILD_REPLACEMENTS = (
    ("len(items)==21,'all eleven sources and ten Typed Relations required'", "len(items)==22,'all twelve sources and ten Typed Relations required'"),
    ("len(cores)==21 and post!=before['projection'],'twenty-one independent prospective cores required'", "len(cores)==22 and post!=before['projection'],'twenty-two independent prospective cores required'"),
    ("'authored_current_artifacts':11", "'authored_current_artifacts':12"),
    ("'independent_participation_decision_cores':21", "'independent_participation_decision_cores':22"),
    ("'actual_original_targets':23,'records':21", "'actual_original_targets':24,'records':22"),
)

def rewrite_build(raw):
    text = raw.decode()
    for old, new in BUILD_REPLACEMENTS:
        if text.count(old) != 1: raise ValueError('source count anchor differs: ' + old)
        text = text.replace(old, new)
    ast.parse(text)
    return text.encode()

def check_contract(body, scope, prefix):
    if body['kind'] != 'challenge-contract' or body['node_id'] != 'challenge-contract:' + prefix + '-agent-contest':
        raise ValueError('candidate contract identity differs')
    if body['scope_ref'] != scope or body['authority_effect'] != 'none':
        raise ValueError('candidate contract scope/effect differs')
    payload = body['payload']
    if payload['challengeable_subject_kinds'] != ['work'] or payload['eligible_challenger_kinds'] != ['agent-instance']:
        raise ValueError('candidate contest eligibility differs')
    if body['lifecycle_state'] != 'candidate' or payload['resolution_gate_ref'] != 'gate:explicit-owner-decision':
        raise ValueError('candidate decision boundary differs')
    import jsonschema
    jsonschema.Draft202012Validator(json.loads(safe_read(ROOT / SCHEMA, INPUTS[SCHEMA]))).validate(body)
    return body

def binding(path): return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}

def replace_staged(path, old_sha, new_raw):
    safe_read(path, old_sha)
    temp = path.with_name(path.name + '.t22-contest-' + secrets.token_hex(4))
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(new_raw); stream.flush(); os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists(): temp.unlink()

def stage():
    for name, pin in INPUTS.items(): safe_read(ROOT / name, pin)
    predecessor = selected_predecessor()
    native = predecessor.load_native()
    instance = 'legacy-local-' + secrets.token_hex(8)
    private_home = Path(tempfile.mkdtemp(prefix='cal-T22-agent-contest-', dir='/tmp'))
    if stat.S_IMODE(private_home.stat().st_mode) != 0o700: raise ValueError('private fixture home mode differs')
    base = native.stage(instance, private_home)
    family = Path(base['family'])
    selection_path = family / 'construction-selection.json'
    selection = json.loads(selection_path.read_bytes())
    rows = {row['new']['path']: row for row in selection['template_rows']}
    def change(relative, transform):
        path = family / relative
        row = rows.get(path.relative_to(ROOT).as_posix())
        if row is None: raise ValueError('staged template row absent: ' + relative)
        old_sha = row['new']['sha256']
        replace_staged(path, old_sha, transform(safe_read(path, old_sha)))
        row['new'] = binding(path)
        return path
    records = change('source/records.py', lambda raw: rewrite_records(raw, predecessor))
    build = change('source/build.py', rewrite_build)
    episode_path = family / 'source/episode-contract.json'
    episode = json.loads(safe_read(episode_path, selection['episode_binding']['sha256']))
    if episode['purpose'] != 'Distinct independently signed legacy diagnostic family; no old identity, Assignment or grant renewal.':
        raise ValueError('episode purpose differs')
    episode['purpose'] = 'R03 episode 0005 API30 Work inspection and fresh scoped Agent contest candidate; no historical grant renewal or outcome.'
    replace_staged(episode_path, selection['episode_binding']['sha256'], canon(episode))
    selection['episode_binding'] = binding(episode_path)
    capture = {'schema_version': 'lab-T22-agent-contest-input/v1', 'predecessor_author': binding(PREDECESSOR),
               'foundation_contract': {'path': FOUNDATION, 'sha256': INPUTS[FOUNDATION]},
               'contract_schema': {'path': SCHEMA, 'sha256': INPUTS[SCHEMA]},
               'session_evidence': {'path': SESSION, 'sha256': INPUTS[SESSION]},
               'subject': 'work:' + 'completion-' + instance, 'challenger_kind': 'agent-instance',
               'contest_outcome': None, 'owner_decision': None, 'authority_effect': 'none',
               'native_agent_challenge_policy_selected': False, 'challenge_api_operations': 0}
    input_path = family / 'source/t22-agent-contest-input.json'
    fd = os.open(input_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(canon(capture)); stream.flush(); os.fsync(stream.fileno())
    selected = {row['path']: row for row in selection['current_runtime_input_bindings']}
    for name, pin in {**predecessor.INPUTS, **INPUTS, PREDECESSOR.relative_to(ROOT).as_posix(): PREDECESSOR_SHA}.items():
        row = {'path': name, 'sha256': pin}
        if name in selected and selected[name] != row: raise ValueError('conflicting source input')
        selected[name] = row
    for path in (input_path, Path(__file__)):
        row = binding(path); selected[row['path']] = row
    selection['t22_agent_contest_input_binding'] = binding(input_path)
    selection['t22_agent_contest_author_binding'] = binding(Path(__file__))
    selection['current_runtime_input_bindings'] = [selected[key] for key in sorted(selected)]
    replace_staged(selection_path, sha(selection_path.read_bytes()), canon(selection))
    receipt = {'schema_version': 'lab-T22-agent-contest-stage/v1', 'status': 'STAGED',
               'instance': instance, 'family': family.relative_to(ROOT).as_posix(),
               'source_name': base['source_name'], 'not_before': base['not_before'], 'expires_at': base['expires_at'],
               'construction_selection_binding': binding(selection_path), 'records_binding': binding(records),
               'build_binding': binding(build), 'episode_binding': binding(episode_path),
               'contest_input_binding': binding(input_path), 'private_home_locator_sha256': sha(str(private_home).encode()),
               'source_built': False, 'reader_built': False, 'mapper_built': False, 'context_built': False,
               'native_agent_challenge_policy_selected': False, 'challenge_api_operations': 0,
               'contest_outcome': None, 'owner_decision': None, 'authority_effect': 'none'}
    out = TASK / 'STAGE-0001.json'
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(canon(receipt)); stream.flush(); os.fsync(stream.fileno())
    return receipt

def verify():
    receipt = json.loads((TASK / 'STAGE-0001.json').read_bytes())
    family = ROOT / receipt['family']
    for key in ('construction_selection_binding', 'records_binding', 'build_binding', 'episode_binding', 'contest_input_binding'):
        row = receipt[key]; safe_read(ROOT / row['path'], row['sha256'])
    selection = json.loads((family / 'construction-selection.json').read_bytes())
    selected = {row['path']: row['sha256'] for row in selection['current_runtime_input_bindings']}
    for name, pin in {**INPUTS, **selected_predecessor().INPUTS}.items():
        if selected.get(name) != pin: raise ValueError('source input capture differs')
        safe_read(ROOT / name, pin)
    if selection['t22_agent_contest_author_binding'] != binding(Path(__file__)):
        raise ValueError('author binding differs')
    if receipt['native_agent_challenge_policy_selected'] or receipt['challenge_api_operations'] != 0:
        raise ValueError('stage claim ceiling differs')
    text = (family / 'source/records.py').read_text()
    if "'challenge-contract': contract" not in text or "eligible_challenger_kinds=['agent-instance']" not in text:
        raise ValueError('candidate contract source differs')
    return receipt

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--stage', action='store_true'); parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.stage == args.verify: raise ValueError('choose one command')
    value = stage() if args.stage else verify()
    print(json.dumps({'status': value['status'], 'instance': value['instance'], 'family': value['family']}, sort_keys=True))

if __name__ == '__main__': main()
