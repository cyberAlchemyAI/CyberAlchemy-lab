"""Semantic pilot reads exact target, scope and target kind before recursive derived signals."""
from pathlib import Path
import sys,copy
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'s06'));import runtime as r
sys.path.insert(0,str(BASE/'s09'));import bounded_qualification as bounded
s=r.s
sys.path.insert(0,str(Path(__file__).resolve().parent));import saved_result_guard as saved_guard

def proposal(wrong_scope=False):
 b=r.ext.c.fixture();b['inference']['domain'].append({'kind':'scope','value':'other-scope'});after=copy.deepcopy(b);edge=next(e for e in b['graph']['assertions'] if e['kind']=='relation.conforms-to');target=edge['target'];scope=edge['qualifiers']['conformance_scope']
 for id in ['ContractReview','ContractReady']:
  after['inference']['predicates'].append({'id':id,'version':'v2','sorts':['reference'],'role':'ordinary'});after['producers'].append({'predicate':id,'class':'derived-information','meaning':'derived-positive-horn'})
 first={'id':'review-exact-contract-scope','version':'v2','head':{'predicate':'ContractReview','terms':[{'variable':'x'}]},'body':[{'predicate':'ConformsTo','terms':[{'variable':'x'},{'constant':{'kind':'reference',**target}},{'constant':{'kind':'scope','value':'other-scope' if wrong_scope else scope}}]},{'predicate':'TargetKind','terms':[{'constant':{'kind':'reference',**target}},{'constant':{'kind':'text','value':'contract'}}]}]}
 def unary(name,head,body):return {'id':name,'version':'v2','head':{'predicate':head,'terms':[{'variable':'x'}]},'body':[{'predicate':body,'terms':[{'variable':'x'}]}]}
 after['inference']['rules'] += [first,unary('recursive-contract-ready','ContractReady','ContractReview'),unary('positive-contract-cycle','ContractReview','ContractReady')]
 return r.proposal(b,after,'rich-wrong-scope' if wrong_scope else 'rich-contract-semantic-pilot')

def explain(p,result):
 saved_guard.validate(result,p)
 ready=[a for a in result['closure'] if a['predicate']['id']=='ContractReady'];by_atom={s.identity(step['conclusion']):n for n,step in enumerate(result['certificates'])}
 def trace(a):
  index=by_atom[s.identity(a)];step=result['certificates'][index]
  if step['kind']=='base':
   support=[x['witness'] for x in result['supports'] if x['atom']==a]
   return {'predicate':a['predicate']['id'],'values':a['values'],'leaf':'source-observation' if support else 'supplied-truth','supports':support}
  s.require(all(n<index for n in step['indices']),'cyclic certificate trace');return {'predicate':a['predicate']['id'],'rule':step['instance']['rule']['id'],'substitution':step['instance']['substitution'],'premises':[trace(result['certificates'][n]['conclusion']) for n in step['indices']]}
 return {'query':'ContractReady(subject)','present':bool(ready),'trace':trace(ready[0]) if ready else None,'reason':'Exact source conformance target/scope and target-kind observations seed the positive cycle.' if ready else 'The rule requests declared other-scope; the source conformance assessment supplies static scope. The empty fresh cycle has no seed.','model_class':result['model_class'],'closure_scope':result['closure_scope'],'fulfillment':'not-established','admission':'not-derived','human_review':'pending','authority_effect':'none'}
