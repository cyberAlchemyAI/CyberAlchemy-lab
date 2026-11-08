from pathlib import Path
import subprocess,sys,json
root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.finding';prep=u.parent/'cal.definition.evidence-set/next-unit-preparation'
def run(stem,script,arguments):
 argv=[sys.executable,str(script),*arguments];p=subprocess.run(argv,cwd=root,capture_output=True)
 log=u if u.exists() else Path('/tmp')
 prefix=stem if log==u else 'finding-'+stem
 for suffix,data in [('stdout',p.stdout),('stderr',p.stderr)]:
  with (log/(prefix+'-'+suffix+'.txt')).open('xb') as out:out.write(data)
 record={'argv':argv,'exit_code':p.returncode,'stdout':prefix+'-stdout.txt','stderr':prefix+'-stderr.txt'}
 with (log/(prefix+'-command-result.json')).open('x') as out:json.dump(record,out,indent=2);out.write('\n')
 print(json.dumps({'producer':stem,'exit_code':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()}),flush=True)
 if p.returncode:raise SystemExit(p.returncode)
run('author',prep/'author_candidate.py',[])
run('build',u/'build_candidate.py',[])
run('model',u/'verify_candidate.py',['--write'])
run('source',u/'verify_source_checks.py',['--write'])
