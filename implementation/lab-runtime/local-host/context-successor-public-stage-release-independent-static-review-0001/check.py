"""Independent inert checks of frozen Context stage release. Never dispatch."""
import hashlib
import json
import os
from pathlib import Path
import sys
import types

LOCAL = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
RELEASE = LOCAL/'context-successor-public-stage-release-0001'
STAGE = LOCAL/'context-successor-public-stage-writer-0002'
RELEASE_SHA = 'f44f312c674dc34cb8b4a430937bfeb0d11e4844dfc3dcb600258aac71d68a34'
STAGE_SHA = '8a49c612931a277485ce3a17fc5c89ac81020c2aa9e556ca46ba65e21c73c742'

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def require(ok, why):
    if not ok: raise RuntimeError(why)

def audit(event, args):
    if event == 'open' and args and str(args[0]).endswith('branch.snapshot'):
        raise RuntimeError('PRIVATE_ARCHIVE_BODY_DISABLED')
    if event.startswith(('subprocess.', 'socket.')) or event in ('os.system', 'os.fork', 'os.exec'):
        raise RuntimeError('REAL_EFFECT_DISABLED')
sys.addaudithook(audit)

release_freeze = json.loads((RELEASE/'freeze.json').read_bytes())
stage_freeze = json.loads((STAGE/'freeze.json').read_bytes())
require(digest(RELEASE/'freeze.json') == RELEASE_SHA and
        digest(STAGE/'freeze.json') == STAGE_SHA, 'FREEZE_DRIFT')
for folder, freeze in ((RELEASE, release_freeze), (STAGE, stage_freeze)):
    for member, expected in freeze['members'].items():
        require(digest(folder/member) == expected, 'MEMBER_DRIFT_'+member)
require(release_freeze['stage_freeze_sha256'] == STAGE_SHA and
        release_freeze['stage_code_sha256'] == stage_freeze['members']['stage_writer.py'] and
        release_freeze['stage_review_sha256'] ==
        digest(LOCAL/'context-successor-stage-writer-independent-review-0002/review.json') and
        release_freeze['stage_review_md_sha256'] ==
        digest(LOCAL/'CONTEXT-SUCCESSOR-STAGE-WRITER-INDEPENDENT-STATIC-REVIEW-0002.md'),
        'PREDECESSOR_DRIFT')

raw = (RELEASE/'release.py').read_bytes()
module = types.ModuleType('checked_independent_context_release')
module.__file__ = str(RELEASE/'release.py')
exec(compile(raw, module.__file__, 'exec'), module.__dict__)
require(module.EFFECT_ENABLED is True and module.ATTEMPT ==
        Path(release_freeze['attempt']) and not os.path.lexists(module.ATTEMPT),
        'RELEASE_OR_ATTEMPT_DRIFT')
stage = module.basis()
require(stage.EFFECT_ENABLED is False and
        stage.sha(stage.pinned(STAGE/'stage_writer.py', release_freeze['stage_code_sha256'])) ==
        release_freeze['stage_code_sha256'], 'CHECKED_STAGE_BUFFER')
preflight = module._strict_preflight(stage)
require(preflight['rows'] == 1570 and preflight['directories'] == 1021 and
        preflight['auth'] == 'UNMINTED_UNSELECTED' and
        preflight['selection_reads']['protected_source_archive_body'] == 'UNOPENED' and
        preflight['source_checks'] == {'public_hashed':1464,'owner_only_metadata_only':94},
        'CURRENT_PREFLIGHT')

try:
    module.pinned(STAGE/'stage_writer.py', '0'*64)
except module.Refused:
    pass
else:
    raise RuntimeError('WRONG_STAGE_PIN_ACCEPTED')

real_basis, real_preflight = module.basis, module._strict_preflight
count = []
fake = types.SimpleNamespace(EFFECT_ENABLED=False)
def fake_run():
    require(fake.EFFECT_ENABLED is True, 'EFFECT_NOT_ENABLED_IN_ROUTE')
    count.append('run')
    return {'status':'PROVISIONAL_STAGE_ONLY_EXTERNAL_OS_REVIEW_REQUIRED',
            'files':1570,'directories':1021,'attempt':str(module.ATTEMPT),
            'retry_allowed':False}
fake.run_effect = fake_run
module.basis = lambda:fake
module._strict_preflight = lambda _: (_ for _ in ()).throw(module.Refused('STALE'))
try:
    module.execute_reviewed_one_shot()
except module.Refused as exc:
    require(str(exc) == 'STALE', 'PREFLIGHT_ERROR_DRIFT')
else:
    raise RuntimeError('STALE_PREFLIGHT_ACCEPTED')
require(count == [] and fake.EFFECT_ENABLED is False, 'PREFLIGHT_EFFECT_LEAK')
module._strict_preflight = lambda _:{'attempt':str(module.ATTEMPT)}
fake.run_effect = lambda: (_ for _ in ()).throw(OSError('late close uncertain'))
try:
    module.execute_reviewed_one_shot()
except OSError as exc:
    require(str(exc) == 'late close uncertain', 'CLOSE_ERROR_MASKED')
else:
    raise RuntimeError('CLOSE_ERROR_ACCEPTED')
require(fake.EFFECT_ENABLED is False, 'CLOSE_EFFECT_LEAK')
fake.run_effect = fake_run
require(module.execute_reviewed_one_shot()['retry_allowed'] is False and
        count == ['run'] and fake.EFFECT_ENABLED is False, 'ONE_SHOT_WRAPPER_RESULT')
module.basis, module._strict_preflight = real_basis, real_preflight
for fn in (module.issue_authority, module.jit_or_docker):
    try: fn()
    except module.Refused: pass
    else: raise RuntimeError('AUTH_OR_DOCKER_ROUTE_OPEN')
require(not os.path.lexists(module.ATTEMPT), 'ATTEMPT_CREATED')
print(json.dumps({'schema':'context-stage-release-independent-static-check/v1',
                  'checks':5,'passed':True,'release_freeze_sha256':RELEASE_SHA,
                  'stage_freeze_sha256':STAGE_SHA,'real_effect':'NOT_RUN',
                  'protected_archive_body':'UNOPENED','attempt':'ABSENT'},
                 sort_keys=True))
