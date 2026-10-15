"""Explicit source-bound stress mapping; potential/active/fulfilled remain distinct."""
from pathlib import Path
import sys,copy,json,os,subprocess,tempfile,importlib.util
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'s05'));import adapter as p
s=p.s;c=p.c;resource=p.resource
_spec=importlib.util.spec_from_file_location('v1_stress_transport',s.V1/'relation-stress/v1/implementation/stress_cli.py');typed=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(typed)

def modules():
 return s.core_modules({'RelationalInput','RelationalSemantics','SemanticLogic','InferenceCore','StressTypes','DelegationSemantics','ObligationSemantics','StressCheckers','StressLaws','StressProofs'})+[('StressRuntime',s.V1/'relation-stress/v1/implementation/StressRuntime.lean')]+[(n,BASE/f's00/{n}.lean') for n in ['RequirementSemantics','RequiredStatements']]+[(n,BASE/f's04/{n}.lean') for n in ['ConditionSemantics','InterpretationSemantics','MappingStatements']]+[('KernelMapping',HERE/'KernelMapping.lean')]

def prepare(build):
 build=Path(build);build.mkdir(parents=True,exist_ok=True);audit=build/'dependencies.json';mods=modules()
 if audit.exists():
  logs=s.read(audit)['modules'];s.require([x['source'] for x in logs]==[s.binding(p) for _,p in mods],'stress mapping import drift')
  for x in logs:s.check(x['source']);s.check(x['olean'])
 else:s.write(audit,{'modules':s.compile_modules(build,mods)})


def source_assertion(request):
 b=request['baseline'];c.validate_baseline(b);resource.preflight(b);g=b['graph'];selected=[e for e in g['assertions'] if e['id']==request['assertion_id']];s.require(len(selected)==1,'source assertion absent/ambiguous');e=selected[0]
 s.require(len({n['ref']['id']+'\0'+n['ref']['version'] for n in g['nodes']})==len(g['nodes']),'duplicate source reference')
 s.require(len({a['id'] for a in g['assertions']})==len(g['assertions']),'duplicate source assertion')
 declaration=next(k for k in b['registry']['kinds'] if k['id']==e['kind']);s.check(declaration['source']);s.require(e['kind_version']==declaration['version'],'source relation version drift')
 s.require(set(e['qualifiers'])==set(declaration['fields']) and all(isinstance(v,str) and v for v in e['qualifiers'].values()),'unmapped/missing source qualifier')
 def node(ref):
  rows=[n for n in g['nodes'] if n['ref']==ref];s.require(len(rows)==1,'exact source endpoint absent');return rows[0]
 a,z=node(e['source']),node(e['target']);s.require({'source_kind':a['kind'],'target_kind':z['kind']} in declaration['pairs'],'undeclared exact source endpoint pair')
 record=request['interpretation'];s.check(record['evidence']);s.require(record['record_identity']==s.identity({k:v for k,v in record.items() if k!='record_identity'}),'stale interpretation record/version identity')
 for key,expected in {'source_identity':s.identity(g),'registry_identity':s.identity(b['registry']),'context_identity':s.identity(b['context']),'assertion_identity':s.identity(e),'typed_identity':s.identity(request['typed'])}.items():s.require(record[key]==expected,'stale interpretation '+key)
 kind='relation.acts-for' if request['operation']=='delegation' else 'relation.inherits-contract';s.require(e['kind']==kind,'wrong source meaning selected')
 return e

def condition_key(request,edge):
 b=request['baseline'];condition=request['interpretation']['fields']['condition_ref']
 return copy.deepcopy({'profile':b['profile_identity'],'condition':condition,'context':{'id':b['context']['id'],'version':b['context']['version']},'subject':edge['subject'],'target':edge['contract'],'scope':edge['scope'],'epoch':b['context']['epoch']})
