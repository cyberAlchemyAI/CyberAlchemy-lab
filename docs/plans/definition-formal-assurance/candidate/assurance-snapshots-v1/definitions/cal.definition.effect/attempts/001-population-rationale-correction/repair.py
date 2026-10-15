from pathlib import Path
import shutil,json,hashlib
u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.effect');attempt=u/'attempts/001-population-rationale-correction';initial=attempt/'initial';initial.mkdir(parents=True)
refs=[]
for p in sorted(u.iterdir()):
 if p.is_file():
  shutil.copyfile(p,initial/p.name);refs.append({'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(attempt/'initial-manifest.json').write_text(json.dumps(refs,indent=2,sort_keys=True)+'\n')
(attempt/'NOTE.md').write_text('Initial formulas and producer checks passed, but final review found inherited Contract/Context population rationale wording. Initial fresh contract/model/source/profile checks exited0; dependency and inventory processes were explicitly withdrawn with SIGTERM (exit-15) before changing inputs. Replay parent terminal exit1 observed. All initial files, reports, logs and terminal-result JSON retained here. Correct only explanatory population/dependency/counterexample rationales; preserve sources, declarations, formulas, domains, populations, queries and all twelve owner findings. Rebuild and replay affected evidence before sealing. This initial replay is not completion evidence.\n')
p=u/'build_candidate.py';s=p.read_text();replacements={
 'Supplied contexts/revisions,typed dependency,map membership,present/absent reverse lookup,recompute and separate spelling/containment/import witnesses;not actual consistency,registry completeness,owner or consumer proof.':'Supplied declared effects,change categories,governed identity-or-record,Decision-or-Action links,scoped stage facts,twenty same-record stage distinctions,overlap and exact/successor uses;not actual outcomes,episode independence,trace order,owner or consumer proof.',
 'Actual contract/version/scope/normative/owner/breach and runtime maps unresolved.':'Actual effect kind,subject,scope,actor,stage evidence,trace,authority,owner and consumer maps unresolved.',
 'Exact state/history/order/hash/derived/authority/runtime meanings require independent alignment.':'Exact Effect kind,governance,identity,actor,fact,stage,evidence,authority,relation and runtime meanings require independent alignment.',
 'Declared normative content does not establish compliance or operational authority.':'Declared effect content and stage markers do not establish actual delivery,observation or operational authority.'}
for old,new in replacements.items():assert old in s;s=s.replace(old,new)
p.write_text(s)
produced=['t.json','correspondence.json','static-ir.json','correspondence-check.json','query-policy.json','source-query-obligation.json','denominator.json','clause-analysis.json','comparison-selection.json','model-controls.json','source-checks.json','source-render-1.md','source-render-2.md','authority-profile-checks.json','dependency-selection.json','dependency-graph.json','current-inventory.json','current-dependency-selection.json','current-dependency-graph.json','fresh-command-results.json']
for p in list(u.glob('fresh-*-*.txt'))+[u/x for x in produced]:
 assert (initial/p.name).is_file();p.unlink()
shutil.copyfile('/tmp/repair_effect_metadata.py',attempt/'repair.py')
print(json.dumps({'retained_initial_files':len(refs),'repair':'explanatory-metadata-only','initial_replay_withdrawn':True}))
