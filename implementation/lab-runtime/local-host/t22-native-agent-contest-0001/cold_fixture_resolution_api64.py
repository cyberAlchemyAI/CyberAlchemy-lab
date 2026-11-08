"""Fresh-process read of native local fixture resolution and its source originals."""
import base64
import importlib
import json
import os
from pathlib import Path
import stat
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v64-t22-fixture-resolution-0001'
SOURCE='b30d6074af7b45d0090dbb754d64fe576a6efd785e051c7c2c825dfac2838ee9'
PROFILE='0d81c76772c441d44b412c0d26d9f1c1c4531c0008ff74d9002802ff91414db1'
SUBMISSION='2f358e462cace64bf08f0899d0087826087e71f7fbe924f47be0858d3570073b'
def run(policy_file,namespace,expected_proposal_sha):
 if not sys.flags.isolated or not sys.dont_write_bytecode:raise ValueError('isolated no-bytecode child required')
 path=Path(policy_file);info=path.lstat()
 if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode&0o777!=0o600:raise ValueError('private policy required')
 sys.path.insert(0,str(API.parent));pkg=API.name
 G=importlib.import_module(pkg+'.guard');G.verify(SOURCE)
 W=importlib.import_module(pkg+'.workspace');P=importlib.import_module(pkg+'.protocol');R=importlib.import_module(pkg+'.fixture_resolution_source');A=importlib.import_module(pkg+'.auth')
 policy=P.frame_parse(path.read_bytes());vault=W.Vault(SimpleNamespace(policy=policy))
 claim,result=vault.state(namespace)
 if claim['operation']!='challenge.resolve' or result['posture']!='completed':raise ValueError('completed native fixture resolution required')
 original=P.frame_parse(vault.object_read(claim['original_call_material_binding']))
 raw=vault.object_read(result['domain_binding']);proposal=P.frame_parse(raw)
 if R.sha(P.compact(proposal))!=expected_proposal_sha or proposal['base_cut']!=original['expected_source_cut']:raise ValueError('native proposal/cut differs')
 capsule=P.frame_parse(vault.object_read(policy['resolution_control']['routing_binding']))
 R.verify(capsule,selected_public_hex=base64.b64decode(policy['reader_public_key'],validate=True).hex(),
  selected_submission_sha256=SUBMISSION,selected_source_cut=proposal['base_cut'],now=A.now())
 if policy['principal_ref']!=capsule['envelope']['payload']['fixture_principal_ref']:raise ValueError('fixture owner differs')
 target=proposal['targets'][0];body=vault.object_read({'ref':target['content']['content_ref'],'sha256':target['content']['byte_sha256']})
 if P.frame_parse(body).get('payload',{}).get('response_state')!='deferred' or P.frame_parse(body)!=capsule['members']['challenge-event'] or target['predecessor']['byte_sha256']!=R.ORIGINAL_CANDIDATE_SHA:
  raise ValueError('native consequence changed original Agent event')
 for b in result['evidence_bindings']:vault.object_read(b)
 G.verify(SOURCE)
 return {'result':'PASS-fresh-process-native-fixture-resolution','api_source_sha256':SOURCE,
  'namespace':namespace,'proposal_original_sha256':R.sha(raw),'proposal_structural_sha256':R.sha(P.compact(proposal)),'candidate_sha256':R.sha(body),
  'original_native_candidate_sha256':R.ORIGINAL_CANDIDATE_SHA,
  'fixture_source_sha256':R.sha(R.canon(capsule)),'selected_fixture_outcome':'defer',
  'actual_owner_outcome':None,'authority_effect':'none'}
if __name__=='__main__':
 try:result=run(*sys.argv[1:])
 except Exception as error:
  print(json.dumps({'result':'REFUSED-cold-fixture-resolution','exception':type(error).__name__}));raise SystemExit(2)
 print(json.dumps(result,sort_keys=True))
