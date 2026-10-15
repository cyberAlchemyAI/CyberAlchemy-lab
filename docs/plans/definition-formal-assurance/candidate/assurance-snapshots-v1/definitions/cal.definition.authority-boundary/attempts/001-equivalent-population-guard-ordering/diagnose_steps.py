"""Read-only per-control evaluator step observation; no proof or changed resource budget."""
import json
import verify_candidate as a
b=a.b;v=a.v;core=a.load('t.json')['payload'];typed=a.load('static-ir.json');ids={x['symbol_id']:b.ir.qualified(core['source'],core['scope'],x['symbol_id']) for x in core['declarations']}
for case in a.controls():
 if case['expected_error'] is not None:continue
 e=v.Denotation(typed['declarations'],a.qualify(case['model'],ids));rows=[]
 try:
  for x in [x for x in typed['clauses'] if x['disposition']=='encoded']+[x for x in typed['populations'] if x['requirement']=='required']:
   id=x.get('clause_id',x.get('population_id'));before=e.steps;truth=e.truth(x.get('formal_statement',x.get('statement')));rows.append({'id':id,'truth':truth,'steps':e.steps-before})
  print(json.dumps({'case_id':case['case_id'],'total_steps':e.steps,'rows':rows}))
 except v.VerificationFault as error:print(json.dumps({'case_id':case['case_id'],'fault':error.code,'at':id,'total_steps':e.steps,'rows':rows}))
