from pathlib import Path
import json,subprocess,sys
root=Path.cwd();unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.implementation';implementation=root/'craft/formalization/candidates/definition-assurance-v1';rows=[]
commands=[('contract',[sys.executable,'-B',str(implementation/'contracts.py'),'validate','--kind','interpretation','--input',str(unit/'t.json')]),('model',[sys.executable,'-B',str(unit/'verify_candidate.py')]),('source',[sys.executable,'-B',str(unit/'verify_source_checks.py')])]
for name,argv in commands:
 result=subprocess.run(argv,cwd=root,capture_output=True);stem='fresh-types-'+name
 row={'check':name,'argv':argv,'exit_code':result.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'}
 for key,data in [('stdout',result.stdout),('stderr',result.stderr)]:
  with (unit/row[key]).open('xb') as f:f.write(data)
 with (unit/(stem+'-command-result.json')).open('x') as f:json.dump(row,f,indent=2);f.write('\n')
 print(name,result.returncode,flush=True)
 if result.returncode or result.stderr:print(result.stderr.decode(),file=sys.stderr);raise SystemExit(result.returncode or 1)
 if name!='contract':assert result.stdout==(unit/(name+'-stdout.txt')).read_bytes()
 rows.append(row)
with (unit/'fresh-types-logic-results.json').open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
print('PASS-three-fresh-types-logic-checks',flush=True)
