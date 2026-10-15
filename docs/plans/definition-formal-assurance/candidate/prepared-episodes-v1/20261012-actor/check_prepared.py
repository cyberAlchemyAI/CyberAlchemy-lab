"""Validate the full prepared signature/populations and independently evaluate every control."""
from pathlib import Path
import sys,ast,json
root=Path.cwd();p=Path(__file__).resolve().parent;dest=p/'prepared';base=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1';sys.path[:0]=[str(dest),str(root/'craft/formalization/candidates/definition-assurance-v1'),str(base/'units/A04')]
import build_candidate as b
import verify_candidate as a
import verifier as v
b.ROOT=root;b.BASE=base;b.IMPL=root/'craft/formalization/candidates/definition-assurance-v1'
source=b.source_ref(b.snapshot(),'cal.definition.actor');doc=b.co.source_document(b.snapshot(),source);N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression';module=ast.parse((dest/'build_candidate.py').read_text());main=next(x for x in module.body if isinstance(x,ast.FunctionDef) and x.name=='main');node=next(x for x in main.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='chosen' for t in x.targets));env=dict(b.__dict__,N=N,F=F);exec(compile(ast.Module(body=[node],type_ignores=[]),'<chosen-source-clauses>','exec'),env);chosen=env['chosen'];units=b.co.inventory(doc);texts=dict(b.co.string_leaves(doc));assert all(s in texts for s in chosen)
clauses=[{'clause_id':'pre-'+str(i),'source_selector':s,'excerpt_sha256':b.r.digest(texts[s].encode()),'start_character':0,'disposition':'encoded','forms':forms,'roles':['definition'],'formal_statement':formula,'rationale':'Prepared exact necessary source guards.'} for i,(s,(formula,forms)) in enumerate(chosen.items())]
populations=[{'population_id':'POP-REQ-'+n,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':z,'scope':b.SCOPE,'rationale':'Authored prepared witness.','review_ref':None} for n,(carrier,z) in b.required_populations().items()]+[{'population_id':'POP-UNRESOLVED-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':b.SCOPE,'rationale':'Pending actual universe and source maps.','review_ref':None} for n,args in b.SIGNATURE.items()]
core={'source':source,'interpretation_id':'prepared-actor-precheck','profile_ref':'profile:prepared-actor-precheck','scope':b.SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':b.declarations(),'clauses':clauses,'depends_on':[],'relations':[],'assumptions':[],'populations':populations}
contract=b.c.validate({'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core},'interpretation');assert contract['status']=='structurally-valid',contract;assert len({x['population_id'] for x in populations})==len(populations)
compiled=b.ir.compile_interpretation(core,b.snapshot());ids={x['symbol_id']:b.ir.qualified(source,b.SCOPE,x['symbol_id']) for x in core['declarations']};results=[];maximum=0
for case in a.controls():
 m=a.qualify(case['model'],ids)
 try:
  e=v.Denotation(compiled['declarations'],m);truths=[e.truth(x['formal_statement']) for x in compiled['clauses']];inhabitation=[e.truth(x['statement']) for x in compiled['populations'] if x['requirement']=='required'];T=all(truths);I=all(inhabitation);maximum=max(maximum,e.steps)
  assert case['expected_error'] is None and T==case['expected_T'] and (case['expected_I'] is None or I==case['expected_I']),(case['case_id'],T,I);results.append({'case_id':case['case_id'],'T':T,'I':I})
 except v.VerificationFault as error:
  assert error.code==case['expected_error'],(case['case_id'],error.code);results.append({'case_id':case['case_id'],'error':error.code})
assert not (base/'definitions/cal.definition.actor').exists()
print(json.dumps({'result':'PASS-prepared-full-contract-unique-populations-exact-source-clauses-and-model-controls','source_units':len(units),'encoded_source_clauses':len(chosen),'sorts':len(b.SORTS),'constants':len(b.CONSTANTS),'functions':len(b.FUNCTIONS),'signatures':len(b.SIGNATURE),'declarations':len(b.declarations()),'required_populations':len(b.required_populations()),'unresolved_populations':len(b.SIGNATURE),'controls':len(results),'T_true':sum(x.get('T') is True for x in results),'T_false':sum(x.get('T') is False for x in results),'malformed':sum('error' in x for x in results),'maximum_steps':maximum,'native_unit_created':False},indent=2))