def condition_status(es,key):
 ids=[]
 for e in es:
  s.require(e['id'] and e['evidence'] and e['key']['profile'] and all(e['key'][k]['id'] and e['key'][k]['version'] for k in ['condition','context','subject','target']) and e['key']['scope'],'invalid condition evaluation')
  ids.append(e['id'])
 if len(set(ids))!=len(ids):return 'invalid'
 statuses={e['status'] for e in es if e['key']==key}
 if len(statuses)>1:return 'invalid'
 if 'holds' in statuses:return 'yes'
 if 'does-not-hold' in statuses:return 'no'
 return 'unknown'

def key_lean(k):
 d=c.f.d
 return '{ profile := '+d.literal(k['profile'])+', condition := '+d.refs(k['condition'])+', context := '+d.refs(k['context'])+', subject := '+d.refs(k['subject'])+', target := '+d.refs(k['target'])+', scope := '+d.literal(k['scope'])+', epoch := '+('none' if k['epoch'] is None else 'some '+str(k['epoch']))+' }'
def evaluations_lean(es):
 d=c.f.d;statuses={'holds':'holds','does-not-hold':'doesNotHold','unknown':'unknown'}
 return d.rows(es,lambda e:'{ id := '+d.literal(e['id'])+', key := '+key_lean(e['key'])+', status := .'+statuses[e['status']]+', evidence := '+d.literal(e['evidence'])+' }')
def store_lean(e,fields,op):
 d=c.f.d
 def row(token,value):return '('+d.literal(token)+', '+value+')'
 if op=='delegation':
  refs='[(('+d.literal('delegation')+', '+d.literal(e['qualifiers']['delegation_ref'])+'), '+typed.encode(fields['delegation_ref'],'ref')+')]'
  scopes='['+row(e['qualifiers']['scope_ref'],d.literal(fields['scope_ref']))+']';periods='['+row(e['qualifiers']['effective_period'],typed.encode(fields['effective_period'],'period'))+']';rev='['+row(e['qualifiers']['revocation_state'],typed.encode(fields['revocation_state'],'option:nat'))+']'
 else:
  refs='['+', '.join('((' + d.literal(role)+', '+d.literal(e['qualifiers'][token])+'), '+typed.encode(fields[token],'ref')+')' for role,token in [('binding','binding_ref'),('contract-version','contract_version_ref')])+']';scopes=periods=rev='[]'
 return '{ references := '+refs+', scopes := '+scopes+', periods := '+periods+', revocations := '+rev+' }'

def map_input(request,e):
 t=copy.deepcopy(request['typed']);f=request['interpretation']['fields']
 if request['operation']=='delegation':
  s.require(t['operation']=='evaluate-acts-for','wrong typed operation');edge=t['edge']
  expected={'id':e['id'],'agent':e['source'],'principal':e['target'],'delegation':f['delegation_ref'],'scope':f['scope_ref'],'period':f['effective_period'],'revokedAt':f['revocation_state']}
  s.require(edge==expected,'typed delegation/source field mapping mismatch')
  s.require(t['snapshot']['ref']=={'id':request['baseline']['context']['id'],'version':request['baseline']['context']['version']} and t['snapshot']['epoch']==request['baseline']['context']['epoch'],'stale delegation snapshot')
  s.require(request['evaluations']==[],'delegation profile does not consume norm condition records')
 else:
  s.require(t['operation']=='close-inherits-contract','wrong typed operation');g=t['graph'];s.require(len(g['inheritances'])==1,'selected single-source inheritance query contains unmapped edges')
  edge=g['inheritances'][0];expected={'id':e['id'],'subject':e['source'],'contract':e['target'],'binding':f['binding_ref'],'scope':f['scope'],'condition':f['condition_ref']['id']}
  s.require(edge==expected and f['contract_version_ref']==e['target'],'typed inheritance/source field mapping mismatch')
  resource.preflight(request['baseline'],{'inheritances':g['inheritances'],'norms':[n for k in g['contracts'] for n in k['norms']]})
 typed.validate_request(t);return t

