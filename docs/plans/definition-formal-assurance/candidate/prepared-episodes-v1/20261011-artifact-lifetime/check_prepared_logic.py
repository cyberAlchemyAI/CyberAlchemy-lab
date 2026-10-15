from pathlib import Path
import sys,types,json,hashlib,ast
root=Path.cwd();p=Path(__file__).resolve().parent/'prepared';art=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.artifact';impl=root/'craft/formalization/candidates/definition-assurance-v1';base=art.parents[1]
code=(p/'build_candidate.py').read_text();ast.parse(code);replacement="UNIT=Path("+repr(str(art))+ ");ROOT=UNIT.parents[6];BASE=UNIT.parents[1]"
code=code.replace('UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1]',replacement)
b=types.ModuleType('build_candidate');b.__file__=str(p/'build_candidate.py');sys.modules['build_candidate']=b;exec(compile(code,str(p/'build_candidate.py'),'exec'),b.__dict__)
m=types.ModuleType('prepared_model');m.__file__=str(p/'verify_candidate.py');exec(compile((p/'verify_candidate.py').read_bytes(),str(p/'verify_candidate.py'),'exec'),m.__dict__)
declarations=[{'kind':'sort','symbol_id':n,'scope':b.SCOPE,'domain_policy':'nonempty'} for n in b.SORTS]+[{'kind':'constant','symbol_id':n,'scope':b.SCOPE,'result_sort':s} for n,s in b.CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':b.SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in b.FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':b.SCOPE,'argument_sorts':args} for n,args in b.SIGNATURE.items()]
rows=[]
for case in m.controls():
 try:
  e=m.v.Denotation(declarations,case['model']);t=all(e.truth(x) for x in b.THEORY);pop=[{'name':n,'truth':e.truth(x)} for n,x in b.required_populations().items()];i=all(x['truth'] for x in pop)
  if case['expected_error'] is not None or t!=case['expected_T'] or (case['expected_I'] is not None and i!=case['expected_I']):raise ValueError('Wrong prepared control '+case['case_id']+' '+str((t,i,pop)))
  rows.append({'case_id':case['case_id'],'T':t,'I':i})
 except m.v.VerificationFault as e:
  if e.code!=case['expected_error']:raise
  rows.append({'case_id':case['case_id'],'rejection':e.code})
print(json.dumps({'result':'PASS-for-prepared-logic-only','controls':len(rows),'T_true':sum(x.get('T') is True for x in rows),'T_false':sum(x.get('T') is False for x in rows),'malformed':sum('rejection' in x for x in rows),'sorts':len(b.SORTS),'declarations':len(declarations),'required_populations':len(b.required_populations()),'native_Lifetime_created':False,'source_fidelity':'pending','mechanized_proof':False},indent=2))
