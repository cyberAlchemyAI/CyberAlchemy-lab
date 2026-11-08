import pathlib,json,hashlib,stat
R=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab');L=R/'implementation/lab-runtime/local-host';C=L/'fresh-reader-docker-0007';O=L/'independent-fresh-reader-docker-review-0007'
def binding(p):
 if p.name=='branch.snapshot':raise RuntimeError('archive body prohibited')
 b=p.read_bytes();return {'path':str(p),'size':len(b),'sha256':hashlib.sha256(b).hexdigest()}
f=binding(C/'freeze.json');assert f['sha256']=='3391cd37a4457472534768b9483cab97dbfb375536687684ca44d88d8724f41f';rows={f['path']:f}
for r in json.loads((C/'freeze.json').read_bytes())['file_bindings']:
 b=binding(R/r['path']);assert b['sha256']==r['sha256'] and b['size']==r['size'];rows[b['path']]=b
prior=json.loads((L/'independent-fresh-reader-docker-review-0005/bindings.json').read_bytes())
for r in prior['bindings']:
 b=binding(pathlib.Path(r['path']));assert b==r;rows[b['path']]=b
for name in ('freeze.json',):
 p=L/'fresh-reader-docker-0005'/name;rows[str(p)]=binding(p)
for r in json.loads((L/'fresh-reader-docker-0005/freeze.json').read_bytes())['file_bindings']:
 b=binding(R/r['path']);assert b['sha256']==r['sha256'] and b['size']==r['size'];rows[b['path']]=b
old=prior['archive_metadata_only'];s=pathlib.Path(old['path']).lstat();archive={'path':old['path'],'size':s.st_size,'device':s.st_dev,'inode':s.st_ino,'mode':oct(stat.S_IMODE(s.st_mode)),'nlink':s.st_nlink,'current_bytes_verified':False};assert archive==old
addendum=binding(L/'FRESH-READER-DOCKER-0006-SUPERSESSION-ADDENDUM-0001.md');rows[addendum['path']]=addendum
oldfreeze=L/'fresh-reader-docker-0006/freeze.json';rows[str(oldfreeze)]=b(oldfreeze)
assert rows[str(oldfreeze)]['sha256']=='cf057d87c684e2deb781a6206bd752ea62204296443fd05d6816c7b07a734b36'
for r in json.loads(oldfreeze.read_bytes())['file_bindings']:
 x=b(R/r['path']);assert x['sha256']==r['sha256'] and x['size']==r['size'];rows[x['path']]=x
for name in ('normal.log','optimized.log'):
 t=json.loads((O/name).read_text().splitlines()[-1]);assert t['passed'] and t['tests']==34 and t['post_verified']
 o=t['observations'];assert o[0]['refused'] and o[0]['unknown_present'] and not o[0]['reader_input_released'];assert o[2]['refused'] and o[2]['unknown_absent'] and o[2]['external_exit_required'] and not o[2]['reader_input_released']
manifest={'bindings':list(rows.values()),'count':len(rows),'archive_metadata_only':archive,'real_attempt_absent':not pathlib.Path('/tmp/cal-reader-stage-20261020-0001-0007').exists()};assert manifest['real_attempt_absent'];(O/'bindings.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
review={'schema_version':'independent-fresh-reader-static-review/v7-stage-only','verdict':'PASS_BOUNDED_NEUTRAL_STAGE_OBSERVATION','effect_release':'HOLD_DISABLED_REQUIRES_SEPARATE_RELEASE','effect':'NOT_RUN','freeze':f,'design':b(L/'FRESH-READER-DOCKER-DESIGN-0008.md'),'tests':{'normal':34,'optimized':34,'os_exit_each':0,'independent_synthetic_probes_per_mode':3},'findings':[], 'verified':[
'FR6-R01 closed for narrowed observation semantics: exact-expiry during terminal persistence causes refusal and UNKNOWN after the neutral OBSERVED_STAGE_ONLY receipt. No standalone durable PASS and reader_input_released=false.',
'Independent post-neutral-receipt role mutation is refused by second descriptor-based exact stage verifier. With UNKNOWN-write failure injected too, original failure still propagates, marker and neutral receipt remain, no Reader input release, and exact error note retains secondary receipt failure. External zero exit remains mandatory; absence of UNKNOWN alone cannot establish success.',
'Independent current synthetic archive digest mismatch consumes attempt and yields UNKNOWN with no neutral terminal; original synthetic bytes unchanged.',
'Author34-case suite each mode covers first-inventory mutation, receipt-time expiry, marker-before-copy, marker fault, partial retention/no retry, exact plan/attempt/mode/expiry, copy cleanup and primary provenance, destination readback, parent fsync and nofollow swaps.',
'27 current frozen members verified before/after. Corrected0006 predecessor remains byte-identical to cf057d87; original0001-0005 selected inputs and Source non-archive bindings unchanged.',
'986-row plan remains exact Source978 plus Reader8; literal source/package/Reader/selection joins preserved. Actual archive current bytes remain explicitly unchecked by preflight. Full selected attempt stays absent and effect gate remains false.'
], 'observation_semantics':'OBSERVED_STAGE_ONLY is a neutral historical receipt of ordered checks, not authorization or a durable current-stage PASS. Successful external OS exit and final post-persistence checks are needed to conclude observed completion. A later Reader must freshly revalidate byte/identity/mode inventory and period and establish its own custody. No atomic same-UID immutable-tree promise.',
'limitations':[
'No actual private archive-body read, hash or copy; attachment metadata only unchanged. Synthetic archive-named files contain reviewer/author disposable bytes only. No generated Reader/Source import or Docker activity.',
'Currentness decision is final period observation, not a guarantee that wall-clock remains current during later scheduling/return or Reader use. Expiry later blocks that use independently.',
'No physical crash/power-loss or actual full986file stage test. UNKNOWN receipt is best-effort; occupied attempt/nonzero outcome still forbids retry even when receipt fails.',
'Per-file held directory verification prevents symlink substitution during selected read but does not establish concurrent whole-tree snapshot or immutable retained pathnames. This ceiling is now explicit.',
'Logs/exceptions and copied package remain private; no public diagnostic sanitization reviewed. statvfs is not capacity reservation.',
'No Reader effect, Mapper/Context, protectedSource8, host/cgroup/G01/G02 qualification, human outcome or original-task acceptance; separate release and exact predispatch still required.'
], 'preservation':{'selected_bindings':len(rows),'real_attempt_absent':True,'archive_body_opened':False,'candidate_modified':False},'evidence':[b(O/n) for n in ('checks.py','normal.log','optimized.log','bindings.json')]}
(O/'review.json').write_text(json.dumps(review,indent=2,sort_keys=True)+'\n');print(json.dumps(b(O/'review.json')))
