"""Compare every supplied well-formed control's old/new population truth; no universal or source-fidelity proof."""
import json
import verify_candidate as a
b=a.b;v=a.v
def verify(write=False):
 old=b.UNIT/'attempts/001-equivalent-population-guard-ordering';oldcore=json.loads((old/'t.json').read_bytes())['payload'];core=a.load('t.json')['payload'];oldir=json.loads((old/'static-ir.json').read_bytes());typed=a.load('static-ir.json');snap=b.snapshot();b.r.verify(snap,b.ROOT)
 without=lambda c:{k:x for k,x in c.items() if k!='populations'}
 if not b.r.same_json(without(oldcore),without(core)) or not b.r.same_json(oldir,b.ir.compile_interpretation(oldcore,snap)) or not b.r.same_json(typed,b.ir.compile_interpretation(core,snap)) or not b.r.same_json(oldir['declarations'],typed['declarations']):raise ValueError('Scope/source/primary theory/signature changed')
 oldp={x['population_id']:x for x in oldir['populations']};newp={x['population_id']:x for x in typed['populations']}
 if set(oldp)!=set(newp) or any(not b.r.same_json({k:x for k,x in oldp[id].items() if k!='statement'},{k:x for k,x in newp[id].items() if k!='statement'}) for id in oldp):raise ValueError('Population obligations/metadata changed')
 ids={x['symbol_id']:b.ir.qualified(core['source'],core['scope'],x['symbol_id']) for x in core['declarations']};rows=[]
 for case in a.controls():
  if case['expected_error'] is not None:continue
  model=a.qualify(case['model'],ids);checks=[]
  for id in sorted(oldp):
   if oldp[id]['requirement']!='required':continue
   before=v.Denotation(oldir['declarations'],model).truth(oldp[id]['statement']);after=v.Denotation(typed['declarations'],model).truth(newp[id]['statement'])
   if before!=after:raise ValueError('Changed supplied model population truth '+case['case_id']+' '+id)
   checks.append({'population_id':id,'old_truth':before,'new_truth':after})
  rows.append({'case_id':case['case_id'],'model_sha256':b.ir.digest(model),'population_truth_comparisons':checks})
 refs=[b.ref(p) for p in [old/'t.json',old/'static-ir.json',b.UNIT/'t.json',b.UNIT/'static-ir.json',b.UNIT/'verify_candidate.py',b.UNIT/'verify_population_reordering.py',b.IMPL/'verifier.py']]
 report={'schema_version':'definition-assurance-population-reordering/v1-candidate','status':'PASS-for-exact-supplied-model-old-new-population-truth-comparisons','authority_effect':'none','input_refs':refs,'well_formed_control_count':len(rows),'required_population_count':10,'exact_truth_comparisons':sum(len(x['population_truth_comparisons']) for x in rows),'rows':rows,'source_scope_signature_primary_theory_unchanged':True,'domains_evaluator_and_budget_unchanged':True,'rewrite_rule':'Commute existential binders and hoist conjuncts before binders whose variables are not free in those conjuncts. Replace existential p equality to total boundPrincipal(b) with its total function value in remaining conjuncts.','evaluation_scope':'Old/new required populations independently evaluated, one fresh unchanged-budget evaluator per formula, solely to inspect this rewrite. Main model controls keep their existing cumulative budget.','source_fidelity':'pending','semantic_ready':False,'mechanized_universal_equivalence_proof':False}
 b.unchanged(refs)
 if write:b.put('population-reordering-checks.json',report)
 elif not b.r.same_json(report,a.load('population-reordering-checks.json')):raise ValueError('Fresh population comparison differs')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({k:x[k] for k in ['status','well_formed_control_count','required_population_count','exact_truth_comparisons','source_scope_signature_primary_theory_unchanged','domains_evaluator_and_budget_unchanged','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()
