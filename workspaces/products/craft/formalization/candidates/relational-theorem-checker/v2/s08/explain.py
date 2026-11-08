"""Explain scoped source, supplied truth and derivation evidence without upgrading readiness."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'s06'));import runtime as r
s=r.s

def value(v):return v['id']+'@'+v['version'] if v['kind']=='reference' else str(v['value'])
def atom(a):return a['predicate']['id']+'('+', '.join(value(v) for v in a['values'])+')'
def describe(result,proposal=None,query=None):
 status=result.get('status','invalid');lines=[]
 if status in ['unknown','unknown-resource','unsupported','invalid']:
  return {'text':status+': '+str(result.get('reason','required evidence unavailable'))+'. No complete closure, absence or readiness claim is available.','scope':'incomplete-or-unsupported','authority_effect':'none'}
 if result.get('schema')=='relational.mapped-stress-result/v2':
  for m in result['kernel_evidence']:s.check(m['source']);s.check(m['olean'])
  lines.append('Source assertion '+result['source_assertion']+' has a kernel-checked mapping in one exact source/context snapshot. Typed verdict: '+status+'.')
  if result['operation']=='inheritance':
   lines.append(str(len(result['potential_norms']))+' potential norm(s), '+str(len(result['active_norms']))+' active norm(s), '+str(len(result['active_conflicts']))+' active conflict(s). Selected condition status: '+result['condition_status']+'.')
   lines.append('Inheritance carries a norm from the binding and contract. An active norm also needs a matching condition evaluation. Fulfillment has not been established; admission has not been derived.')
   lines.append('Scope: '+result['potential_scope']+'. Certificate scope: '+result['certificate_scope']+'.')
  else:lines.append('Effectiveness is evaluated for the exact agent, principal, delegation revision, action, scope and epoch. Declaration/policy/gate truth is supplied; chains remain unsupported.')
  lines.append('This recorded machine result is separate from human review and fresh application replay. Authority effect: none.')
  return {'text':'\n\n'.join(lines),'scope':result['scope'],'truth_assumptions':result['truth_boundary'],'authority_effect':'none'}
 s.require(proposal is not None,'recursive explanation requires the exact proposal');r.validate_receipt(proposal,result)
 # Ensure the displayed closure/certificate/theory is the exact checked source, not
 # a caller-modified result wrapped around a genuine unrelated proof file.
 ev={'closure':result['closure'],'steps':result['certificates']}
 source=s.check(result['evidence']['actual'][0]['source'])
 expected=r.witness_source(result['before_normal_form'],result['normal_form'],ev,r.projection.predict(proposal['before'])['graph'])
 s.require(source.read_text()==expected,'displayed theory/closure/certificate does not match checked source')
 p=r.projection.predict(proposal['before']);s.require(result['observations']==p['facts'] and result['supports']==p['supports'],'displayed source support does not match source snapshot')
 lines.append('Recorded result: '+status+'. Current file bindings match. Model class: '+result['model_class']+'. Closure scope: '+result['closure_scope']+'.')
 lines.append('The general theorem says every old model has an expansion with the same old interpretation. The actual witness checks this proposal’s fresh ordinary heads, fixed domain, roots, old rules and initial facts. The complete-closure witness is a separate finite computation.')
 steps=result['certificates'];by_atom={s.identity(x['conclusion']):i for i,x in enumerate(steps)}
 def trace(a):
  index=by_atom.get(s.identity(a));s.require(index is not None,'missing certificate trace');step=steps[index]
  if step['kind']=='base':
   supports=[x for x in result['supports'] if x['atom']==a]
   if supports:
    return {'atom':atom(a),'leaf':'source observation','supports':[x['witness'] for x in supports],'truth':'accepted assessment truth is supplied; exact source membership/endpoints/scope/version are checked'}
   return {'atom':atom(a),'leaf':'independently supplied root receipt' if a['predicate']['id']=='CheckedRoot' else 'supplied ordinary truth','truth':'external truth assumed; provenance binding checked'}
  s.require(all(i<index for i in step['indices']),'forward/cyclic explanation certificate')
  return {'atom':atom(a),'rule':step['instance']['rule'],'substitution':[value(v) for v in step['instance']['substitution']],'premises':[trace(steps[i]['conclusion']) for i in step['indices']]}
 details=None
 if query:
  if query in result['closure']:
   details=trace(query);lines.append('Requested atom is present: '+atom(query)+'. Its rule and source/supplied leaves are shown in the trace.')
  else:
   outside=any(v not in result['normal_form']['domain'] for v in query['values'])
   lines.append(('Requested atom is outside the declared finite domain: ' if outside else 'Requested atom is absent from the recorded complete selected closure: ')+atom(query)+'. Check the exact contract, scope, revision and target kind; a unary Conforms fact keeps only the subject and loses those distinctions.')
 lines.append('ConformsTo(subject,target,scope) describes a checked source observation. TargetKind(target,kind) retains the target’s type. Conforms(subject) is an existential summary and cannot select a particular contract or scope.')
 lines.append('Human review: '+result['human_review']+'. Saved evidence does not authorize application; fresh replay is required. Authority effect: none.')
 return {'text':'\n\n'.join(lines),'trace':details,'source_support_count':len(result['supports']),'model_class':result['model_class'],'scope':result['closure_scope'],'human_review':result['human_review'],'readiness':'unchanged; fresh application replay required','authority_effect':'none'}

def main():
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('result',type=Path);p.add_argument('--proposal',type=Path);args=p.parse_args()
 try:out=describe(s.read(args.result),s.read(args.proposal) if args.proposal else None);print(out['text']);return 0
 except Exception as e:print('Stale or mismatched explanation evidence: '+str(e).splitlines()[0]);return 5
if __name__=='__main__':sys.exit(main())
