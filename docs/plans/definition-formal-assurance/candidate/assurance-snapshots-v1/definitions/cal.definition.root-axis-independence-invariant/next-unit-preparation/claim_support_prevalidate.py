"""Check planned unqualified models in scratch; this is not a target-unit delivery receipt."""
from pathlib import Path
import sys,types,json
builder=Path('/tmp/claim_support_builder.py').read_text().split('def main():')[0]
builder=builder.replace('UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1]',"ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');BASE=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1';UNIT=Path('/tmp/claim-support-prevalidation')")
b=types.ModuleType('build_candidate');b.__file__='/tmp/claim_support_builder.py';sys.modules['build_candidate']=b;exec(compile(builder,b.__file__,'exec'),b.__dict__)
a=types.ModuleType('scratch_controls');exec(compile(Path('/tmp/claim_support_model_head.py').read_text(),'/tmp/claim_support_model_head.py','exec'),a.__dict__)
D=[{'kind':'sort','symbol_id':n} for n in b.SORTS]+[{'kind':'constant','symbol_id':n,'result_sort':s} for n,s in b.CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'argument_sorts':args,'result_sort':s} for n,(args,s) in b.FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'argument_sorts':args} for n,args in b.SIGNATURE.items()]
I=b.required_populations();rows=[]
for case in a.controls():
 try:
  e=a.v.Denotation(D,case['model']);T=all(e.truth(f) for f in b.THEORY);inhabited=all(e.truth(f) for f in I.values());assert case['expected_error'] is None and T==case['expected_T'] and (case['expected_I'] is None or inhabited==case['expected_I']),(case['case_id'],T,inhabited)
  rows.append({'case_id':case['case_id'],'T':T,'I':inhabited})
 except a.v.VerificationFault as err:
  assert err.code==case['expected_error'],(case['case_id'],err.code);rows.append({'case_id':case['case_id'],'rejected':err.code})
report={'status':'PASS-for-scratch-unqualified-planned-controls-only','target_unit_created':False,'source_owner_acceptance':False,'candidate_delivery_sealed':False,'controls':len(rows),'T_true':sum(x.get('T') is True for x in rows),'T_false':sum(x.get('T') is False for x in rows),'malformed':sum('rejected' in x for x in rows),'declarations':len(D),'required_populations':len(I),'results':rows}
Path('/tmp/claim_support_prevalidation_results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
