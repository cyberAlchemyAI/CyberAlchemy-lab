"""Verify explicit byte-equivalent evidence locators without writing external refs."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'docs/plans/0010-lab-one-shot-execution').is_dir())
REF = '/home/vlad_/projects/cyberAlchemy-v2/.git/refs/heads/main'
REF_SHA = 'dc064a539d5a525fbe777769a3496840c99aaba7271ccc8a3790ac40a99ade04'
COMMIT = 'f74e67fce7b0c704dee6bd859a16eebea0fc40fb'
EXE = '/tmp/cal-O03-native-build-ezn_8vqs/debug/lab-ontology-native'
EXE_SHA = '480d421a438f712db930bb287d2ee1d5e4a0933e1336816defa28d6c284de9c3'
EXPECTED = {REF: REF_SHA, EXE: EXE_SHA}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(p):
    return json.loads(Path(p).read_bytes())


def binding(p):
    p = Path(p)
    return {'path': p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p), 'sha256': sha(p.read_bytes())}


def original(row):
    p = ROOT / row['path']
    require(p.is_file() and not p.is_symlink(), 'absent or unsafe selected file: ' + row['path'])
    raw = p.read_bytes()
    require(sha(raw) == row['sha256'], 'selected bytes changed: ' + row['path'])
    return raw


def equivalent_ref(raw):
    require(raw == (COMMIT + '\n').encode('ascii') and sha(raw) == REF_SHA, 'ref resolved to a different commit or representation')


def observe_ref():
    command = ['git', '-C', '/home/vlad_/projects/cyberAlchemy-v2', 'show-ref', '--verify', '--hash', 'refs/heads/main']
    process = subprocess.run(command, capture_output=True, check=True)
    equivalent_ref(process.stdout)
    return {'command': command, 'terminal_observed': True, 'exit_code': process.returncode,
            'resolved_commit': COMMIT, 'resolved_commit_line_sha256': sha(process.stdout),
            'loose_ref_present': Path(REF).is_file(), 'external_repository_written': False}


def check_partition(parent, successor):
    """All historical bindings remain checked or have an exact declared replacement."""
    before = {r['path']: r['sha256'] for r in parent['files']}
    after = {r['path']: r['sha256'] for r in successor['files']}
    routes = successor['portable_locator_routes']
    declared = {r['historical_binding']['path']: r for r in routes}
    require(len(declared) == len(routes), 'duplicate locator route')
    require(set(before) - set(after) == set(declared), 'historical closure omitted or undeclared locator removed')
    for name, digest in before.items():
        if name in declared:
            route = declared[name]
            require(EXPECTED.get(name) == digest and route['historical_binding'] == {'path': name, 'sha256': digest}, 'unapproved historical locator substitution')
            replacement = route['portable_binding']
            require(replacement['sha256'] == digest and after.get(replacement['path']) == digest, 'portable locator bytes are not equivalent')
        else:
            require(after.get(name) == digest, 'historical file changed or dropped: ' + name)
    require(successor.get('source_bindings', []) == parent.get('source_bindings', []), 'original source obligations changed')
    for key in parent:
        if key not in {'files', 'schema_version'}:
            require(successor.get(key) == parent[key], 'historical acceptance or claim changed: ' + key)


def verify_receipt(path):
    successor = load(path)
    parent = load(ROOT / successor['predecessor_receipt_binding']['path'])
    original(successor['predecessor_receipt_binding'])
    check_partition(parent, successor)
    for row in successor['files'] + successor.get('source_bindings', []):
        original(row)
    return len(successor['files'])


def currentness():
    """Current transport observations are separate from retained historical proof."""
    errors, observations = [], []
    try:
        m = load(HERE / 'source-manifest.json')
        for row in m['files']:
            original(row)
        result = load(HERE / 'proof/0001/result.json')
        require(result['result'] == 'PASS', 'portable producer did not pass')
        observations.append(observe_ref())
        equivalent_ref(original(result['portable_ref_binding']))
        require(sha(original(result['portable_native_binding'])) == EXE_SHA, 'portable native executable differs')
        for row in result['successor_receipt_bindings']:
            original(row)
            observations.append({'receipt': row['path'], 'checked_file_bindings': verify_receipt(ROOT / row['path']), 'result': 'PASS'})
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        errors.append('portable-currentness:' + str(error))
    return errors, observations
