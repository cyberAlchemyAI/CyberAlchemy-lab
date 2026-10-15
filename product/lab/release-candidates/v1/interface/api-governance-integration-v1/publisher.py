"""Native original-byte publication with actual scoped clock/source callbacks.

This explicit adapter retains the frozen signed prepare/consequence/transaction
protocol and original recovery mechanism. Deadline checks occur before PENDING
and HEAD; interruption after staging reports uncertainty and preserves residue.
"""
from .host import now,need
from .dependencies import S,C,O,U
class OwnedPublisher(S.Store):
 def __init__(self,path,repo,host):super().__init__(path,repo);self.host=host
 def apply(self,proposal,approval):
  with self.lock():
   data=self.replay(require_current=True)
   for tx in data['transactions'][1:]:
    if tx['proposal']['proposal_id']==proposal['proposal_id']:
     C.require(tx['proposal']==proposal and tx['approval']==approval,'proposal ID reused with different bytes')
     return {'idempotent':True,'transaction_digest':tx['digest'],'receipt':tx['consequences']['receipt']}
   C.require(not self.leftovers(data['head']),'uncommitted work exists; recover before writing')
   projection,cores=O.prepare(data['projection'],proposal,data['head']['transaction_digest'],data['config'])
   S.verify_approval(approval,proposal,cores,data['config'])
   sequence=data['head']['sequence']+1;output=O.consequences(projection,proposal,cores,approval,sequence,data['config']['store_id'])
   tx=C.sealed({'schema_version':'lab-runtime-original-json-transaction/v1-candidate','kind':'admission','sequence':sequence,'previous_digest':data['head']['transaction_digest'],'config_digest':C.digest(data['config']),'baseline_digest':data['baseline']['snapshot_digest'],'proposal':proposal,'decision_cores':cores,'approval':approval,'consequences':output,'projection_digest':C.digest(projection)})
   pending={'sequence':sequence,'expected_head':data['head']['transaction_digest'],'transaction_digest':tx['digest']}
   self.host.guard();need(self.host.active_deadline is not None and now()<self.host.active_deadline,'deadline-exceeded','Actual deadline expired before native PENDING effect.')
   C.atomic(self.path/'PENDING.json',C.encoded(C.sealed(pending)))
   target=self.path/'transactions'/f'{sequence:010d}.json';C.require(not target.exists(),'uncommitted transaction occupies next sequence');C.atomic(target,C.encoded(tx))
   head=C.sealed({'sequence':sequence,'transaction_digest':tx['digest'],'config_digest':C.digest(data['config']),'baseline_digest':data['baseline']['snapshot_digest']})
   C.require(S.freshness(self.repo,data['baseline'])['status']=='current','source changed before commit')
   self.host.guard();need(now()<self.host.active_deadline,'deadline-exceeded','Actual deadline expired after native staging; preserve uncertainty without publishing HEAD.')
   C.atomic(self.path/'HEAD.json',C.encoded(head));(self.path/'PENDING.json').unlink();C.fsync_dir(self.path)
   return {'idempotent':False,'transaction_digest':tx['digest'],'receipt':output['receipt']}
