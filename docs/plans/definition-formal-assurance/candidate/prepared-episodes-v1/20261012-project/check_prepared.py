"""Pre-native full contract,source correspondence and independent T/I/countermodel check."""
from pathlib import Path
import sys,json
p=Path(__file__).resolve().parent;root=Path.cwd();base=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1';sys.path[:0]=[str(p/'prepared'),str(root/'craft/formalization/candidates/definition-assurance-v1'),str(base/'units/A04')]
import build_candidate as b
import verify_candidate as a
import verifier as v
b.ROOT=root;b.BASE=base;b.IMPL=root/'craft/formalization/candidates/definition-assurance-v1'
source=b.source_ref(b.snapshot(),'CAV2-D60');doc=b.co.source_document(b.snapshot(),source);rows=b.selected_clauses(doc);clauses=[{'clause_id':'pre-'+str(i),'source_selector':x['source_selector'],'excerpt_sha256':b.r.digest(x['excerpt'].encode()),'start_character':x['start_character'],'disposition':x['disposition'],'forms':x['forms'],'roles':['definition'] if x['disposition']=='encoded' else ['explanation-example'] if x['disposition']=='explanatory' else ['unresolved'],'formal_statement':x['formula'],'rationale':'Prepared Project eleven fields,Goal cardinality,state conditions,explicit membership and identity continuity.'} for i,x in enumerate(rows)]
pops=[{'population_id':'POP-REQ-'+n,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':z,'scope':b.SCOPE,'rationale':'Prepared supplied population witness.','review_ref':None} for n,(carrier,z) in b.required_populations().items()]+[{'population_id':'POP-UNRESOLVED-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':b.SCOPE,'rationale':'Actual universe/owner mappings pending.','review_ref':None} for n,args in b.SIGNATURE.items()]
core={'source':source,'interpretation_id':'prepared-CAV2-D60-Project-precheck','profile_ref':'profile:prepared-CAV2-D60-Project-precheck','scope':b.SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':b.declarations(),'clauses':clauses,'depends_on':[],'relations':[],'assumptions':[],'populations':pops}
assert b.c.validate({'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core},'interpretation')['status']=='structurally-valid'
assert len({x['population_id'] for x in pops})==len(pops);compiled=b.ir.compile_interpretation(core,b.snapshot());ids={x['symbol_id']:b.ir.qualified(source,b.SCOPE,x['symbol_id']) for x in core['declarations']};results=[];maximum=0
for case in a.controls():
 model=a.qualify(case['model'],ids)
 try:
  e=v.Denotation(compiled['declarations'],model);T=all([e.truth(x['formal_statement']) for x in compiled['clauses'] if x['disposition']=='encoded']);I=all([e.truth(x['statement']) for x in compiled['populations'] if x['requirement']=='required']);maximum=max(maximum,e.steps)
  assert case['expected_error'] is None and T==case['expected_T'] and (case['expected_I'] is None or I==case['expected_I']),(case['case_id'],T,I)
  results.append({'case_id':case['case_id'],'T':T,'I':I})
 except v.VerificationFault as error:
  assert error.code==case['expected_error'],(case['case_id'],error.code);results.append({'case_id':case['case_id'],'error':error.code})
for q in b.query_specs():
 e=v.Denotation(compiled['declarations'],a.qualify(a.base_model(),ids));assert e.truth(v.renamed(q['target'],ids)) is False and e.truth(v.renamed(q['witness_condition'],ids)) is True,q['query_id']
texts=dict(b.co.string_leaves(doc))
for unit in b.co.inventory(doc):
 spans=[(x['start_character'],x['start_character']+len(x['excerpt']),x['excerpt']) for x in rows if x['source_selector']==unit['selector']];assert spans[0][0]==0 and spans[-1][1]==len(texts[unit['selector']]) and ''.join(x[2] for x in spans)==texts[unit['selector']]
assert not (base/'definitions/CAV2-D60').exists()
print(json.dumps({'result':'PASS-prepared-complete-source-contract-populations-controls-and-countermodels','source_units':len(b.co.inventory(doc)),'mapped_source_clauses':len(rows),'encoded_source_clauses':sum(x['disposition']=='encoded' for x in rows),'explanatory_source_clauses':sum(x['disposition']=='explanatory' for x in rows),'deferred_source_clauses':sum(x['disposition']=='deferred' for x in rows),'sorts':len(b.SORTS),'constants':len(b.CONSTANTS),'functions':len(b.FUNCTIONS),'signatures':len(b.SIGNATURE),'declarations':len(b.declarations()),'required_populations':len(b.required_populations()),'unresolved_populations':len(b.SIGNATURE),'controls':len(results),'T_true':sum(x.get('T') is True for x in results),'T_false':sum(x.get('T') is False for x in results),'malformed':sum('error' in x for x in results),'countermodel_queries':len(b.query_specs()),'maximum_steps':maximum,'native_unit_created':False},indent=2))

