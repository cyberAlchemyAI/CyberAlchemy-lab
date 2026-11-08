"""After Project audit, assemble and independently check prepared CI code.

This script is not a native author and writes no BASE/IMPL artifacts. Its
gate prohibits module import, theory compilation or model creation before the
parent's actual full seal and separate audit succeed.
"""
from pathlib import Path
import json,sys
p=Path(__file__).resolve().parent;root=Path.cwd()
parent=root/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261012-project'
base=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'
native=base/'definitions/cal.definition.capability-instance'
for stem in ['full-delivery-seal','full-delivery-audit']:
 path=parent/(stem+'-command-result.json')
 if not path.is_file():raise RuntimeError('Parent Project actual full '+stem+' not yet observed; no imports/evaluation performed.')
 row=json.loads(path.read_bytes());err=Path(row['stderr']);err=err if err.is_absolute() else parent/err
 if row['exit_code'] or err.read_bytes():raise RuntimeError('Parent Project full delivery failed; no next-unit evaluation.')
assert not native.exists()
sys.path[:0]=[str(p/'prepared'),str(root/'craft/formalization/candidates/definition-assurance-v1'),str(base/'units/A04')]
import build_candidate as b
import verify_candidate as a
import verifier as v
source=b.source_ref(b.snapshot(),'cal.definition.capability-instance')
assert source['sha256']=='d1e0140d47887b3f8c49334e81c33bd105edaecaf02f3df3df841885340505a5'
prior=json.loads((base/'definitions/CAV2-D60/delivery-manifest.json').read_bytes())
b.unchanged(prior['files'])
doc=b.co.source_document(b.snapshot(),source);rows=b.selected_clauses(doc)
clauses=[{'clause_id':'pre-'+str(i),'source_selector':x['source_selector'],'excerpt_sha256':b.r.digest(x['excerpt'].encode()),'start_character':x['start_character'],'disposition':x['disposition'],'forms':x['forms'],'roles':['definition'] if x['disposition']=='encoded' else ['explanation-example'] if x['disposition']=='explanatory' else ['unresolved'],'formal_statement':x['formula'],'rationale':'Prepared owner-local exact-version instance,contexts,claim lanes,recursion andterminal handoff guards.'} for i,x in enumerate(rows)]
pops=[{'population_id':'POP-REQ-'+n,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':z,'scope':b.SCOPE,'rationale':'Prepared example population checked independently of T.','review_ref':None} for n,(carrier,z) in b.required_populations().items()]+[{'population_id':'POP-UNRESOLVED-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':b.SCOPE,'rationale':'Actual universe andaccepted owner/consumer denotations pending.','review_ref':None} for n,args in b.SIGNATURE.items()]
core={'source':source,'interpretation_id':'prepared-CapabilityInstance-precheck','profile_ref':'profile:prepared-CapabilityInstance-precheck','scope':b.SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':b.declarations(),'clauses':clauses,'depends_on':[],'relations':[],'assumptions':[],'populations':pops}
assert b.c.validate({'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core},'interpretation')['status']=='structurally-valid'
compiled=b.ir.compile_interpretation(core,b.snapshot())
ids={x['symbol_id']:b.ir.qualified(source,b.SCOPE,x['symbol_id']) for x in core['declarations']}
results=[];maximum=0;cases=a.controls()
assert len({x['case_id'] for x in cases})==len(cases)
for case in cases:
 model=a.qualify(case['model'],ids)
 try:
  e=v.Denotation(compiled['declarations'],model)
  T=all([e.truth(x['formal_statement']) for x in compiled['clauses'] if x['disposition']=='encoded'])
  I=all([e.truth(x['statement']) for x in compiled['populations'] if x['requirement']=='required'])
  maximum=max(maximum,e.steps)
  assert case['expected_error'] is None and T==case['expected_T'] and (case['expected_I'] is None or I==case['expected_I']),(case['case_id'],T,I)
  results.append({'case_id':case['case_id'],'T':T,'I':I})
 except v.VerificationFault as error:
  assert error.code==case['expected_error'],(case['case_id'],error.code)
  results.append({'case_id':case['case_id'],'error':error.code})
for q in b.query_specs():
 e=v.Denotation(compiled['declarations'],a.qualify(a.base_model(),ids))
 assert e.truth(v.renamed(q['target'],ids)) is False and e.truth(v.renamed(q['witness_condition'],ids)) is True,q['query_id']
texts=dict(b.co.string_leaves(doc))
for unit in b.co.inventory(doc):
 spans=[(x['start_character'],x['start_character']+len(x['excerpt']),x['excerpt']) for x in rows if x['source_selector']==unit['selector']]
 assert spans[0][0]==0 and spans[-1][1]==len(texts[unit['selector']]) and ''.join(x[2] for x in spans)==texts[unit['selector']]
b.unchanged(prior['files'])
assert not native.exists()
print(json.dumps({'result':'PASS-prepared-source-contract-populations-controls-and-conditioned-countermodels','source_units':len(b.co.inventory(doc)),'mapped_source_clauses':len(rows),'encoded_source_clauses':sum(x['disposition']=='encoded' for x in rows),'explanatory_source_clauses':sum(x['disposition']=='explanatory' for x in rows),'deferred_source_clauses':sum(x['disposition']=='deferred' for x in rows),'sorts':len(b.SORTS),'constants':len(b.CONSTANTS),'functions':len(b.FUNCTIONS),'signatures':len(b.SIGNATURE),'declarations':len(b.declarations()),'required_populations':len(b.required_populations()),'unresolved_populations':len(b.SIGNATURE),'controls':len(results),'T_true':sum(x.get('T') is True for x in results),'T_false':sum(x.get('T') is False for x in results),'malformed':sum('error' in x for x in results),'countermodel_queries':len(b.query_specs()),'conditioned_queries':2,'maximum_steps':maximum,'native_unit_created':False,'source_fidelity':'pending','semantic_ready':False},indent=2))

