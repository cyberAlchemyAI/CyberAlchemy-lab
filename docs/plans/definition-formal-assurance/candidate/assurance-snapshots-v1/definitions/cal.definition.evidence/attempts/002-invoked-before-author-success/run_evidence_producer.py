from pathlib import Path
import subprocess,sys,json
u=Path.cwd()/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.evidence';stem=sys.argv[1];argv=[sys.executable,('/tmp/evidence_author.py' if stem=='author' else str(u/('build_candidate.py' if stem=='build' else 'verify_candidate.py' if stem=='model' else 'verify_source_checks.py')))]+(['--write'] if stem in ['model','source'] else [])
r=subprocess.run(argv,capture_output=True);dest=u if u.exists() else Path('/tmp')
for suffix,data in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (dest/(stem+'-'+suffix+'.txt')).open('xb') as f:f.write(data)
with (dest/(stem+'-command-result.json')).open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'},f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);print(json.dumps({'producer':stem,'exit_code':r.returncode}));raise SystemExit(r.returncode)
