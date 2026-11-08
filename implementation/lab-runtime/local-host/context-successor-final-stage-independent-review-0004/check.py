"""Independent read-only selection of frozen final-stage 0004."""
import datetime as dt
import hashlib
import json
import pathlib
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent.parent / 'context-successor-final-stage-0004'
FREEZE_SHA = 'b96908371b064fa0fd90e398a8dfbe3023cf83cb99175dacb3393d08f02ed984'
REVIEW_SHA = '5676b6b6ea2d45981ea9db637cde240a86a94983afc3411ee2eb3287e9c6b13f'

def need(value, code):
    if not value:
        raise RuntimeError(code)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

fraw = (HERE/'freeze.json').read_bytes()
need(digest(fraw) == FREEZE_SHA, 'FREEZE_DRIFT')
freeze = json.loads(fraw)
for name, pin in freeze['members'].items():
    need(digest((HERE/name).read_bytes()) == pin, 'MEMBER_DRIFT')
need(freeze['mapper_effect_review_sha256'] == REVIEW_SHA, 'REVIEW_SELECTION')

def audit(event, args):
    if event == 'open' and args and isinstance(args[0], (str, bytes)) and str(args[0]).endswith('branch.snapshot'):
        raise RuntimeError('PRIVATE_ARCHIVE_OPEN')
    if event.startswith(('subprocess.', 'socket.')) or event in ('os.system', 'os.fork', 'os.exec'):
        raise RuntimeError('EFFECT_ATTEMPT')
sys.addaudithook(audit)
sys.path.insert(0, '/usr/lib/python3/dist-packages')
source = (HERE/'final_stage.py').read_bytes()
need(digest(source) == freeze['members']['final_stage.py'], 'SELECTOR_DRIFT')
module = types.ModuleType('independently_frozen_final_stage_0004')
module.__file__ = str(HERE/'final_stage.py')
exec(compile(source, module.__file__, 'exec'), module.__dict__)
now = dt.datetime.now(dt.timezone.utc)
selected = module.select_after_mapper(now)
need(selected['effect_enabled'] is False and selected['bound_file_count'] == 1570 and
     selected['final_count_with_auth'] == 1571 and
     len(selected['bound_rows']) == 1570 and
     len({row['path'] for row in selected['bound_rows']}) == 1570 and
     selected['auth_placeholder']['sha256'] == 'UNMINTED_UNSELECTED' and
     selected['mapper_effect_review_sha256'] == REVIEW_SHA and
     selected['selection_currentness'] == 'CHECKED_NOW_NO_FUTURE_DISPATCH_AUTHORITY' and
     selected['stage_copy'] == selected['docker_effect'] == 'REFUSED',
     'SELECTION_CONTRACT')
for name, pin in freeze['members'].items():
    need(digest((HERE/name).read_bytes()) == pin, 'POST_MEMBER_DRIFT')
print(json.dumps({'status':selected['status'], 'utc':now.isoformat(),
                  'rows':selected['bound_file_count'], 'conditional':selected['final_count_with_auth'],
                  'auth':selected['auth_placeholder']['sha256'],
                  'mapper_review_sha256':selected['mapper_effect_review_sha256'],
                  'effect':'NOT_RUN', 'private_archive_body':'UNOPENED'}, sort_keys=True))
