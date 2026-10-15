from pathlib import Path
import subprocess,sys,json
p=Path(__file__).resolve().parent;root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/CAV2-D20'
def run(stem):
 script=p/'prepared/author_candidate.py' if stem=='author' else u/({'build':'build_candidate.py','model':'verify_candidate.py','source':'verify_source_checks.py'}[stem]);argv=[sys.executable,'-B',str(script)]+([] if stem in ['author','build'] else ['--write']);r=subprocess.run(argv,cwd=root,capture_output=True);target=p if stem=='author' else u
 for k,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
  with (target/(stem+'-'+k+'.txt')).open('xb') as f:f.write(raw)
 with (target/(stem+'-command-result.json')).open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'},f,indent=2);f.write('\n')
 if stem=='author' and r.returncode==0:
  for suffix in ['stdout.txt','stderr.txt','command-result.json']:
   with (u/('author-'+suffix)).open('xb') as f:f.write((p/('author-'+suffix)).read_bytes())
 print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);print(json.dumps({'producer':stem,'exit_code':r.returncode}));return r.returncode
raise SystemExit(run(sys.argv[1]))
