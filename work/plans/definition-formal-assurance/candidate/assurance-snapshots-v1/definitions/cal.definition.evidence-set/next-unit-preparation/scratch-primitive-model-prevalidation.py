from pathlib import Path
import sys,types,json,time
root=Path.cwd();future=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.finding';b=types.ModuleType('build_candidate');b.__file__=str(future/'build_candidate.py');sys.modules['build_candidate']=b
exec(compile((Path(__file__).resolve().parent/'build_candidate.py').read_bytes(),b.__file__,'exec'),b.__dict__)
m=types.ModuleType('planned_finding_model');m.__file__=str(future/'verify_candidate.py');exec(compile((Path(__file__).resolve().parent/'verify_candidate.py').read_bytes(),m.__file__,'exec'),m.__dict__)
source=b.source_ref(b.snapshot(),'cal.definition.finding');ids={n:b.ir.qualified(source,b.SCOPE,n) for n in b.SORTS+list(b.CONSTANTS)+list(b.FUNCTIONS)+list(b.SIGNATURE)}
decl=[{'kind':'sort','symbol_id':ids[n],'scope':b.SCOPE,'domain_policy':'nonempty'} for n in b.SORTS]+[{'kind':'constant','symbol_id':ids[n],'scope':b.SCOPE,'result_sort':ids[s]} for n,s in b.CONSTANTS.items()]+[{'kind':'total-function','symbol_id':ids[n],'scope':b.SCOPE,'argument_sorts':[ids[s] for s in args],'result_sort':ids[result],'definedness_policy':None} for n,(args,result) in b.FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':ids[n],'scope':b.SCOPE,'argument_sorts':[ids[s] for s in args]} for n,args in b.SIGNATURE.items()]
sorts={n:ids[n] for n in b.SORTS};symbols={n:next(x for x in decl if x['symbol_id']==ids[n]) for n in b.CONSTANTS.keys()|b.FUNCTIONS.keys()|b.SIGNATURE.keys()};T=[b.ir.formula(f,sorts,symbols) for f in b.THEORY];I=[b.ir.formula(f,sorts,symbols) for f in b.required_populations().values()];rows=[]
for case in m.controls():
 model=m.qualify(case['model'],ids)
 try:
  e=m.v.Denotation(decl,model);t=all(e.truth(f) for f in T);i=all(e.truth(f) for f in I);ok=case['expected_error'] is None and t==case['expected_T'] and (case['expected_I'] is None or i==case['expected_I']);row={'case_id':case['case_id'],'T':t,'I':i,'matched':ok}
 except m.v.VerificationFault as err:row={'case_id':case['case_id'],'error':err.code,'matched':err.code==case['expected_error']}
 rows.append(row)
 if not row['matched']:print(json.dumps(row),flush=True)
report={'kind':'scratch-qualified-finite-prevalidation-only','actual_unit_created':False,'controls':len(rows),'results':rows,'actual_execution_or_authority_established':False}
Path('/tmp/finding-prevalidation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'controls':len(rows),'matched':sum(x['matched'] for x in rows),'T_true':sum(x.get('T') is True for x in rows),'T_false':sum(x.get('T') is False for x in rows),'malformed':sum('error' in x for x in rows)}),flush=True)
if not all(x['matched'] for x in rows):raise SystemExit(1)
