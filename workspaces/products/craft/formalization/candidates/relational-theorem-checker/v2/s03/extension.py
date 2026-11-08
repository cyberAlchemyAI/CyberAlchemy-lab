"""Independently computed structural hypotheses for the recursive extension profile."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));from normalizer import normalize,c,s
class Unsupported(ValueError):pass
def require(ok,why):
 if not ok:raise Unsupported(why)
def classify(before,after):
 c.validate_baseline(before);c.validate_baseline(after)
 for key in before:
  if key not in ['inference','producers']:require(before[key]==after[key],'rule-only frame changed '+key)
 a,b=before['inference'],after['inference']
 for key in a:
  if key not in ['predicates','rules']:require(a[key]==b[key],'rule-only inference frame changed '+key)
 require(b['predicates'][:len(a['predicates'])]==a['predicates'],'old predicate mutated/reordered/removed')
 require(b['rules'][:len(a['rules'])]==a['rules'],'old rule mutated/reordered/removed')
 require(after['producers'][:len(before['producers'])]==before['producers'],'old producer policy changed')
 fresh=b['predicates'][len(a['predicates']):];freshids={p['id'] for p in fresh}
 require(all(p['role']=='ordinary' for p in fresh),'fresh protected/root predicate unsupported')
 require(all(p['class']=='derived-information' for p in after['producers'][len(before['producers']):]),'fresh head producer must be derived-information')
 added=b['rules'][len(a['rules']):]
 require(all(r['head']['predicate'] in freshids for r in added),'added rule head is old or undeclared; every-old-model expansion unavailable')
 old,new=normalize(a),normalize(b)
 require(old['rules']==new['rules'][:len(old['rules'])],'component-local old rule identity changed')
 return {'change_class':'rule-only','before_identity':s.identity(before),'after_identity':s.identity(after),'old_normal':old,'new_normal':new,'fresh_predicates':fresh,'added_rules':added,'model_class':'generic-root-constrained-horn','source_faithful_preservation':'requires old sealed-key coverage/source-faithful old model','authority_effect':'none'}

def example(before):
 from copy import deepcopy
 after=deepcopy(before)
 for id in ['FreshReview','FreshReady']:
  after['inference']['predicates'].append({'id':id,'version':'v2','sorts':['reference'],'role':'ordinary'});after['producers'].append({'predicate':id,'class':'derived-information','meaning':'derived-positive-horn'})
 def rule(name,head,body):return {'id':name,'version':'v2','head':{'predicate':head,'terms':[{'variable':'x'}]},'body':[{'predicate':body,'terms':[{'variable':'x'}]}]}
 after['inference']['rules'].extend([rule('fresh-seed','FreshReview','BaselineSignal'),rule('fresh-chain','FreshReady','FreshReview'),rule('fresh-cycle','FreshReview','FreshReady')])
 return after
