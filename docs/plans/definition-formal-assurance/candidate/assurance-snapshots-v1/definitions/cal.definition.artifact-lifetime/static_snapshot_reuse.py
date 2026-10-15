"""Process-local exact-byte static-snapshot proof reuse; live checks always delegate."""
import copy,hashlib,json
class StaticSnapshotReuse:
 def __init__(self,resolver,snapshot):
  self.resolver=resolver;self.snapshot=snapshot;self.original=resolver.verify;self.before=self.bytes(snapshot);self.proof=None;self.reused=0;self.live_delegated=0;self.other_delegated=0;self.original_static_checks=0;self.finished=False
 @staticmethod
 def bytes(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
 def __enter__(self):
  self.proof=self.original(self.snapshot);self.original_static_checks+=1;self.resolver.verify=self.verify;return self
 def verify(self,snapshot,root=None):
  if root is not None:self.live_delegated+=1;return self.original(snapshot,root)
  try:unchanged=self.bytes(snapshot)==self.before
  except (TypeError,ValueError):unchanged=False
  if unchanged:self.reused+=1;return copy.deepcopy(self.proof)
  self.other_delegated+=1;return self.original(snapshot)
 def finish(self):
  if self.finished:return
  self.resolver.verify=self.original
  if self.bytes(self.snapshot)!=self.before:raise ValueError('Selected in-memory snapshot changed during static-proof reuse')
  after=self.original(self.snapshot);self.original_static_checks+=1
  if after!=self.proof:raise ValueError('Original static verifier result changed')
  self.finished=True
 def report(self):
  if not self.finished:raise ValueError('Static-proof reuse report requested before original final revalidation')
  return {'method':'exact-canonical-serialized-bytes static-only snapshot validation reuse','selected_snapshot_input_sha256':hashlib.sha256(self.before).hexdigest(),'original_static_verifications':self.original_static_checks,'reused_static_verifications':self.reused,'live_repository_verifications_delegated':self.live_delegated,'live_repository_verifications_reused':0,'different_or_unserializable_inputs_delegated':self.other_delegated,'original_verifier_restored':self.resolver.verify==self.original,'initial_and_final_original_static_results_equal':True,'semantic_proof_claimed':False}
 def __exit__(self,exc_type,exc,tb):
  if exc_type is None:self.finish()
  else:self.resolver.verify=self.original
  return False
