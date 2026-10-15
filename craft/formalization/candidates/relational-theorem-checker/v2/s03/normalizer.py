"""V2 component-local rule identity; unrelated fresh predicates cannot rekey old rules."""
from pathlib import Path
import sys,copy
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'s15'))
import contracts as c
s=c.s

def normalize(raw):
 n=c.f.normalize(raw)
 for rule,source in zip(n['rules'],raw['rules']):
  used={p['predicate']['id'] for p in rule['body']+[rule['head']]}
  resolved={k:copy.deepcopy(v) for k,v in rule.items() if k!='hash'}
  rule['hash']=s.identity({'policy':'component-local-v2','source_rule':source,'resolved_rule':resolved,'predicate_definitions':[p for p in n['predicates'] if p['id'] in used]})
 n['schema']='relational.inference-normal-form/v2';n['identity_policy']='component-local-v2'
 n.pop('normal_form_identity',None);n['normal_form_identity']=s.identity(n)
 return n
