"""Strict immutable v2 contract; structural checks do not confer registration."""
from pathlib import Path
import sys,json,importlib.util
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'execution'))
import support as s
import jsonschema
HERE=Path(__file__).resolve().parent
# Legacy modules capture their own support namespace; never alias v2 evidence helpers.
_spec=importlib.util.spec_from_file_location('v1_support',s.V1/'execution/support.py')
_v1s=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_v1s)
_saved_support=sys.modules.get('support');sys.modules['support']=_v1s
try:
 sys.path.insert(0,str(s.V1/'inference/profile'));import frontend as f
 sys.path.insert(0,str(s.V1/'evolution/proposals'));import classifier as legacy
finally:
 sys.modules['support']=_saved_support
SORTS=['reference','effect','scope','epoch','text']
PRODUCERS=['sealed-observation','derived-information','independent-root','root-preserving']
SEALED={'ConformsTo':['reference','reference','scope'],'TargetKind':['reference','text'],'Conforms':['reference']}
MEANINGS={'ConformsTo':'member-conformance','TargetKind':'member-kind','Conforms':'existential-conformance','CheckedRoot':'existing-admission-root','Admitted':'root-preserving-conclusion'}
def decode(raw):
 def pairs(rows):
  result={}
  for k,v in rows:
   s.require(k not in result,'duplicate JSON key '+k);result[k]=v
  return result
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite '+x)))
def schema(name,obj):
 jsonschema.Draft202012Validator(s.read(HERE/(name+'.schema.json'))).validate(obj)
def catalog():return s.read(HERE/'obligation-catalog.json')
def profile():return s.read(HERE/'selected-profile.json')
def validate_profile(p):
 schema('profile',p);s.require(p==profile(),'profile substitution or shrunken producer/catalog contract')
 s.require(p['catalog_identity']==s.identity(catalog()),'stale selected catalog')
 for b in p['trusted_bindings']:s.check(b)
 s.require(p['toolchain']==s.binding(s.V1/'formal/toolchain-lock.json'),'toolchain lock substitution')
 s.lean_path();return p

def obligations(change):
 c=catalog();s.require(change in c['change_classes'],'unsupported/mixed change class '+change)
 ids=c['change_classes'][change]
 return [next(o for o in c['obligations'] if o['id']==id) for id in ids]
def reference_stability(before,after):
 old={(n['ref']['id'],n['ref']['version']):n for n in before['nodes']}
 for n in after['nodes']:
  ref=(n['ref']['id'],n['ref']['version'])
  s.require(ref not in old or (n['kind'],n['content_identity'])==(old[ref]['kind'],old[ref]['content_identity']),'same reference changed kind/content; require new revision')
def validate_baseline(b):
 schema('baseline',b);p=validate_profile(profile())
 s.require(b['profile_identity']==s.identity(p),'baseline profile mismatch')
 s.require(b['catalog_identity']==p['catalog_identity'],'baseline catalog mismatch')
 s.require(b['toolchain']==p['toolchain'],'baseline toolchain mismatch')
 s.require(b['context']['epoch']==b['inference']['snapshot_epoch'],'context/epoch mismatch')
 s.require(b['graph']['admission_roots']==[],'graph-level admission roots need a separate mapping; inference receipts supported separately')
 legacy.structural_registry(b['registry'])
 s.require(set(b['registry'])==legacy.REGISTRY_FIELDS,'unknown registry fields')
 for k in b['registry']['kinds']:s.require(set(k)==legacy.KIND_FIELDS,'unknown registry kind fields')
 for x in b['source_bindings']:s.check(x)
 normal=f.normalize(b['inference']);preds={x['id']:x for x in b['inference']['predicates']}
 producers=b['producers'];s.require(set(preds)=={x['predicate'] for x in producers} and len(producers)==len(preds),'producer coverage missing/duplicate')
 for x in producers:
  id=x['predicate'];sig=preds[id];kind=x['class']
  if id in SEALED:
   s.require(kind=='sealed-observation' and x['meaning']==MEANINGS[id] and sig['sorts']==SEALED[id] and sig['role']=='ordinary','sealed meaning/signature/producer changed')
  elif id=='CheckedRoot':s.require(kind=='independent-root' and x['meaning']==MEANINGS[id],'root producer changed')
  elif sig['role']!='ordinary':s.require(kind=='root-preserving' and x['meaning'] in ['root-preserving-conclusion','root-carrier'],'root role/producer mismatch')
  else:s.require(kind=='derived-information' and x['meaning']=='derived-positive-horn','alias or unsupported observation producer')
 for id in SEALED:s.require(id in preds,'missing sealed predicate '+id)
 sealed={x['predicate'] for x in producers if x['class']=='sealed-observation'}
 for r in b['inference']['rules']:s.require(r['head']['predicate'] not in sealed,'sealed rule head: '+r['head']['predicate'])
 for a in b['inference']['facts']:s.require(a['predicate'] not in sealed,'caller injected sealed seed: '+a['predicate'])
 # Projected source observations are injected later by the checked adapter, not accepted here.
 return {'identity':s.identity(b),'normal':normal,'registration':'unqualified-structural-contract','authority_effect':'none'}

def fixture():
 base=legacy.baseline();graph=base['graph']
 domain=[{'kind':'reference',**n['ref']} for n in graph['nodes']]
 for n in graph['nodes']:
  v={'kind':'text','value':n['kind']}
  if v not in domain:domain.append(v)
 for e in graph['assertions']:
  if e['kind']=='relation.conforms-to':
   v={'kind':'scope','value':e['qualifiers']['conformance_scope']}
   if v not in domain:domain.append(v)
 domain += [{'kind':'effect','value':'admission'},{'kind':'scope','value':'static'},{'kind':'epoch','value':0}]
 # Remove duplicates by exact canonical meaning.
 domain=list({s.identity(v):v for v in domain}.values())
 preds=f.CORE+[{'id':'ConformsTo','version':'v2','sorts':SEALED['ConformsTo'],'role':'ordinary'}, {'id':'TargetKind','version':'v2','sorts':SEALED['TargetKind'],'role':'ordinary'}, {'id':'BaselineSignal','version':'v2','sorts':['reference'],'role':'ordinary'}]
 rule={'id':'existing-conformance-signal','version':'v2','head':{'predicate':'BaselineSignal','terms':[{'variable':'x'}]},'body':[{'predicate':'Conforms','terms':[{'variable':'x'}]}]}
 producers=[]
 for pr in preds:
  id=pr['id'];kind='sealed-observation' if id in SEALED else 'independent-root' if id=='CheckedRoot' else 'root-preserving' if pr['role']!='ordinary' else 'derived-information'
  producers.append({'predicate':id,'class':kind,'meaning':MEANINGS.get(id,'derived-positive-horn')})
 p=profile()
 return {'schema':'relational.baseline/v2','graph':graph,'registry':base['registry'],'inference':{'schema':'relational.inference-input/v1','snapshot_epoch':0,'domain':domain,'predicates':preds,'rules':[rule],'facts':[],'roots':[],'root_assessments':[]},'producers':producers,'interpretations':[],'context':{'id':'candidate-context','version':'v2','epoch':0},'source_bindings':[s.binding(s.V1/'registry/normalized-registry.json'),s.binding(s.V1/'demonstrations/l0/input.json')],'profile_identity':s.identity(p),'catalog_identity':p['catalog_identity'],'toolchain':p['toolchain'],'authority_effect':'none'}
