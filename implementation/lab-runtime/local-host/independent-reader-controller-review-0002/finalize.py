import pathlib,json,hashlib
R=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab');L=R/'implementation/lab-runtime/local-host';C=L/'reader-only-docker-controller-0002';O=L/'independent-reader-controller-review-0002'
def b(p):
 if p.name=='branch.snapshot':raise RuntimeError('archive body prohibited')
 raw=p.read_bytes();return {'path':str(p),'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
rows={}
for d in (C,L/'reader-only-docker-controller-0001',L/'fresh-reader-docker-0004'):
 freeze=d/'freeze.json';rows[str(freeze)]=b(freeze)
 for row in json.loads(freeze.read_bytes())['file_bindings']:
  p=R/row['path'] if row['path'].startswith('implementation/') else d/row['path'];actual=b(p);assert actual['sha256']==row['sha256'] and actual['size']==row['size'];rows[str(p)]=actual
for p in (L/'READER-ONLY-DOCKER-CONTROLLER-INDEPENDENT-STATIC-REVIEW-0001.md',):rows[str(p)]=b(p)
for name in ('normal-0002.log','optimized-0002.log'):
 t=json.loads((O/name).read_text().splitlines()[-1]);assert t['passed'] and t['tests']==24 and t['post_verified'];assert t['observations'][0]['stdout_closed']==False and t['observations'][1]['remaining']==2
(O/'bindings.json').write_text(json.dumps({'bindings':list(rows.values()),'count':len(rows),'future_reader_attempt_absent':not pathlib.Path('/tmp/cal-reader-only-dev-20261020-0001-exact1').exists(),'archive_body_opened':False},sort_keys=True,indent=2)+'\n')
review={'schema_version':'independent-reader-controller-static-review/v2','verdict':'HOLD_CLEANUP_AND_MOUNT_CUSTODY','effect':'NOT_RUN','freeze':b(C/'freeze.json'),'tests':{'corrected_normal':24,'corrected_optimized':24,'corrected_os_exit_each':0,'independent_cleanup_observations_per_mode':2,'allowed_local_python_helpers_per_mode':3,'docker_invocations':0},'prior_run_accounting':'Original normal/optimized runs each had3 errors because reviewer audit hook permitted selected Python Popen but denied its posix_spawn implementation. All original driver/logs retained. Revised driver whitelists the same three exact Python snippets for both events; final24/24 pass both modes. This was reviewer harness failure, not candidate failure.', 'verified':[
'Five current freeze members unchanged before/after runs; selected Reader0004 literal freeze and predecessor controller freeze member hashes verified.',
'Prior R01 evidence/log corrections hold under source review and tests: held nofollow ancestor chains, no-replace relative writes with parent fsync, log reopening by exact selected precreated inode, leaf symlink and replacement refusal.',
'Prior R02 timing fixes pass fake-daemon late-stop at terminal entry, signal during terminal file fsync, and expiry at terminal publication. Terminal same-leaf rewrite downgrades UNKNOWN. Defined decision point is final post-fsync check while SIGINT/TERM blocked; later signals are not retroactive.',
'Prior R03 bounded reads use regular held FDs, limit before read and limit+1/size checks. Receipt cap1MiB, log cap4MiB, every Docker CLI stream cap1MiB. Exact allowed local Python children exercise caps and pipe teardown without Docker.',
'Fake lifecycle retains marker/no retry, exact CID/name/image/nonce before cleanup, daemon wait/inspect and durable pre-removal evidence before rm, double absence observation, forced cleanup never PASS and cleanup-only recovery. Lost-create fake is failure response without simulating daemon-side successful create; do not overstate that test.',
'Controller run/recovery remain disabled. Selected Reader0004 tool also remains disabled; no newly released entrypoint or different stage silently substituted.'
], 'findings':[
{'id':'RDC2-R04','source':'controller.py cli finally, lines350-359 approximately','kind':'causal synthetic owned-client cleanup failure','observation':'Fake Popen child, selector setup ValueError primary, then terminate raises OSError. cli raises OSError instead of primary, calls only terminate, leaves stdout and stderr open, and never reaches kill/wait. Reviewer closes both fake streams; no real child/PID involved in this probe.','required':'Independent guarded cleanup for client termination/reap, selector and both pipes; attempt all despite BaseException, retain exact primary plus cleanup errors, and keep unresolved real client state UNKNOWN. Add terminate/kill/wait/selector/pipe failure regressions without signaling foreign processes.'},
{'id':'RDC2-R05','source':'controller.py held_directory finally lines93-95 approximately','kind':'causal synthetic descriptor cleanup failure','observation':'First real close succeeds then raises OSError; one of three closes attempted and two owned directory FDs remain open. Reviewer closes remaining descriptors once after patch removal.','required':'Attempt every held descriptor close exactly once, preserve active primary and complete secondary provenance, delay interruption until all owned closes attempted; never infer successful cleanup on ambiguity. Include nested ExitStack/post-terminal failure accounting.'}
], 'remaining_effect_obligations':[
'Docker still resolves bind-source pathname strings. Held pre/post checks do not exclude same-UID change-and-restore during daemon mount resolution. Preserve explicit mount-source handoff HOLD and causal race qualification requirement.',
'Private986file stage/current archive hash, actual mount/UID/image feasibility, released Reader tool with exact closure and same-state period selection not established. No private archive body was accessed.',
'Final durable terminal alone cannot prove a later controller/held-FD close succeeded; future external effect review must bind actual process exit and postclose outcome. No physical crash or real-daemon fault qualification from mocks.',
'Error strings/class names and raw process captures remain private evidence; this review does not qualify public diagnostic sanitization.',
'No real Docker create/start/stop/kill/rm, no Reader cold-open, Source/private copy, Mapper/Context, protectedSource8, G01/G02 or original task acceptance.'
], 'evidence':[b(O/n) for n in ('checks.py','normal.log','optimized.log','checks-0002.py','normal-0002.log','optimized-0002.log','bindings.json')],'candidate_modified':False}
(O/'review.json').write_text(json.dumps(review,indent=2,sort_keys=True)+'\n');print(json.dumps(b(O/'review.json')))
