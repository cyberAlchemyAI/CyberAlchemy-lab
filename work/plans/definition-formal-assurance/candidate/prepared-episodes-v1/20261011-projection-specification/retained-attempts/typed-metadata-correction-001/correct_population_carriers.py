"""Retain the successful initial typed packet, then correct two population carrier labels."""
from pathlib import Path
import json,hashlib,shutil,ast
root=Path.cwd();p=Path(__file__).resolve().parent;u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.projection-specification';ret=u/'retained-stages/initial-native-typed';ret.mkdir(parents=True)
def ref(q):return {'path':q.relative_to(root).as_posix(),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}
rows=[]
for q in sorted(u.iterdir()):
 if not q.is_file() or q.suffix=='.pyc':continue
 target=ret/'native'/q.name;target.parent.mkdir(exist_ok=True)
 with target.open('xb') as f:f.write(q.read_bytes())
 rows.append({'original_ref':ref(q),'retained_ref':ref(target)})
for q in [p/'prepared/build_candidate.py',p/'check_prepared.py',*[p/('prepared-check-'+n) for n in ['command-result.json','stdout.txt','stderr.txt']]]:
 target=ret/'preparation'/q.name;target.parent.mkdir(exist_ok=True)
 with target.open('xb') as f:f.write(q.read_bytes())
 rows.append({'original_ref':ref(q),'retained_ref':ref(target)})
for stem in ['author','build','model','source']:
 x=json.loads((u/(stem+'-command-result.json')).read_text());assert x['exit_code']==0 and not (u/x['stderr']).read_bytes()
assert json.loads((p/'prepared-check-command-result.json').read_text())['exit_code']==0
with (ret/'manifest.json').open('x') as f:json.dump({'authority_effect':'none','result':'retained-successful-initial-partial-stage','reason':'Two Meaning witness formulas had ConceptReference population labels; correction changes carrier metadata only, not formula semantics or source.','files':rows,'original_native_producer_exit_codes':{n:0 for n in ['author','build','model','source']},'retained_failure':False,'semantic_ready':False,'source_fidelity':'pending'},f,indent=2,sort_keys=True);f.write('\n')
for q in [u/'build_candidate.py',p/'prepared/build_candidate.py']:
 s=q.read_text();before="'carrier':'ConceptReference','predicate_ref':None,'requirement':'required'";after="'carrier':'MeaningReference' if n in ['SelectedMeaning','CanonicalMeaningWithDeclaredSourceRelations'] else 'ConceptReference','predicate_ref':None,'requirement':'required'";assert s.count(before)==1;s=s.replace(before,after);ast.parse(s);q.write_text(s)
q=p/'check_prepared.py';s=q.read_text();before="'carrier':'ConceptReference','predicate_ref':None,'requirement':'required'";after="'carrier':'MeaningReference' if n in ['SelectedMeaning','CanonicalMeaningWithDeclaredSourceRelations'] else 'ConceptReference','predicate_ref':None,'requirement':'required'";assert s.count(before)==1;s=s.replace(before,after);ast.parse(s);q.write_text(s)
# Keep the regeneration source synchronized, without rerunning its exclusive writer.
q=p/'prepare_typed.py';s=q.read_text();assert s.count(before)==1;q.write_text(s.replace(before,after))
for n in ['command-result.json','stdout.txt','stderr.txt']:(p/('prepared-check-'+n)).unlink()
outputs=['t.json','correspondence.json','static-ir.json','correspondence-check.json','query-policy.json','source-query-obligation.json','denominator.json','clause-analysis.json','comparison-selection.json','model-controls.json','source-checks.json','source-render-1.md','source-render-2.md']
outputs += [stem+'-'+suffix for stem in ['build','model','source'] for suffix in ['command-result.json','stdout.txt','stderr.txt']]
for n in outputs:(u/n).unlink()
q=u/'context.json';x=json.loads(q.read_text());original=next(z['retained_ref'] for z in rows if z['original_ref']['path']==q.relative_to(root).as_posix());x['retained_successful_prior_stage_refs']=[ref(ret/'manifest.json')];x['typed_metadata_correction']={'reason':'Meaning-only required populations now declare MeaningReference carrier.','changed_population_ids':['POP-SelectedMeaning','POP-CanonicalMeaningWithDeclaredSourceRelations'],'original_context_ref':original,'actual_formula_semantics_changed':False,'source_bytes_changed':False,'original_native_producers_terminal_zero':True};x['external_sources']=[ref(Path(z['absolute_path']))|{'absolute_path':z['absolute_path']} for z in x['external_sources']];x['external_sources']=[{'absolute_path':z['absolute_path'],'sha256':z['sha256']} for z in x['external_sources']];q.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
print(json.dumps({'retained_original_files':len(rows),'corrected_Meaning_population_labels':2,'actual_formula_semantics_changed':False,'source_bytes_changed':False}))
