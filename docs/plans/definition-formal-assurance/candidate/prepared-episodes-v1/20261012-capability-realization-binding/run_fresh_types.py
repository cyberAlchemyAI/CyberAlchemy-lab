from pathlib import Path
import json,subprocess,sys
root=Path.cwd();p=Path(__file__).resolve().parent;u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-realization-binding';impl=root/'craft/formalization/candidates/definition-assurance-v1';rows=[]
for name,script,args in [('contract',impl/'contracts.py',['validate','--kind','interpretation','--input',str(u/'t.json')]),('model',u/'verify_candidate.py',[]),('source',u/'verify_source_checks.py',[])]:
 argv=[sys.executable,'-B',str(script)]+args;r=subprocess.run(argv,cwd=root,capture_output=True);stem='fresh-types-'+name;row={'check':name,'argv':argv,'exit_code':r.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'}
 for folder in [p,u]:
  for suffix,data in [('stdout.txt',r.stdout),('stderr.txt',r.stderr),('command-result.json',(json.dumps(row,indent=2)+'\n').encode())]:
   with (folder/(stem+'-'+suffix)).open('xb') as f:f.write(data)
 print(json.dumps({'check':name,'actual_exit_code':r.returncode}),flush=True)
 if r.returncode or r.stderr:raise SystemExit(r.returncode or 1)
 if name!='contract':assert r.stdout==(u/(name+'-stdout.txt')).read_bytes()
 rows.append(row)
for folder in [p,u]:
 with (folder/'fresh-types-logic-results.json').open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
