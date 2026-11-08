"""Independent inert checks for the exact frozen one-shot wrapper."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from unittest import mock

ROOT=Path(__file__).resolve().parent.parent
CANDIDATE=ROOT/'context-public-policy-namespace-probe-effect-0003'
sys.path.insert(0,str(CANDIDATE))
import wrapper as W

freeze_raw=(CANDIDATE/'freeze.json').read_bytes()
assert hashlib.sha256(freeze_raw).hexdigest()=='fbcf33ed639157d3f4571471c5b13b70f0a0c0ffe721e707b48bf7bceaceea44'
freeze=json.loads(freeze_raw)
for name,digest in freeze['members'].items():
    assert hashlib.sha256((CANDIDATE/name).read_bytes()).hexdigest()==digest
selection=W.basis()
assert selection[4]==hashlib.sha256(freeze_raw).hexdigest()
assert selection[0].EFFECT_ENABLED is False
assert selection[1].EFFECT_ENABLED is False
assert selection[2].EFFECT_ENABLED is False

def refuses(call):
    try: call()
    except (W.Refused,FileNotFoundError): return
    raise AssertionError('unexpected acceptance')

refuses(lambda:W.own_static_review('0'*64,selection[4]))
with tempfile.TemporaryDirectory(prefix='independent-own-review-',dir=CANDIDATE) as directory:
    path=Path(directory)/'review.json'
    base={'schema':'context-public-policy-probe-effect-one-shot-independent-static-review/v1',
          'verdict':'PASS_BOUNDED_PUBLIC_ONLY_ONE_SHOT_STATIC',
          'candidate_freeze_sha256':selection[4],'findings':[],
          'docker_effect':'UNRUN',
          'same_uid_ceiling':'TRUSTED_SAME_UID_NOT_HOSTILE_SWAP_PROOF'}
    with mock.patch.object(W,'FUTURE_REVIEW',path):
        for change in ({'verdict':'HOLD'}, {'candidate_freeze_sha256':'f'*64},
                       {'findings':[{'id':'R01'}]}, {'docker_effect':'RUN'}):
            path.write_bytes(W.wire(dict(base,**change)))
            refuses(lambda:W.own_static_review(W.sha(path.read_bytes()),selection[4]))

summary={'overall':'PASS_BOUNDED_PUBLIC_NAMESPACE_PROBE_ONLY',
         'container_name_absent':True,'container_cid_absent':True,
         'retry_allowed':False}
stdout=W.wire(summary)
record=W.wire({'schema':'context-public-only-probe-observer-record/v1',
               'status':'PROVISIONAL_MATCH','candidate':summary,'retry_allowed':False})
assert W.outer_join(0,stdout,b'',record)['outer_os_exit']==0
for bad in (False,0.0,1): refuses(lambda:W.outer_join(bad,stdout,b'',record))
refuses(lambda:W.outer_join(0,stdout,b'error',record))
refuses(lambda:W.outer_join(0,stdout,b'',W.wire({'schema':'context-public-only-probe-observer-record/v1',
    'status':'UNKNOWN_PRESERVE_NO_RETRY','candidate':summary,'retry_allowed':False})))
assert not W.OUTER_OBSERVATION.exists()
assert not W.INNER_OBSERVATION.exists()
assert not W.RELEASE_ATTEMPT.exists()
print('independent frozen-member, review-gate, strict outer OS and no-effect checks PASS')
