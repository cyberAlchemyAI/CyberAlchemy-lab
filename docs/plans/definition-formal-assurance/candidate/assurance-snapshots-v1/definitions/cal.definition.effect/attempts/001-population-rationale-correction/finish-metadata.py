from pathlib import Path
import json
u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.effect');attempt=u/'attempts/001-population-rationale-correction'
(attempt/'metadata-comparison-NOTE.md').write_text('The first post-repair metadata comparison exited1 at static-ir.json because it stripped rationale fields but retained input_core_sha256 and ir_sha256. T and correspondence comparisons had passed. Inspection confirmed only rationale-bearing input_core/populations and their derived digests changed. Corrected comparator excludes these two derived digests after the normal finalizer independently recompiles and checks the full current IR. No signature,formula,query,domain,population or finding change is permitted.\n')
(attempt/'metadata-comparison-stderr.txt').write_text('Traceback (most recent call last):\n  File "<stdin>", line 9, in <module>\nAssertionError: static-ir.json\n');(attempt/'metadata-comparison-stdout.txt').write_text('')
def semantic(v):
 if isinstance(v,dict):return {k:semantic(x) for k,x in v.items() if k not in ['rationale','input_core_sha256','ir_sha256']}
 if isinstance(v,list):return [semantic(x) for x in v]
 return v
for name in ['t.json','correspondence.json','static-ir.json']:
 assert semantic(json.loads((u/name).read_text()))==semantic(json.loads((attempt/'initial'/name).read_text())),name
print('Sources,signature,formulas,domains,populations,queries and findings unchanged;only explanatory rationales and their derived IR digests changed.')
p=u/'finalize.py';s=p.read_text();needle=" review=(b.UNIT/'REVIEW.md').read_text();"
insert=""" attempt=b.UNIT/'attempts/001-population-rationale-correction';retained=json.loads((attempt/'initial-manifest.json').read_bytes());require(len(retained)==57 and all(b.r.digest((attempt/'initial'/x['path']).read_bytes())==x['sha256'] for x in retained),'Initial correction evidence changed')
 initial_fresh=json.loads((attempt/'initial/fresh-command-results.json').read_bytes());require([x['exit_code'] for x in initial_fresh]==[0,0,0,0,-15,-15] and all(not (attempt/'initial'/x['stderr']).read_bytes() for x in initial_fresh),'Withdrawn replay mislabeled')
 def semantics(x):
  if isinstance(x,dict):return {k:semantics(z) for k,z in x.items() if k not in ['rationale','input_core_sha256','ir_sha256']}
  if isinstance(x,list):return [semantics(z) for z in x]
  return x
 for name in ['t.json','correspondence.json','static-ir.json']:require(semantics(load(name))==semantics(json.loads((attempt/'initial'/name).read_bytes())),'Rationale correction changed semantics')
 require(load('denominator.json')==json.loads((attempt/'initial/denominator.json').read_bytes()) and load('query-policy.json')==json.loads((attempt/'initial/query-policy.json').read_bytes()),'Rationale correction changed denominators or queries')
"""
assert needle in s;s=s.replace(needle,insert+needle)
s=s.replace("'preserved_attempts':[]", "'preserved_attempts':[{'path':'attempts/001-population-rationale-correction','result':'Inherited population/dependency/counterexample rationales corrected after retaining57initialfiles;four initial freshchecks exited0,two withdrawn exit-15,parent exit1observed. Initial metadata comparator retained derived IR digests and exited1;corrected comparator verifies unchanged semantics excluding rationales and their two derived digests. Sources,signature,formulas,domains,populations,queries and findings preserved;producer/fresh evidence regenerated.'}]")
p.write_text(s)
p=u/'REVIEW.md';s=p.read_text();old='No failed authoring attempt occurred in this unit before the initial review. Successful author, build and producer logs are retained. Any later failed finalizer or replay is retained before repair, and does not become successful evidence by changing a reported status. Corrections must preserve source obligations and fixed model domains; an unavailable exact primitive remains a visible semantic obligation rather than a reason to substitute a neighbor or claim owner acceptance.'
new='Final review found inherited Contract/Context wording in population rationales. All 57 initial unit files are retained with a hash manifest. Four initial fresh checks exited zero; two long dependency/inventory checks were explicitly withdrawn with SIGTERM and exited -15, and the replay parent exited one. This withdrawn replay is not completion evidence. The correction changes only population, dependency and counterexample rationales. A first metadata comparator exited one because it retained the two IR digests derived from the changed annotations; the trace and explanation are retained. The corrected comparator checks source selection, declarations, formulas, domains, populations, queries and findings without annotations or those derived digests, while normal validation separately recompiles and verifies the full current IR. Fresh producer and terminal evidence are regenerated. An unavailable primitive remains visible residue and does not authorize substitution or owner acceptance.'
assert old in s;p.write_text(s.replace(old,new));compile((u/'finalize.py').read_text(),str(u/'finalize.py'),'exec')
