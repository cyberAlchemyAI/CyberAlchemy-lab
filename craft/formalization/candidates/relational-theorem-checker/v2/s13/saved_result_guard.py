"""Exact split inventory and bound evidence equality for saved explanations/audits."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'s09'));import bounded_qualification as bounded
s=bounded.s

def validate(result,proposal=None):
 if proposal is not None:
  r=bounded.r;r.validate_receipt(proposal,result);r.ext.classify(proposal['before'],proposal['after'])
  observed=r.projection.predict(proposal['before'])
  s.require(result['observations']==observed['facts'] and result['supports']==observed['supports'],'saved observation/support mismatch')
  s.require(result['before_normal_form']==r.normal_with_observations(proposal['before'],observed) and result['normal_form']==r.normal_with_observations(proposal['after'],observed),'saved normal form/proposal mismatch')
  expected=r.projection.witness_source(observed)
  s.require(len(result['evidence']['projection'])==1 and s.check(result['evidence']['projection'][0]['source']).read_text()==expected,'saved projection witness mismatch')
 s.require(result.get('witness_layout')=='split-independent-stages-v2','unexpected witness layout')
 evidence=result['evidence'];layout=evidence['layout']
 s.require(len(layout['parts'])==4 and len(evidence['actual'])==4,'incomplete split proof inventory')
 bounded.check_layout(result)
 paths={b['path'] for o in result['obligations'] for b in o['evidence']}
 s.require(len(paths)==1,'ambiguous concrete proof evidence')
 for o in result['obligations']:
  for b in o['evidence']:
   actual=s.read(s.check(b))
   s.require(all(actual[k]==evidence[k] for k in ['actual','general','projection','dependencies']),'saved result differs from bound proof evidence')
 return True
