from pathlib import Path
from ..p03.context import C,require
from ..execution.extension_runtime import lean_ref,lean_string
H=Path(__file__).resolve().parent;SCHEMA=H/'lifecycle-transition.schema.json'
SCOPE='Separate candidate lifecycle eligibility and exact head/history transition; qualification alone does not commit or retire anything.'
def modules():return [('LifecycleSemantics',H/'LifecycleSemantics.lean')]
def key(r):return (r['id'],r['version'])
def payload(r):return {k:v for k,v in r.items() if k!='source_identity'}
def normalize(r,ctx):
 s=r['before'];d=r['declaration'];e=r['eligibility'];v=r['review']
 require(C.identity(payload(r))==r['source_identity'],'source identity mismatch')
 require(all(type(x) is int for x in [s['epoch'],s['generation'],e['epoch'],v['epoch'],v['generation']]),'canonical integer state/review required')
 require(s['history'] and s['history'][-1]==s['head'] and len(set(map(key,s['history'])))==len(s['history']) and len(s['history'])==s['generation']+1 and len(s['evidence'])==s['generation'],'malformed state history/generation')
 require(e['declaration']==d['ref'] and e['predecessor']==d['predecessor'] and e['successor']==d['successor'] and e['context']==s['context'] and e['epoch']==s['epoch'],'eligibility key mismatch')
 eligible=(d['predecessor']==s['head'] and d['successor'] not in s['history'] and d['declared'] and e['value']=='yes' and v['accepted'] and v['head']==s['head'] and v['successor']==d['successor'] and v['generation']==s['generation'] and v['context']==s['context'] and v['epoch']==s['epoch'])
 after=None
 if eligible:
  after={**s,'head':d['successor'],'generation':s['generation']+1,'history':s['history']+[d['successor']],'evidence':s['evidence']+[r['source_identity']]}
 return {'request':r,'eligible':eligible,'after':after}
def state(s):return '⟨'+', '.join([lean_string(s['store']),lean_ref(s['context']),str(s['epoch']),lean_ref(s['head']),str(s['generation']),'['+', '.join(map(lean_ref,s['history']))+']','['+', '.join(map(lean_string,s['evidence']))+']'])+'⟩'
def change(r):
 s=r['before'];d=r['declaration'];v=r['review']
 return '⟨'+', '.join([lean_string(s['store']),lean_ref(s['context']),str(s['epoch']),lean_ref(d['predecessor']),lean_ref(d['successor']),str(s['generation']),'true' if d['declared'] else 'false','.'+r['eligibility']['value'],lean_ref(v['head']),lean_ref(v['successor']),str(v['generation']),lean_ref(v['context']),str(v['epoch']),'true' if v['accepted'] else 'false',lean_string(r['source_identity'])])+'⟩'
def render(p):
 expected='some ('+state(p['after'])+')' if p['after'] else 'none'
 return '\n'.join(['import LifecycleSemantics','open RelationalExtensions.Lifecycle','namespace LifecycleInstance','def before : State := '+state(p['request']['before']),'def requested : Change := '+change(p['request']),
 'theorem exact_transition : transition before requested = '+expected+' := by decide',
 'theorem exact_policy : decide (Policy before requested) = '+('true' if p['eligible'] else 'false')+' := by decide',
 '#print axioms exact_transition','#print axioms exact_policy','end LifecycleInstance',''])
def result(p):return {'schema':'relational.lifecycle-result/v1','profile':p['request']['profile'],'source_identity':p['request']['source_identity'],'eligible':p['eligible'],'before':p['request']['before'],'after':p['after'],'declaration':p['request']['declaration'],'commit':'not-performed-by-qualification','authority_effect':'none','application_authorized':False}
