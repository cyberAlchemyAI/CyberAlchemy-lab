#!/usr/bin/env python3
"""Verify transport completeness without claiming semantic readiness."""
from copy import deepcopy
from pathlib import Path
import bundle_contract as b
s=b.s


def main():
 proposal=s.read(s.BASE/'evolution/proposals/rule-change-proposal.json')
 bundle=b.make_bundle(proposal);result=b.validate_transport(proposal,bundle)
 s.require(result['transport_valid'] and result['readiness']=='unresolved' and not result['semantic_verification_complete'],'transport alone became semantic readiness')
 controls=[]
 def reject(name,change):
  bad=deepcopy(bundle);change(bad)
  try:b.validate_transport(proposal,bad,check_dependencies=False)
  except ValueError as error:controls.append({'name':name,'result':'rejected','diagnostic':str(error)})
  else:raise ValueError('bad bundle accepted: '+name)
 reject('omitted mandatory obligation',lambda x:x['obligations'].pop())
 reject('duplicate mandatory obligation',lambda x:x['obligations'].append(x['obligations'][0]))
 reject('client readiness flag',lambda x:x.update(ready=True))
 reject('client satisfied verdict',lambda x:x['obligations'][0].update(verdict='satisfied'))
 reject('weakened hard flag',lambda x:x['obligations'][0].update(hard=False))
 reject('weakened scope',lambda x:x['obligations'][0].update(scope='optional'))
 reject('self-selected policy',lambda x:x.update(policy_identity='0'*64))
 reject('bounded search replaces universal conservativity',lambda x:next(o for o in x['obligations'] if o['name']=='conservative-expansion').update(method='bounded-search'))
 reject('generic theorem replaces actual countermodel',lambda x:next(o for o in x['obligations'] if o['name']=='independence-witnesses').update(method='proof-submission'))
 wrapper=b.HERE/'captured-countermodel-evidence.json'
 s.write(wrapper,{'schema':b.ROLE_SCHEMA['model-witness'],'proposal_identity':b.g.c.identity(proposal),
  'witness':s.binding(s.BASE/'inference/integration/countermodel.json')})
 witness_bundle=deepcopy(bundle)
 row=next(o for o in witness_bundle['obligations'] if o['name']=='independence-witnesses')
 row.update(method='checked-model-witness',artifacts={'model-witness':s.binding(wrapper)})
 witnessed=b.validate_transport(proposal,witness_bundle)
 s.require(witnessed['transport_valid'] and not witnessed['semantic_verification_complete'],'typed artifact transport became proof truth')
 controls.append({'name':'exact captured countermodel transport remains unverified semantic evidence','result':'pass','readiness':'unresolved'})
 # Reuse a real proof request under a model role: its hash cannot change its role.
 reject('proof schema mislabeled as model witness',lambda x:next(o for o in x['obligations'] if o['name']=='independence-witnesses').update(
  method='checked-model-witness',artifacts={'model-witness':s.binding(s.BASE/'workflow/proof-verifier/examples/derivation-submission.json')}))
 s.write(b.HERE/'bundle-policy.json',b.policy())
 s.write(b.HERE/'builtin-rule-bundle.json',bundle)
 s.write(b.HERE/'typed-witness-bundle.json',witness_bundle)
 s.write(b.HERE/'transport-controls.json',{'result':'pass','positive_obligations':len(result['required']['obligations']),'controls':controls,
  'validation_script':s.binding(Path(__file__)),'semantic_verification_complete':False,'readiness':'unresolved','authority_effect':'none',
  'validation_scope':'Complete transport identities, independent obligation set and method/role checks only. R03 semantic replay and aggregation remain incomplete.'})
 print('R03 transport preflight:',len(result['required']['obligations']),'required entries;',len(controls),'controls; readiness unresolved')

if __name__=='__main__':main()
