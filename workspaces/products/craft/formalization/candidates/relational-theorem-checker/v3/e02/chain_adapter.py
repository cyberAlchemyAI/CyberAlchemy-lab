from pathlib import Path
import itertools
from ..p03.context import C,require
from ..p06.worker_context import ResourceExhausted
from ..execution.extension_runtime import lean_ref,lean_string
H=Path(__file__).resolve().parent
SCHEMA=H/'chain.schema.json'
SCOPE='Complete bounded simple redelegation query under exact supplied source/gate/revocation truth; no admission or unrestricted authority.'
def modules():return [('ChainSemantics',H/'ChainSemantics.lean')]
def key(r):return (r['id'],r['version'])
def normalize(r,ctx):
 s=r['source'];q=r['query'];f=s['frame']
 require(C.identity(s)==r['source_identity'],'source identity mismatch')
 require(f['profile']==r['profile'] and f['subject']==q['principal'] and f['target']==q['agent'] and f['scope']==q['scope'] and f['epoch']==q['epoch'],'query/source frame mismatch')
 require(type(q['epoch']) is int and type(q['max_depth']) is int and type(f['epoch']) is int,'canonical integer query/frame required')
 nodes={}
 for n in s['principals']:
  require(key(n['ref']) not in nodes and n['roles'] and len(set(n['roles']))==len(n['roles']),'duplicate/empty principal roles');nodes[key(n['ref'])]=n
 hops={}
 for h in s['hops']:
  require(key(h['ref']) not in hops,'duplicate hop identity')
  require(key(h['principal']) in nodes and 'principal' in nodes[key(h['principal'])]['roles'] and key(h['agent']) in nodes and 'agent' in nodes[key(h['agent'])]['roles'],'hop endpoint roles missing')
  require(h['scopes'] and h['actions'] and len(set(h['scopes']))==len(h['scopes']) and len(set(h['actions']))==len(h['actions']),'empty/duplicate restrictions')
  require(type(h['start']) is int and type(h['finish']) is int and h['start']<h['finish'],'invalid half-open interval');hops[key(h['ref'])]=h
 require(key(q['principal']) in nodes and key(q['agent']) in nodes,'query endpoints absent')
 assessments={};ids=set()
 for a in s['assessments']:
  k=(key(a['hop']),a['kind']);require(k not in assessments and key(a['ref']) not in ids,'duplicate/conflicting assessment')
  require(key(a['hop']) in hops and a['frame']==f,'assessment hop/frame mismatch');assessments[k]=a;ids.add(key(a['ref']))
 count=sum(len(hops)**d for d in range(1,q['max_depth']+1))
 if count>4096:raise ResourceExhausted('complete path enumeration exceeds 4096 words; no partial verdict')
 edges=[]
 for h in s['hops']:
  e=dict(h)
  for kind in ['gate','revocation']:e[kind]=assessments.get((key(h['ref']),kind),{}).get('value','unknown')
  edges.append(e)
 supported=[];unknown=[]
 for d in range(1,q['max_depth']+1):
  for path in itertools.product(edges,repeat=d):
   if path[0]['principal']!=q['principal'] or path[-1]['agent']!=q['agent']:continue
   principals=[key(e['principal']) for e in path]+[key(path[-1]['agent'])]
   if len(set(principals))!=len(principals):continue
   if any(p['agent']!=c['principal'] or not p['redelegate'] or not set(c['scopes'])<=set(p['scopes']) or not set(c['actions'])<=set(p['actions']) or not p['start']<=c['start'] or not c['finish']<=p['finish'] for p,c in zip(path,path[1:])):continue
   if any(q['scope'] not in e['scopes'] or q['action'] not in e['actions'] or not e['start']<=q['epoch']<e['finish'] or e['gate']=='no' or e['revocation']=='yes' for e in path):continue
   if all(e['gate']=='yes' and e['revocation']=='no' for e in path):supported.append(list(path))
   else:unknown.append(list(path))
 return {'request':r,'edges':edges,'supported':supported,'unknown':unknown,'count':count,'verdict':'yes' if supported else 'unknown' if unknown else 'no'}
def hop(e):return '⟨'+', '.join([lean_ref(e['ref']),lean_ref(e['principal']),lean_ref(e['agent']),'['+', '.join(map(lean_string,e['scopes']))+']','['+', '.join(map(lean_string,e['actions']))+']',str(e['start']),str(e['finish']),'true' if e['redelegate'] else 'false','.'+e['gate'],'.'+e['revocation']])+'⟩'
def paths(ps):return '['+', '.join('['+', '.join(map(hop,p))+']' for p in ps)+']'
def render(p):
 q=p['request']['query'];query='⟨'+', '.join([lean_ref(q['principal']),lean_ref(q['agent']),lean_string(q['scope']),lean_string(q['action']),str(q['epoch'])])+'⟩'
 return '\n'.join(['import ChainSemantics','set_option maxRecDepth 4096','open RelationalExtensions.Chain','namespace ChainInstance','def q : Query := '+query,'def edges : List Hop := ['+', '.join(map(hop,p['edges']))+']','def depth : Nat := '+str(q['max_depth']),
 'theorem full_count : (pathUniverse edges depth).length = '+str(p['count'])+' := by decide',
 'theorem all_positive_paths : supported q edges depth = '+paths(p['supported'])+' := by decide',
 'theorem all_unknown_paths : undecided q edges depth = '+paths(p['unknown'])+' := by decide',
 'theorem complete_verdict : query q edges depth = .'+p['verdict']+' := by decide',
 'theorem each_reported_ancestor : ∀ p ∈ supported q edges depth, ∀ h ∈ p, q.scope ∈ h.scopes ∧ q.action ∈ h.actions ∧ h.start ≤ q.epoch ∧ q.epoch < h.finish := by intro p hp; exact reported_path_non_amplification q edges depth p hp',
 '#print axioms full_count','#print axioms all_positive_paths','#print axioms all_unknown_paths','#print axioms complete_verdict','#print axioms each_reported_ancestor','end ChainInstance',''])
def result(p):return {'schema':'relational.chain-result/v1','profile':p['request']['profile'],'source_identity':p['request']['source_identity'],'frame':p['request']['source']['frame'],'query':p['request']['query'],'verdict':p['verdict'],'enumerated_words':p['count'],'supported_paths':[[h['ref'] for h in path] for path in p['supported']],'unknown_paths':[[h['ref'] for h in path] for path in p['unknown']],'completeness':'All source edge words of length 1..max_depth; joined simple paths only.','admission':'not-derived','authority_effect':'none','application_authorized':False}
