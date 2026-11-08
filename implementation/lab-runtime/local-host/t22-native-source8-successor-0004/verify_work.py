"""Cold-check the exact built T22 Source Work and its selected input lineage."""
import hashlib
import json
import os
from pathlib import Path
import stat


ROOT = Path(__file__).resolve().parents[4]
FAMILY = 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-710362c855a8a11c'
SOURCE = FAMILY + '/source/source-manifest.json'
PACKAGE = FAMILY + '/source/packages/0001/manifest.json'
INDEX = FAMILY + '/source/packages/0001/record-index.json'
WORK = FAMILY + '/source/packages/0001/artifacts/04.json'
SOURCE_SHA = 'a519c711b666f72897fcfffebfe63bc01d0b8994367a182e849b1d747bed7037'
PACKAGE_SHA = '614b14c45370e0d8b500a2dd7c9d57a38394ca404c09414ad3ad80f10db55839'
INDEX_SHA = 'aa996c874242f39ec0371620286e0341f91d2cb5b64018ac8a27d53027154722'
WORK_SHA = '863c92ab8fc926e14dbdced13b9140a8d6b3721afb1b530faa02f3b0892f32ba'
STAGE = 'implementation/lab-runtime/local-host/t22-native-source8-successor-0004/STAGE-0001.json'
STAGE_SHA = '7b7b678083a429ce696aa1d63c9e8a7e4eef422d30572932cac058ae6e021212'
COORDINATION = FAMILY + '/source/packages/0001/artifacts/07.json'
COORDINATION_SHA = 'a226dc36bfbd2f29790fc1799a02211b4a440d8442665b80c6f6c4ecb4462ec9'
CONTEXT = FAMILY + '/source/packages/0001/artifacts/08.json'
CONTEXT_SHA = '4eb3aa8587fed60970847d13f69286005e373e9d03bbb44188c217c6937f8fb2'
POLICY = FAMILY + '/mapped/policy.json'
POLICY_SHA = '1c2ddd360e56666fec0f4ff2095f32369705cff7b96edecbc5ba0720136457ab'
API30 = 'product/lab/release-candidates/v1/interface/api-integration-v30/source-manifest.json'
STATE = 'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances/project-state.json'
INSPECTION = 'implementation/lab-runtime/local-host/t22-api30-episode-inspection-0002/RUN-0003.json'
INPUTS = {
    API30: 'cfd9a932d87c565c22b915234bbf2a18bfed23f163607b95b96f24b2533e3a16',
    STATE: 'cccf18d2966cf0dd494f7d88b054243bb635a91bc84fdcbf5c70709b7b6f8793',
    INSPECTION: '500270b28b5c07ee740a817f4c42afdd3b51226df227c90445fb76e0c04480ae',
}


def digest(raw): return hashlib.sha256(raw).hexdigest()


def read(rel, expected):
    path = Path(rel)
    if path.is_absolute() or '..' in path.parts or path.as_posix() != rel:
        raise ValueError('noncanonical selected path')
    target = ROOT / path
    if any(parent.is_symlink() for parent in target.parents) or target.is_symlink():
        raise ValueError('linked selected path')
    fd = os.open(target, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode): raise ValueError('selected path is not regular')
        with os.fdopen(fd, 'rb', closefd=False) as stream: raw = stream.read()
    finally:
        os.close(fd)
    if digest(raw) != expected: raise ValueError('selected bytes changed: ' + rel)
    return raw


def validate(work, source, package, index, stage):
    if stage['family'] != FAMILY or stage['source_name'] != 'completion-legacy:legacy-local-710362c855a8a11c':
        raise ValueError('wrong staged source identity')
    if stage['authority_effect'] != 'none' or stage['original_t22_complete'] is not False:
        raise ValueError('stage authority claim differs')
    files = {r['path']: r['sha256'] for r in source['files']}
    for path, pin in INPUTS.items():
        if files.get(path) != pin: raise ValueError('selected episode input missing')
    pkg = {r['path']: r['sha256'] for r in package['files']}
    if pkg.get(WORK) != WORK_SHA or pkg.get(INDEX) != INDEX_SHA:
        raise ValueError('built Work or index not package-selected')
    rows = [r for r in index if r.get('kind') == 'work']
    if len(rows) != 1 or rows[0]['original_binding'] != {'path': WORK, 'sha256': WORK_SHA}:
        raise ValueError('built Work index differs')
    if work['name'] != 'Inspect Lab interface API30 current Project State':
        raise ValueError('built Work purpose differs')
    refs = work['payload']['input_refs']
    if refs != ['intent:completion-legacy-local-710362c855a8a11c@1.0.0-candidate.1']:
        raise ValueError('built Work exact input refs differ')
    statement = work['payload']['work_statement']
    if not all('sha256:' + INPUTS[path] + ':' + path in statement for path in (API30, STATE)):
        raise ValueError('built Work selected byte tokens differ')
    if work['evidence_refs'] != [API30, STATE, INSPECTION]:
        raise ValueError('built Work evidence differs')
    if (work['payload']['project_ref'] != 'project:cyberalchemy-v2-to-lab-migration' or
            work['payload']['completion_state'] != 'pending' or work['authority_effect'] != 'none'):
        raise ValueError('built Work project or effect differs')
    return {'status': 'PASS-exact-built-Work', 'source_sha256': SOURCE_SHA,
            'package_sha256': PACKAGE_SHA, 'work_sha256': WORK_SHA,
            'current_input_bindings': [{'path': path, 'sha256': INPUTS[path]} for path in (API30, STATE, INSPECTION)],
            'authority_effect': 'none', 'native_session_consumed': False}


def validate_context_alignment(coordination, context, policy, package):
    selected = {r['path']: r['sha256'] for r in package['files']}
    if selected.get(COORDINATION) != COORDINATION_SHA or selected.get(CONTEXT) != CONTEXT_SHA:
        raise ValueError('signed Coordination/Context not package-selected')
    use = policy['intended_use_binding']['original_Coordination_Context_value']
    if coordination['intended_uses'] != [use] or context['intended_uses'] != [use]:
        raise ValueError('signed Context intended use differs from mapped policy')
    if use != 'Read current scoped Project State' or 'API30 inspection Work' not in context['purpose']:
        raise ValueError('signed Context purpose differs')


def verify_alignment(package):
    coordination = json.loads(read(COORDINATION, COORDINATION_SHA))
    context = json.loads(read(CONTEXT, CONTEXT_SHA))
    policy = json.loads(read(POLICY, POLICY_SHA))
    validate_context_alignment(coordination, context, policy, package)


def verify():
    raw = {path: json.loads(read(path, pin)) for path, pin in
           ((SOURCE, SOURCE_SHA), (PACKAGE, PACKAGE_SHA), (INDEX, INDEX_SHA), (WORK, WORK_SHA), (STAGE, STAGE_SHA))}
    for path, pin in INPUTS.items(): read(path, pin)
    selected = raw[STAGE]['construction_selection_binding']
    selection = json.loads(read(selected['path'], selected['sha256']))
    templates = {item['new']['path']: item['new']['sha256'] for item in selection['template_rows']}
    if templates.get(POLICY) != POLICY_SHA:
        raise ValueError('mapped policy not stage-selected')
    result = validate(raw[WORK], raw[SOURCE], raw[PACKAGE], raw[INDEX], raw[STAGE])
    verify_alignment(raw[PACKAGE])
    result['signed_context_intended_use_aligned'] = True
    return result


if __name__ == '__main__': print(json.dumps(verify(), sort_keys=True))
