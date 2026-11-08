import pathlib,json,hashlib
R=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab'); L=R/'implementation/lab-runtime/local-host'; E=L/'independent-reader-entrypoint-review-0003'; C=L/'reader-only-entrypoint-0003'
def binding(p):
 b=p.read_bytes(); return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(b).hexdigest(),'size':len(b)}
def verify(p,pin,base):
 b=binding(p)
 if b['sha256']!=pin:raise RuntimeError('freeze mismatch')
 f=json.loads(p.read_bytes()); out=[b]
 for row in f['file_bindings']:
  actual=binding(base/row['path'])
  if actual['sha256']!=row['sha256'] or actual['size']!=row['size']:raise RuntimeError('member mismatch')
  out.append(actual)
 return out
bindings=verify(C/'freeze.json','c6d5f11ef3c3964b8fbc58ed05880f09c5d1f108d76cc6d659f352e60c7f6a7e',C)
bindings+=verify(L/'fresh-reader-docker-0005/freeze.json','28d97810e1c3ac77aceee504a49a4e3e0c57fe08c520053b1c46b62c61e326a1',R)
results={}
for mode in ['normal','optimized']:
 results[mode]=json.loads((E/(mode+'.log')).read_text().splitlines()[-1])
 if not results[mode]['passed'] or results[mode]['tests']!=16 or not results[mode]['post_verified']:raise RuntimeError('test outcome mismatch')
bindings += [binding(E/n) for n in ['checks.py','normal.log','optimized.log','finalize.py']]
(E/'bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
report={
 'schema_version':'independent-reader-entrypoint-review/v1','candidate':'reader-only-entrypoint-0003','reviewer':'evidence_review','verdict':'HOLD','effect':'NOT_RUN',
 'freeze_sha256':bindings[0]['sha256'],'bindings':binding(E/'bindings.json'),
 'verification':{'candidate_members':6,'selected_reader_0005_members':22,'normal_tests':16,'optimized_tests':16,'independent_observations_per_mode':3,'source_pre_post_unchanged':True,'results':results},
 'findings':[
 {'id':'RE3-R01','severity':'high','status':'OPEN','source':'reader_once.py:165-182','title':'Interrupted held-directory cleanup leaks remaining descriptors',
 'evidence':'Both modes: real close followed by KeyboardInterrupt on first descriptor attempts 1 of 3 closes; 2 remain open. Reviewer closes the remaining descriptors after the probe.',
 'required_correction':'Attempt every owned descriptor close once under BaseException handling; preserve the work primary and all cleanup failures without unsafe retry of an ambiguously closed descriptor. Add interruption and active-primary regressions.'},
 {'id':'RE3-R02','severity':'high','status':'OPEN','source':'reader_once.py:321-344','title':'Cleanup can unlink a replacement root member before detecting root substitution',
 'evidence':'Both modes: after the initial owned-root identity check, rename the owned synthetic root and create a replacement at the same name. The first held_directory open follows the replacement; its matching victim file is deleted. The final root check refuses only afterward. The original tree is retained.',
 'required_correction':'Anchor destructive traversal to held original root/child identities and validate named attachment before each destructive action. Do not freshly resolve a replacement namespace and treat it as owned. Refuse substitution without deleting any replacement member; retain original residue.'}
 ],
 'supported_checks':[
 'Exact 986-name selection, source descriptor hashing and destination readback; no-replace directories/files; symlink ancestors and changed member bytes refused in synthetic fixtures.',
 'run rebinds ROOT before second selected() and passes snapshot into the sealed import/cold-open path. An independent stubbed endpoint probe consumes original snapshot bytes while host source bytes change, then restores ROOT and removes the snapshot.',
 'Synthetic loader probes execute verified raw code and reject namespace/origin substitutions; no selected original Reader or protected source role executed.',
 'Report and receipt bounds and period checks exist at selected cold/report/receipt boundaries; archive data is not included in aggregate receipt.'
 ],
 'limitations':[
 'All tests use owned synthetic public fixtures. Actual archive body, private stage, original Reader cold-open, Docker and protected Source8 access NOT_RUN. Audit hook rejects archive-named opens and process launches.',
 'Different st_dev proves distinct device, not tmpfs filesystem type or installed mount custody/capacity. Actual selected Docker mount qualification remains untested.',
 'The 400 MiB aggregate check occurs after each complete member copy; this is an acceptance bound, not a proven peak-write reserve. A member can be allowed up to 512 MiB. No large allocation probe was run.',
 'The independent run-rewiring positive stubs only _run_sealed; it does not establish actual original Reader import/data behavior.',
 'Last cold-path period check precedes code/snapshot cleanup. External terminal currentness and post-close verification remain required. A persisted receipt alone cannot establish process success or cleanup.',
 'No whole product, full chain, actual host G01/G02 or protected qualification is granted.'
 ],
 'next_unit':'Disjoint successor correcting RE3-R01 and RE3-R02 with synthetic causal negatives; preserve this frozen candidate and review before any effect.'
}
(E/'review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(binding(E/'review.json'),sort_keys=True))