def witness_source(request,e,t,response):
 d=c.f.d;op=request['operation'];f=request['interpretation']['fields'];store=store_lean(e,f,op)
 out='import KernelMapping\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace Successor.MappingRuntime.Actual\nopen Stress Successor.Interpretation\ndef store : Store := '+store+'\ntheorem functional : StoreFunctional store := by decide\n'
 if op=='delegation':
  raw='{ id := '+d.literal(e['id'])+', agent := '+typed.encode(e['source'],'ref')+', principal := '+typed.encode(e['target'],'ref')+', delegationToken := '+d.literal(e['qualifiers']['delegation_ref'])+', scopeToken := '+d.literal(e['qualifiers']['scope_ref'])+', periodToken := '+d.literal(e['qualifiers']['effective_period'])+', revocationToken := '+d.literal(e['qualifiers']['revocation_state'])+' }'
  out+='def raw : LegacyActs := '+raw+'\ndef edge : ActsEdge := '+typed.encode(t['edge'],'actsEdge')+'\ntheorem mapping : MapsActs store raw edge := by decide\n'
  verdict={'yes':'yes','no':'no','unknown':'unknown','invalid':'invalid'}[response['status']]
  out+='theorem actual_verdict : checkActs '+typed.encode(t['delegations'],'list:delegation')+' '+typed.encode(t['snapshot'],'snapshot')+' edge '+typed.encode(t['action'],'string')+' '+typed.encode(t['redelegated'],'bool')+' = .'+verdict+' := by decide\n#print axioms actual_verdict\n'
 else:
  edge=t['graph']['inheritances'][0];raw='{ id := '+d.literal(e['id'])+', subject := '+typed.encode(e['source'],'ref')+', contract := '+typed.encode(e['target'],'ref')+', bindingToken := '+d.literal(e['qualifiers']['binding_ref'])+', contractVersionToken := '+d.literal(e['qualifiers']['contract_version_ref'])+' }'
  out+='def raw : LegacyInheritance := '+raw+'\ndef graph : Stress.Graph := '+typed.encode(t['graph'],'graph')+'\ndef edge : Inheritance := '+typed.encode(edge,'inheritance')+'\ntheorem mapping : MapsInheritance store raw edge := by decide\n'
  verdict=response['status'];out+='theorem actual_verdict : checkInheritance graph '+str(t['budget'])+' = .'+verdict+' := by decide\n'
  out+='def potential : List Fact := '+typed.encode(response.get('facts',[]),'list:fact')+'\ntheorem potential_origins : ∀ f ∈ potential, Successor.PotentialNorm graph f := by decide\n'
  key=condition_key(request,edge);status=condition_status(request['evaluations'],key)
  active=response.get('facts',[]) if verdict=='yes' and status=='yes' else []
  out+='def key : Successor.EvaluationKey := '+key_lean(key)+'\ndef evaluations : List Successor.Evaluation := '+evaluations_lean(request['evaluations'])+'\ndef active : List Fact := '+typed.encode(active,'list:fact')+'\ntheorem condition_verdict : Successor.Conditions.checkCondition evaluations key = .'+status+' := by decide\ntheorem activation_exact : ∀ f ∈ potential, (Successor.ActiveNorm graph f evaluations key ↔ f ∈ active) := by decide\n'
  pairs=[(a,b) for a in active for b in active if a['norm']['mode']=='require' and b['norm']['mode']=='forbid' and a['norm']['action']==b['norm']['action']]
  out+='def activePairs : List (Fact × Fact) := '+d.rows(pairs,lambda pair:'('+typed.encode(pair[0],'fact')+', '+typed.encode(pair[1],'fact')+')')+'\n'
  out+='theorem conflict_sound : ∀ pair ∈ activePairs, Successor.ActiveConflict graph pair.1 pair.2 evaluations key key := by decide\n'
  out+='theorem conflict_complete : ∀ f ∈ active, ∀ h ∈ active, Successor.ActiveConflict graph f h evaluations key key → (f,h) ∈ activePairs := by decide\n'
  if verdict=='yes':out+='theorem complete_potential_query : potential = closure graph := by decide\n#print axioms complete_potential_query\n'
  out+='#print axioms potential_origins\n#print axioms condition_verdict\n#print axioms activation_exact\n#print axioms conflict_sound\n#print axioms conflict_complete\n'
 out+='#print axioms functional\n#print axioms mapping\nend Successor.MappingRuntime.Actual\n';return out

