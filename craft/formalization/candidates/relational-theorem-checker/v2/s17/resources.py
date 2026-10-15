"""Conservative work bounds; no Cartesian product construction before preflight."""
from pathlib import Path
import sys,time
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'execution'))
import support as s
HERE=Path(__file__).resolve().parent
class Exhausted(ValueError):pass
def capped_pow(base,exponent,cap):
 # Multiplication is capped; adversarial exponents do not construct huge integers.
 answer=1
 while exponent:
  if exponent&1:
   answer*=base
   if answer>cap:return cap+1
  exponent//=2
  if exponent:base=min(cap+1,base*base)
 return answer

def preflight(b,stress=None):
 lim=s.read(HERE/'preflight-bounds.json')['limits'];i=b['inference'];d=len(i['domain']);counters={'products_allocated':0,'ground_candidates_allocated':0,'atom_candidates_allocated':0,'stress_pairs_allocated':0}
 sizes={'nodes':len(b['graph']['nodes']),'assertions':len(b['graph']['assertions']),'assessments':len(b['graph']['assessments']),'domain':d,'rules':len(i['rules']),'predicates':len(i['predicates'])}
 def stop(stage,bound,cap):
  if bound>cap:raise Exhausted('unknown-resource: '+stage+' upper bound '+str(bound)+' exceeds '+str(cap)+'; products_allocated=0')
 for k,v in sizes.items():stop(k,v,lim[k])
 ground=0;variables=[]
 for r in i['rules']:
  names={t['variable'] for p in r['body']+[r['head']] for t in p['terms'] if 'variable' in t}
  n=len(names);variables.append(n);stop('variables',n,lim['variables']);ground+=capped_pow(d,n,lim['ground_candidates']);stop('ground_candidates',ground,lim['ground_candidates'])
 atoms=0
 for p in i['predicates']:
  stop('arity',len(p['sorts']),lim['arity']);atoms+=capped_pow(d,len(p['sorts']),lim['atom_candidates']);stop('atom_candidates',atoms,lim['atom_candidates'])
 stress=stress or {};potential=len(stress.get('inheritances',[]))*len(stress.get('norms',[]));pairs=potential*potential
 stop('stress_candidates',potential,lim['stress_candidates']);stop('conflict_pairs',pairs,lim['conflict_pairs'])
 return {'outcome':'within-envelope','upper_bounds':{'ground_candidates':ground,'atom_candidates':atoms,'stress_candidates':potential,'conflict_pairs':pairs},'sizes':sizes,'variables_per_rule':variables,'counters':counters,'budget_identity':s.identity(s.read(HERE/'preflight-bounds.json')),'claim_ceiling':'Conservative work estimates, not observed allocation or a completion-time guarantee'}

def timed(stage,fn,counters,seconds=None):
 start=time.monotonic();result=fn();elapsed=time.monotonic()-start;counters[stage+'_seconds']=elapsed
 if seconds is not None and elapsed>seconds:raise Exhausted('unknown-resource: '+stage+' elapsed ceiling; no complete verdict')
 return result
