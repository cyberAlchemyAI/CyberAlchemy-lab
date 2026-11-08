"""Independent inert counterexample checks; no issuer or signed-view effect."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
import types

LOCAL = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
CANDIDATE = LOCAL/'context-successor-local-issuer-adapter-0002'
FREEZE_SHA = '6a2cf9c2fe3c90aacb13b2537668fb37c9dbd94401129b175627ceeea19d7e26'
NOW = dt.datetime(2026,10,20,18,30,tzinfo=dt.timezone.utc)
AUTHORITY = 'fixture-inode:independent-authority'
STAGE = 'fixture-inode:independent-stage'

def need(ok, code):
    if not ok: raise RuntimeError(code)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def audit(event, args):
    if event == 'open' and args and str(args[0]).endswith('branch.snapshot'):
        raise RuntimeError('PRIVATE_ARCHIVE_BODY_DISABLED')
    if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.fork','os.exec'):
        raise RuntimeError('REAL_EFFECT_DISABLED')
sys.addaudithook(audit)

freeze = json.loads((CANDIDATE/'freeze.json').read_bytes())
need(sha(CANDIDATE/'freeze.json') == FREEZE_SHA, 'FREEZE_DRIFT')
for member, expected in freeze['members'].items():
    need(sha(CANDIDATE/member) == expected, 'MEMBER_DRIFT_'+member)
need(sha(LOCAL/'context-successor-local-issuer-independent-review-0001/review.json') ==
     freeze['predecessor_hold_review_sha256'] and
     sha(LOCAL/'context-successor-local-issuer-independent-review-0001/REVIEW.md') ==
     freeze['predecessor_hold_narrative_sha256'], 'HOLD_REVIEW_DRIFT')

code = (CANDIDATE/'adapter.py').read_bytes()
M = types.ModuleType('checked_independent_local_issuer_adapter_0002')
M.__file__ = str(CANDIDATE/'adapter.py')
exec(compile(code,M.__file__,'exec'),M.__dict__)
selected = M.select(NOW)
need(selected['scope_actual'] == 'NOT_OPENED' and
     selected['auth']['issued_sha256'] == 'UNMINTED_UNSELECTED' and
     selected['issuer']['grant'] == 'UNISSUED' and
     selected['reader']['sha256'] == M.READER_CODE_SHA and
     selected['reader']['manifest_sha256'] == M.READER_MANIFEST_SHA,
     'INERT_SELECTED_PINS')

def refusal(fn, code):
    try: fn()
    except M.Refused as exc:
        need(code in str(exc), 'WRONG_REFUSAL_'+str(exc))
    else: raise RuntimeError('MISSED_REFUSAL_'+code)

def facts():
    return {'view_scope':selected['scope_expected'],
            'sources_scope':selected['scope_expected'],
            'selected_basis':{
                'manifest_sha256':selected['reader']['source_package_manifest_sha256'],
                'source_manifest_sha256':selected['reader']['source_manifest_sha256'],
                'adapter_source_sha256':selected['reader']['manifest_sha256']},
            'period_sha256':selected['source_period_sha256'],
            'source_review_sha256':selected['source_effect_review_sha256'],
            'reader_review_sha256':selected['reader_effect_review_sha256'],
            'mapper_review_sha256':selected['mapper_effect_review_sha256'],
            'now_at_close':NOW,'first_guard':True,'final_guard':True,
            'reader_guard':True,'close_ok':True,'current':True}

def after_close():
    m = M.FixtureOneShotModel(selected)
    m.claim(AUTHORITY);m.marker(True);m.begin_signed()
    m.observe_signed_fixture(**facts())
    return m

def after_publication():
    m = after_close()
    raw = m.attestation_candidate()
    digest = m.publish_attestation_fixture(raw,durable=True,
                                           published_identity=AUTHORITY)
    need(digest == hashlib.sha256(raw).hexdigest(), 'PUBLICATION_DIGEST')
    return m,digest

def prewrite(m, digest, **change):
    values = dict(rows=1570,current=True,issuer_local=True,scope_rechecked=True,
                  attestation_sha256=digest,authority_attempt_identity=AUTHORITY,
                  stage_attempt_identity=STAGE)
    values.update(change)
    m.issuer_ready(**values)

# The caller's later edits cannot change the model's selected snapshot.
external = json.loads(json.dumps(selected))
snapshot = M.FixtureOneShotModel(external)
external['scope_expected'] = 'scope:forged-after-selection'
external['reader']['source_manifest_sha256'] = '0'*64
need(snapshot.expected_scope == selected['scope_expected'] and
     snapshot.selection['reader']['source_manifest_sha256'] ==
     selected['reader']['source_manifest_sha256'], 'CALLER_SELECTION_NOT_SNAPSHOTTED')

# First invalid attempt identity and first failed marker are terminal.
m = M.FixtureOneShotModel(selected)
refusal(lambda:m.claim('invalid'),'AUTHORITY_ATTEMPT_IDENTITY_REQUIRED')
need(m.state == 'UNKNOWN_CONSUMED','CLAIM_NOT_POISONED')
refusal(lambda:m.claim(AUTHORITY),'ATTEMPT_ALREADY_CONSUMED')
m = M.FixtureOneShotModel(selected);m.claim(AUTHORITY)
refusal(lambda:m.marker(False),'MARKER_UNKNOWN_NO_RETRY')
refusal(lambda:m.marker(True),'ATTEMPT_NOT_FRESHLY_CLAIMED')
refusal(m.begin_signed,'MARKER_REQUIRED_BEFORE_SIGNED_OPEN')

# Wrong signed scope/close cannot advance to attestation or stage.
for changed in ({'view_scope':'scope:forged'}, {'close_ok':False},
                {'mapper_review_sha256':'0'*64}):
    m = M.FixtureOneShotModel(selected)
    m.claim(AUTHORITY);m.marker(True);m.begin_signed()
    supplied = facts();supplied.update(changed)
    refusal(lambda:m.observe_signed_fixture(**supplied),
            'SIGNED_SCOPE_OR_CLOSE_UNKNOWN_NO_RETRY')
    refusal(m.attestation_candidate,'CLOSED_SIGNED_OBSERVATION_REQUIRED')
    refusal(lambda:m.stage_claim(STAGE),'PUBLISHED_ATTESTATION_REQUIRED')

# A first failed publication, including an identity mismatch, consumes it.
m=after_close()
refusal(lambda:m.stage_claim(STAGE),'PUBLISHED_ATTESTATION_REQUIRED')
refusal(lambda:prewrite(m,'0'*64),'STAGE_MARKER_REQUIRED')
for raw_change, durable, identity in ((True,True,AUTHORITY),
                                      (False,False,AUTHORITY),
                                      (False,True,STAGE)):
    m=after_close();raw=m.attestation_candidate()
    if raw_change:raw+=b'\x00'
    refusal(lambda:m.publish_attestation_fixture(raw,durable=durable,
                                                  published_identity=identity),
            'ATTESTATION_PUBLICATION_UNKNOWN_NO_RETRY')
    need(m.state == 'UNKNOWN_CONSUMED','PUBLICATION_NOT_POISONED')
    refusal(lambda:m.publish_attestation_fixture(m._attestation_raw,durable=True,
                                                  published_identity=AUTHORITY),
            'ATTESTATION_PUBLICATION_NOT_PENDING')
    refusal(lambda:m.stage_claim(STAGE),'PUBLISHED_ATTESTATION_REQUIRED')

# Stage claim and first marker failures cannot be repaired in the same attempt.
m,_ = after_publication()
refusal(lambda:m.stage_claim(AUTHORITY),'STAGE_ATTEMPT_IDENTITY_REQUIRED')
refusal(lambda:m.stage_claim(STAGE),'PUBLISHED_ATTESTATION_REQUIRED')
m,_ = after_publication();m.stage_claim(STAGE)
refusal(lambda:m.stage_marker(False),'STAGE_MARKER_UNKNOWN_NO_RETRY')
refusal(lambda:m.stage_marker(True),'STAGE_NOT_FRESHLY_CLAIMED')
refusal(lambda:prewrite(m,'0'*64),'STAGE_MARKER_REQUIRED')

# At prewrite the recorded publication digest and both claim identities bind.
for change in ({'attestation_sha256':'0'*64},
               {'authority_attempt_identity':STAGE},
               {'stage_attempt_identity':AUTHORITY}):
    m,digest = after_publication();m.stage_claim(STAGE);m.stage_marker(True)
    refusal(lambda:prewrite(m,digest,**change),'AUTH_PREWRITE_UNKNOWN_NO_RETRY')
    need(m.state == 'UNKNOWN_CONSUMED','PREWRITE_NOT_POISONED')
    refusal(lambda:prewrite(m,digest),'STAGE_MARKER_REQUIRED')

m,digest = after_publication();m.stage_claim(STAGE);m.stage_marker(True)
prewrite(m,digest)
need(m.state == 'AUTH_WRITE_ELIGIBLE_MODEL_ONLY','FIXTURE_PREWRITE_STATE')
refusal(m.issue,'EFFECT_DISABLED')
for fn in (M.open_actual_signed_scope,M.issue_actual_auth_or_grant,
           M.create_stage_or_private_policy,M.launch_context):
    refusal(fn,'EFFECT_DISABLED')

print(json.dumps({'schema':'context-local-issuer-independent-static-check/v1',
                  'counterexample_groups':6,'passed':True,
                  'candidate_freeze_sha256':FREEZE_SHA,
                  'effect':'NOT_RUN','signed_scope':'NOT_OPENED',
                  'grant':'UNISSUED','auth':'UNMINTED_UNSELECTED',
                  'private_archive_body':'UNOPENED'},sort_keys=True))