def evaluate(request,build=None):
 import jsonschema
 jsonschema.Draft202012Validator(s.read(HERE/'interpretation.schema.json')).validate(request);e=source_assertion(request);t=map_input(request,e)
 if build is None:build=Path(tempfile.mkdtemp(prefix='v2-mapping-',dir=HERE/'runs'))
 build=Path(build);prepare(build)
 # Trusted typed runtime evaluation is checked again by reduction in the kernel.
 query=build/('TypedQuery_'+s.identity(request)[:20]+'.lean');query.write_text(typed.query_source(t));lean=s.lean_path();r=subprocess.run([str(lean),'--run',str(query)],cwd=build,env={**os.environ,'LEAN_PATH':str(build)},capture_output=True,text=True,timeout=60)
 s.require(r.returncode==0,'typed stress evaluation failed: '+r.stdout+r.stderr);response=json.loads(r.stdout)
 path=build/('MappingWitness_'+s.identity(request)[:20]+'.lean');path.write_text(witness_source(request,e,t,response));logs=s.compile_modules(build,[(path.stem,path)])
 out={'schema':'relational.mapped-stress-result/v2','operation':request['operation'],'status':response['status'],'source_assertion':e['id'],'request_identity':s.identity(request),'source_identity':s.identity(request['baseline']['graph']),'context_identity':s.identity(request['baseline']['context']),'typed_result':response,'kernel_evidence':logs,'dependencies':s.binding(build/'dependencies.json'),'truth_boundary':['supplied direct delegation/policy/gate truth','source endpoint kinds/registry selection tested boundary','source-bound typed interpretation truth','external condition evaluations are supplied, not arbitrary executable strings'],'scope':'one exact mapped source assertion, selected direct typed profile; no whole legacy graph qualification','human_review':'pending','authority_effect':'none'}
 if request['operation']=='inheritance':
  edge=t['graph']['inheritances'][0];key=condition_key(request,edge);status=condition_status(request['evaluations'],key);potential=response.get('facts',[]);active=potential if response['status']=='yes' and status=='yes' else []
  conflicts=[]
  for a in active:
   for b in active:
    if a['norm']['mode']=='require' and b['norm']['mode']=='forbid' and a['norm']['action']==b['norm']['action']:conflicts.append([a,b])
  out.update(condition_status=status,condition_key=key,potential_norms=potential,active_norms=active,active_conflicts=conflicts,potential_scope='complete fixed mapped query' if response['status']=='yes' else 'unknown/incomplete mapped query',fulfilled='not-established',admission='not-derived',certificate_scope='typed propagation witnesses retain origin; certificate alone does not establish complete-query/graph validity')
 return out

def main(operation):
 import argparse
 p0=argparse.ArgumentParser(description=__doc__);p0.add_argument('request',type=Path);p0.add_argument('--output',type=Path);args=p0.parse_args()
 try:
  req=p.decode(args.request.read_bytes());s.require(req['operation']==operation,'wrong adapter operation');out=evaluate(req);code=0
 except (resource.Exhausted,subprocess.TimeoutExpired) as ex:out={'status':'unknown-resource','reason':str(ex),'authority_effect':'none'};code=3
 except Exception as ex:out={'status':'invalid','reason':str(ex).splitlines()[0],'authority_effect':'none'};code=2
 if args.output:s.write(args.output,out)
 print(json.dumps(out,indent=2));return code
