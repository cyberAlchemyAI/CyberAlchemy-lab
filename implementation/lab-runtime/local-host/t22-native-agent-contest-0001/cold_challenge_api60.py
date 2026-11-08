"""Fresh-process validation of API60's private challenge journal and object closure.

The supplied policy remains in owner-only custody. This is an offline journal
read, not an authenticated API operation or a new grant.
"""
from __future__ import annotations
import hashlib
import importlib
import json
import os
from pathlib import Path
import stat
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v60-t22-pinned-family-source-0001'
SOURCE_SHA = 'a38d44c85102b527ad681600b9b585914ac548659aba833b28915c59435fa47c'
PROFILE_SHA = '7c263b912f56c7e5256ff8426d64f0325564038fad84a54f0f6a714ed568a34b'

def sha(raw): return hashlib.sha256(raw).hexdigest()

def run(policy_file, namespace, expected_candidate_sha):
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise ValueError('isolated bytecode-disabled child required')
    path = Path(policy_file)
    info = path.stat(follow_symlinks=False)
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o777 != 0o600:
        raise ValueError('owner-only regular policy required')
    sys.path.insert(0, str(API.parent))
    name = API.name
    guard = importlib.import_module(name + '.guard')
    manifest = guard.verify(SOURCE_SHA)
    if manifest['profile_binding']['sha256'] != PROFILE_SHA:
        raise ValueError('selected profile changed')
    W = importlib.import_module(name + '.workspace')
    P = importlib.import_module(name + '.protocol')
    policy = P.frame_parse(path.read_bytes())
    # Vault's original constructor validates all private workspace modes,
    # manifest/material hashes, scope and ownership. state() then closes the
    # allocation -> original wire -> claim -> result -> objects chain.
    cold = W.Vault(SimpleNamespace(policy=policy))
    claim, result = cold.state(namespace)
    if claim is None or result is None or claim['operation'] != 'challenge.submit' or result['posture'] != 'completed':
        raise ValueError('completed challenge journal required')
    original = P.frame_parse(cold.object_read(claim['original_call_material_binding']))
    proposal_raw = cold.object_read(result['domain_binding'])
    proposal = P.frame_parse(proposal_raw)
    if original['operation'] != 'challenge.submit' or proposal['schema_version'] != 'lab-change-proposal/v1-candidate':
        raise ValueError('challenge wire/proposal differs')
    if proposal['base_cut'] != original['expected_source_cut']:
        raise ValueError('proposal cut differs from original call')
    target = [t for t in proposal['targets'] if t['artifact']['carrier_ref'] == 'cal.artifact-type.challenge-event/v1']
    if len(target) != 1:
        raise ValueError('one exact challenge candidate required')
    body_raw = cold.object_read({'ref':target[0]['content']['content_ref'], 'sha256':target[0]['content']['byte_sha256']})
    candidate = P.frame_parse(body_raw)
    if sha(body_raw) != expected_candidate_sha or target[0]['content']['byte_sha256'] != expected_candidate_sha:
        raise ValueError('candidate original byte correspondence differs')
    if (candidate['payload']['response_state'] != 'open' or candidate['payload']['resolution_decision_ref'] != 'none'
            or candidate['payload']['challenger_ref'] != original['message']['actor']['agent_instance_ref']):
        raise ValueError('challenge state or Agent differs')
    # Parse and hash every evidence/result body through the original Vault reader.
    for binding in result['evidence_bindings']:
        W.privacy(P.frame_parse(cold.object_read(binding)))
    guard.verify(SOURCE_SHA)
    return {'result':'PASS-cold-native-challenge-journal', 'namespace':namespace,
            'claim_sha256':sha((cold.root/'journal'/(namespace+'.claim.json')).read_bytes()),
            'domain_sha256':sha(proposal_raw), 'candidate_sha256':sha(body_raw),
            'evidence_objects':len(result['evidence_bindings']),
            'original_call_sha256':claim['original_call_binding']['sha256'],
            'api_source_sha256':SOURCE_SHA, 'api_profile_sha256':PROFILE_SHA,
            'challenge_resolved':False, 'owner_decision':None, 'authority_effect':'none'}

if __name__ == '__main__':
    try:
        answer=run(*sys.argv[1:])
    except Exception as error:
        # Values/private paths are intentionally excluded from retained output.
        print(json.dumps({'result':'REFUSED-cold-native-challenge-journal', 'exception':type(error).__name__}))
        raise SystemExit(2)
    print(json.dumps(answer, sort_keys=True))
