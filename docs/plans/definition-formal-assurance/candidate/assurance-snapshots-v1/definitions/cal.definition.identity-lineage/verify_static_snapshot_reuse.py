"""Independent differential and adversarial checks of the local static-proof reuse boundary."""
import copy,json
import build_candidate as b
from static_snapshot_reuse import StaticSnapshotReuse
def main():
 snapshot=b.snapshot();original=b.r.verify;bindings=[b.ref(p) for p in [b.UNIT/'static_snapshot_reuse.py',b.UNIT/'verify_static_snapshot_reuse.py',b.IMPL/'resolver.py',b.IMPL/'contracts.py',b.BASE/'current-snapshot.json']];context=json.loads((b.UNIT/'context.json').read_bytes());b.unchanged(context['sources']);b.external_current(context);checks=[]
 def check(id,ok):
  if not ok:raise ValueError(id)
  checks.append({'check_id':id,'result':True})
 baseline=original(snapshot);live=original(snapshot,b.ROOT);check('original-static-and-live-both-pass',baseline['result']==live['result']=='PASS' and baseline['files']==live['files']==201)
 cases=[]
 for name,mutate in [('corrupt-row-sha',lambda x:x['captured_files'][0].update(sha256='0'*64)),('invalid-base64',lambda x:x['captured_files'][0].update(content_base64='!')),('changed-current-term',lambda x:x['current_entries'][0].update(term='hyp:changed')),('duplicate-captured-row',lambda x:x['captured_files'].append(copy.deepcopy(x['captured_files'][0]))),('malformed-shape',lambda x:x.clear())]:
  candidate=copy.deepcopy(snapshot);mutate(candidate)
  try:original(candidate);raise ValueError('Expected original rejection '+name)
  except b.r.CaptureFault as error:cases.append((name,candidate,error.code))
 with StaticSnapshotReuse(b.r,snapshot) as reuse:
  check('same-object-result-equals-original',b.r.verify(snapshot)==baseline)
  check('equal-deep-copy-result-equals-original',b.r.verify(copy.deepcopy(snapshot))==baseline)
  leaked=b.r.verify(snapshot);leaked['files']=-1;check('returned-result-mutation-does-not-taint-cache',b.r.verify(snapshot)==baseline)
  check('live-currentness-delegates-original',b.r.verify(snapshot,b.ROOT)==live)
  for name,candidate,expected in cases:
   try:b.r.verify(candidate);raise ValueError('Expected local rejection '+name)
   except b.r.CaptureFault as error:check('same-original-fault-'+name,error.code==expected)
  own=json.loads((b.UNIT/'t.json').read_bytes())['payload'];plain=b.ir.compile_interpretation(own,snapshot);check('compiled-IR-equals-original-native-stage',b.r.same_json(plain,json.loads((b.UNIT/'static-ir.json').read_bytes())))
  reuse.finish();stats=reuse.report()
 check('original-verifier-restored',b.r.verify==original and stats['original_static_verifications']==2 and stats['live_repository_verifications_reused']==0 and stats['live_repository_verifications_delegated']==1 and stats['different_or_unserializable_inputs_delegated']==5)
 mutable=copy.deepcopy(snapshot)
 try:
  with StaticSnapshotReuse(b.r,mutable):mutable['current_entries'][0]['term']='hyp:changed'
  raise ValueError('Expected finish mutation rejection')
 except ValueError as error:check('in-place-bound-snapshot-mutation-rejected-at-finish',str(error)=='Selected in-memory snapshot changed during static-proof reuse')
 check('original-restored-after-mutation-exception',b.r.verify==original)
 try:
  with StaticSnapshotReuse(b.r,snapshot):raise RuntimeError('hyp:body-exception')
 except RuntimeError:check('original-restored-after-body-exception',b.r.verify==original)
 original(snapshot,b.ROOT);b.unchanged(bindings+context['sources']);b.external_current(context)
 report={'kind':'local-static-snapshot-reuse-differential-adversarial-checks','authority_effect':'none','checks':checks,'selected_inputs':bindings,'reuse_observation':stats,'shared_sealed_validator_files_modified':False,'live_currentness_reused':False,'model_evaluation_or_correspondence_checks_skipped':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False}
 with (b.UNIT/'static-snapshot-reuse-checks.json').open('x') as out:json.dump(report,out,indent=2,sort_keys=True);out.write('\n')
 print(json.dumps({'result':'PASS-for-exact-static-only-reuse-boundary','checks':len(checks),'reused_static_calls':stats['reused_static_verifications'],'live_currentness_reused':False,'shared_validators_modified':False},indent=2))
if __name__=='__main__':main()
