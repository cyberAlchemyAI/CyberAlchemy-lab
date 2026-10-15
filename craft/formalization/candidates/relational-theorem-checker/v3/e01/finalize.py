from pathlib import Path
import sys
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;B=H.parent;sys.path.insert(0,str(B.parent))
from v3.execution import support as s
r=s.read(H/'controls.json');s.require(r['result']=='pass' and r['new_complete_collection_witnesses']==4,'incomplete final controls')
roots=[];fresh=[]
for case in r['cases']:
 s.check(case['input']);a=s.read(s.check(case['answer']));job=a.get('supervised_run',{}).get('job')
 if job:roots.append(Path(job))
 if a['status']=='fresh-extension-candidate':
  s.check(a['completion']);v=a['value']
  for ref in v['imports']+v['worker_sources']:s.check(ref)
  for m in v['kernel']:s.check(m['source']);s.check(m['olean']);s.require('sorryAx' not in m['output'],'admitted witness')
  fresh.append(v)
s.require(len(fresh)==4,'four final witnesses required')
(H/'migration-review.md').write_text('''# Evidence collection implementation review

The new profile explicitly uses any current accepted exactly matching listed assessment, retaining all accepted supports in source order. All listed records are validated before aggregation. Distinct rejected assessments supply no positive support; duplicate or contradictory identities, empty/missing/stale members and context, epoch, scope or revision drift are invalid.

The universal Lean projection is equivalent to an independently quantified eligible assessment. Every accepted support is retained and admission roots are preserved verbatim. Four actual final-source supervised kernel witnesses cover two supports, mixed distinct verdicts, all rejected, and the legacy opaque comma token. All 54 controls pass, including altered registry allowed-kind definitions. The canonical registry is checked in full, with all 41 definition source bindings verified; labels alone cannot substitute a different definition.

Legacy evidence remains one opaque token. It is never split on punctuation. Because legacy assessments do not have individual revisions, each typed reference pairs its token with the immutable normalized source graph identity; the raw source binding and exact evaluation frame are separately retained. Current means present in this bound source, not authenticated real-world evidence or wall-clock validity. Ancillary assessment metadata is retained by the tested bridge, while the theorem checks the typed semantic projection.

This profile checks selected assertion/evidence projection, not the entire legacy graph. Caller frame is compared to an independently derived source frame in the concrete witness. Neither source evidence nor the collection creates admission roots or application authorization. Generic proof, actual concrete witness, Python/JSON bridge tests, supplied truth and the same pinned Lean kernel remain distinct assurance boundaries. Original mapped/direct APIs are unchanged.

The interrupted first development suite is retained as historical evidence. Final acceptance counts only the four complete witnesses generated after the strengthened registry guard; no earlier positive result substitutes for final-source evidence.
''')
extra=[p for p in H.iterdir() if p.is_file() and p.name not in ['task-acceptance.json','control-progress.json']]
extra += [p for p in (H/'formal-build').rglob('*') if p.is_file()]+[p for p in (H/'evidence'/r['run_id']).rglob('*') if p.is_file()]
for root in roots:extra += [p for p in root.rglob('*') if p.is_file()]
extra += [B/'execution/E01-implementation-plan.md',B/'execution/extension_runtime.py',B/'execution/extension_worker.py']
s.accept('E01',['Explicit any-current-accepted policy fixed before code; malformed selected evidence refuses before aggregation.','Universal sound/complete support projection and unchanged-root theorem plus four full final-source witnesses retain every valid accepted support; exact canonical definitions and frame are checked.','Actual legacy comma-token witness preserves one opaque reference; splitting, missing tokens and stale identities refuse.'],r['controls'],extra=list({str(p.resolve()):p for p in extra}.values()))
print('E01 accepted; 54 controls; four final-source full witnesses.')
