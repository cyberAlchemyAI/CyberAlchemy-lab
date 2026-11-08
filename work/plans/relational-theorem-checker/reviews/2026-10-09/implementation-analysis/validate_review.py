#!/usr/bin/env python3
"""Validate review coverage, source bindings and proposal DAG; not future implementation."""
from pathlib import Path
import importlib.util,json,hashlib,re,ast,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'craft/formalization').is_dir())
BASE=ROOT/'craft/formalization/candidates/relational-theorem-checker/v1'
def read(p):return json.loads(p.read_text())
def require(c,msg):
 if not c:raise ValueError(msg)
def check(b):
 p=(ROOT/b['path']).resolve();require(p.is_relative_to(ROOT) and p.is_file(),'missing/outside source '+b['path'])
 require(hashlib.sha256(p.read_bytes()).hexdigest()==b['sha256'],'stale binding '+b['path']);return p

def validate():
 spec=importlib.util.spec_from_file_location('parent_review_validation',HERE.parent/'validate_review.py');parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
 inherited=parent.validate()
 bindings=read(HERE/'source-bindings.json')
 for b in bindings['sources']+bindings['parent_snapshot_bindings']+[bindings['inherited_audit']]:check(b)
 inv=read(HERE/'definition-inventory.json');defs=inv['formal_definitions'];relations=inv['relations']
 require(len({d['id'] for d in defs})==len(defs),'duplicate definition')
 decl=re.compile(r'^(?:(?:private|noncomputable|partial|unsafe)\s+)*(def|abbrev|inductive|structure)\s+([A-Za-z0-9_.]+)',re.M)
 observed=set()
 for module in inv['modules']:
  text=(BASE/module).read_text().split('namespace Witnesses')[0]
  matches=list(decl.finditer(text))
  for i,m in enumerate(matches):
   id=module+'#'+m.group(2);observed.add(id)
   row=next(d for d in defs if d['id']==id);line=text[:m.start()].count('\n')+1
   end=matches[i+1].start() if i+1<len(matches) else len(text)
   excerpt=re.split(r'\n(?:instance|theorem|namespace|end |#print)',text[m.start():end],maxsplit=1)[0].strip()
   require(row['line']==line and row['definition_excerpt']==excerpt,'definition selector/body drift '+id)
   require(row['definition_excerpt_sha256']==hashlib.sha256(excerpt.encode()).hexdigest(),'excerpt hash drift')
   check(row['source']);require(row['analysis'] and row['meaning'] and row['boundary_question'] and row['review_status']=='reviewed','unreviewed definition')
 require(observed=={d['id'] for d in defs},'formal definition coverage gap')
 registry=read(BASE/'registry/normalized-registry.json')
 require(len(relations)==41 and {r['id'] for r in relations}=={k['id'] for k in registry['kinds']},'relation coverage gap')
 for r in relations:
  source=read(check(r['source']))['payload'];k=next(k for k in registry['kinds'] if k['id']==r['id'])
  for key in ['unique_question','operational_effect','forbidden_inferences']:require(r[key]==source[key]==k[key],'source meaning drift '+r['id'])
  require(r['endpoint_pairs']==source['allowed_endpoint_pairs']==k['pairs'],'pair coverage drift')
  require(r['qualifier_contract']==source['qualifier_contract'] and r['qualifier_fields']==k['fields'],'qualifier drift')
  require(r['declared_version']==k['version'],'kind version drift')
  require(all(r[x] for x in ['current_coverage','gap','proposed_improvement','controls','task_refs']),'empty relation review')
  require(r['review_status']=='reviewed' and not r['semantic_expansion_authorized'],'relation posture drift')
 plan=read(HERE/'revised-plan.json');check(plan['supersedes_for_proposal_only'])
 tasks=plan['tasks'];by_id={t['id']:t for t in tasks};require(len(by_id)==len(tasks),'duplicate task')
 require(plan['status']=='proposal-not-executed' and plan['authority_effect']=='none','proposal posture')
 require(tasks[0]['id']==plan['first_step']=='S00' and not tasks[0]['depends_on'],'formalization first')
 active=set();done=set()
 def visit(id):
  require(id in by_id,'unknown dependency '+id);require(id not in active,'DAG cycle '+id)
  if id in done:return
  active.add(id)
  for dep in by_id[id]['depends_on']:visit(dep)
  active.remove(id);done.add(id)
 def ancestors(id):
  result=set()
  for dep in by_id[id]['depends_on']:result.add(dep);result|=ancestors(dep)
  return result
 for id in by_id:visit(id)
 findings=read(HERE/'findings.json')['findings'];fids={f['id'] for f in findings};units=[]
 for t in tasks:
  require(t['status']=='proposed' and t['authority_effect']=='none','task posture')
  require(t['id']=='S00' or 'S00' in ancestors(t['id']),'formalization bypass')
  require(t['write_scope'].startswith(plan['implementation_namespace']+'/') and '..' not in t['write_scope'],'unsafe write scope')
  require(set(t['implementation_finding_refs'])<=fids and t['implementation_finding_refs'],'unmapped task')
  for key in ['inputs','outputs','algorithm','edge_cases','acceptance_criteria','validation','working_units']:require(t[key],'task detail absent')
  for u in t['working_units']:
   require(u['parent']==t['id'] and u['write_scope']==t['write_scope'] and u['evidence']==t['outputs'] and u['verification']==t['validation'],'SWU drift');units.append(u)
 require(read(HERE/'swu-manifest.json')['units']==units,'SWU manifest drift')
 require(len({u['id'] for u in units})==len(units),'SWU duplicate')
 require({f for t in tasks for f in t['implementation_finding_refs']}==fids,'finding without task')
 for f in findings:
  check(f['source']);require(set(f['task_refs'])<=set(by_id),'unknown finding task')
 for row in defs+relations:require(set(row['finding_refs'])<=fids and row['finding_refs'],'missing finding mapping')
 for row in relations+inv['proposed_definitions']:require(set(row['task_refs'])<=set(by_id),'unknown definition task')
 # Check the implementation-driven corrections, not only generic acyclicity.
 for id in ['S05','S06','S07','S09']:require('S15' in ancestors(id),'baseline contract introduced too late')
 for id in ['S03','S05','S06','S07']:require('S16' in ancestors(id),'sealed producer prerequisite absent')
 for id in ['S05','S06','S07']:require('S17' in ancestors(id),'resource prerequisite absent')
 for id in ['S05','S07','S09']:require('S18' in ancestors(id),'source-transition prerequisite absent')
 require('S03' not in ancestors('S05'),'contextual adapter unnecessarily blocked by recursive proof')
 require('S12' not in ancestors('S13') and plan['optimization_optional'],'optional optimization became hard gate')
 require(by_id['S13']['conditional_dependencies']==[{'task':'S12','when':'optimized evaluator selected','otherwise':'use qualified reference within envelope'}],'conditional gate drift')
 require(plan['edge_count']==sum(len(t['depends_on']) for t in tasks),'edge count drift')
 minimum=set(plan['minimum_release_tasks'])
 for id in list(minimum):minimum|=ancestors(id)
 probe=read(HERE/'probe-report.json')
 for b in probe['sources']:check(b)
 require(probe['result']=='pass' and all(probe[k] for k in ['generic_normalizer_accepts_ordinary_semantic_head','generic_normalizer_accepts_ordinary_semantic_seeds','captured_workflow_rejects_new_head']),'probe failed')
 refresh=read(HERE/'refresh-report.json');require(refresh['mutation_mode']=='proposal-only' and not refresh['appliedChanges'] and not refresh['mutation_ready'],'refresh posture')
 require({x['id'] for x in refresh['sourceSignals']}==fids,'refresh finding coverage')
 require({f for c in refresh['proposedChanges'] for f in c['signal_refs']}==fids,'refresh trace gap')
 links=0
 for p in HERE.glob('*.md'):
  text=p.read_text();require(text.count('```')%2==0,'unbalanced fences '+p.name)
  for target in re.findall(r'\]\(([^)]+)\)',text):
   if target.startswith('https://'):continue
   target=re.sub(r':\d+$','',target).split('#')[0];path=Path(target) if target.startswith('/') else HERE/target
   require(path.is_file(),'broken link '+target);links+=1
 for p in HERE.glob('*.py'):ast.parse(p.read_text())
 package=[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation-report.json']
 return {'schema':'relational.implementation-review-validation/v1','date':'2026-10-09','result':'pass','formal_definitions':len(defs),'formal_modules':len(inv['modules']),'relations':len(relations),'proposed_definitions':len(inv['proposed_definitions']),'findings':len(findings),'tasks':len(tasks),'working_units':len(units),'required_dependency_edges':plan['edge_count'],'conditional_dependency_edges':1,'formalization_first':True,'contextual_release_tasks_including_ancestors':sorted(minimum),'source_bindings':len(bindings['sources']),'accepted_receipts_preserved_current':inherited['accepted_receipts_current'],'accepted_artifact_dependency_binding_checks':inherited['accepted_artifact_dependency_bindings_checked'],'original_pending_human_tasks':inherited['original_pending_human_tasks'],'parent_review_preserved':True,'document_file_links':links,'normalizer_and_guard_probe':'pass','package_bindings':package,'method':'Read-only source/receipt binding checks, definition inventory/body coverage, relation source correspondence, traceability, DAG checks and small Python probes. No new Lean proof or successor runtime execution.','authority_effect':'none'}
if __name__=='__main__':
 try:
  result=validate()
  if '--write' in sys.argv:(HERE/'validation-report.json').write_text(json.dumps(result,indent=2)+'\n')
  print(json.dumps({k:v for k,v in result.items() if k!='package_bindings'},indent=2))
 except (ValueError,KeyError,OSError,StopIteration) as error:
  print('Review validation failed: '+str(error),file=sys.stderr);sys.exit(1)
