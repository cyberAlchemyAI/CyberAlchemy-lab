from pathlib import Path
from ..p03.context import C,require
from ..execution.extension_runtime import lean_ref,lean_string
H=Path(__file__).resolve().parent;SCHEMA=H/'fulfillment.schema.json'
SCOPE='Complete selected named criterion fulfillment under supplied exact source/action/output/evaluation truth; intent linkage alone has no stronger meaning.'
def modules():return [('FulfillmentSemantics',H/'FulfillmentSemantics.lean')]
def key(r):return (r['id'],r['version'])
def normalize(r,ctx):
 s=r['source'];f=s['frame'];require(C.identity(s)==r['source_identity'],'source identity mismatch')
 require(f['profile']==r['profile'] and f['subject']==s['request'] and f['target']==s['requirement'] and type(f['epoch']) is int,'source request/requirement/frame mismatch')
 def index(rows,label):
  out={}
  for x in rows:k=key(x['ref']);require(k not in out,'duplicate '+label);out[k]=x
  return out
 criteria=[key(c) for c in s['criteria']];require(criteria and len(set(criteria))==len(criteria),'empty/duplicate named criteria')
 actions=index(s['actions'],'action');outputs=index(s['outputs'],'output');evaluations=index(s['evaluations'],'evaluation');selected={}
 for a in actions.values():
  require(a['request']==s['request'] and a['requirement']==s['requirement'] and a['frame']==f,'stale action request/requirement/frame')
  require(len(set(map(key,a['outputs'])))==len(a['outputs']),'duplicate action output')
  for o in a['outputs']:require(key(o) in outputs and outputs[key(o)]['action']==a['ref'],'action output ownership mismatch')
 for o in outputs.values():require(key(o['action']) in actions and o['ref'] in actions[key(o['action'])]['outputs'],'output owner missing/mismatch')
 for e in evaluations.values():
  require(key(e['criterion']) in criteria and key(e['criterion']) not in selected,'missing/contradictory criterion identity')
  require(e['request']==s['request'] and e['requirement']==s['requirement'] and e['frame']==f,'stale evaluation request/requirement/frame')
  require(key(e['action']) in actions and key(e['output']) in outputs and outputs[key(e['output'])]['action']==e['action'] and e['output'] in actions[key(e['action'])]['outputs'],'unrelated/missing action output evidence')
  selected[key(e['criterion'])]=e
 rows=[]
 for c in s['criteria']:
  e=selected.get(key(c));eligible=e is not None and actions[key(e['action'])]['accepted'] and outputs[key(e['output'])]['accepted']
  value='yes' if eligible and e['value']=='yes' else 'no' if e is not None and e['value']=='no' else 'unknown'
  rows.append({'criterion':c,'verdict':value,'supports':[e] if value=='yes' else []})
 fulfilled=s['linked'] and all(c['verdict']=='yes' for c in rows)
 verdict='yes' if fulfilled else 'no' if not s['linked'] or any(c['verdict']=='no' for c in rows) else 'unknown'
 return {'request':r,'source':s,'rows':rows,'fulfilled':fulfilled,'verdict':verdict}
def frame(f):return '⟨'+', '.join([lean_ref(f['context']),lean_string(f['scope']),str(f['epoch'])])+'⟩'
def ls(rows,render):return '['+', '.join(map(render,rows))+']'
def action(a):return '⟨'+', '.join([lean_ref(a['ref']),lean_ref(a['request']),lean_ref(a['requirement']),frame(a['frame']),ls(a['outputs'],lean_ref),'true' if a['accepted'] else 'false'])+'⟩'
def output(o):return '⟨'+', '.join([lean_ref(o['ref']),lean_ref(o['action']),'true' if o['accepted'] else 'false'])+'⟩'
def evaluation(e):return '⟨'+', '.join([lean_ref(e[k]) for k in ['ref','criterion','request','requirement','action','output']]+[frame(e['frame']),'.'+e['value']])+'⟩'
def render(p):
 s=p['source'];source='⟨'+', '.join([lean_ref(s['request']),lean_ref(s['requirement']),frame(s['frame']),'true' if s['linked'] else 'false',ls(s['criteria'],lean_ref),ls(s['actions'],action),ls(s['outputs'],output),ls(s['evaluations'],evaluation)])+'⟩'
 lines=['import FulfillmentSemantics','set_option maxRecDepth 2048','open RelationalExtensions.Fulfillment','namespace FulfillmentInstance','def source : Source := '+source,'theorem complete_fulfillment : fulfilled source = '+('true' if p['fulfilled'] else 'false')+' := by decide','theorem complete_verdict : verdict source = .'+p['verdict']+' := by decide','theorem independent_meaning : fulfilled source = true ↔ Meaning source := fulfillment_exact source']
 for i,c in enumerate(p['rows']):lines+=['theorem criterion_'+str(i)+' : criterionTruth source '+lean_ref(c['criterion'])+' = .'+c['verdict']+' := by decide','#print axioms criterion_'+str(i)]
 lines+=['#print axioms complete_fulfillment','#print axioms complete_verdict','#print axioms independent_meaning','end FulfillmentInstance',''];return '\n'.join(lines)
def result(p):return {'schema':'relational.fulfillment-result/v1','profile':p['request']['profile'],'source_identity':p['request']['source_identity'],'request':p['source']['request'],'requirement':p['source']['requirement'],'linked':p['source']['linked'],'fulfilled':p['fulfilled'],'verdict':p['verdict'],'criteria':p['rows'],'truth_boundary':'All named criteria under supplied exact action/output/evaluation truth; no real-world authenticity or execution proof.','authority_effect':'none','application_authorized':False}
