"""Retain exact failed consumer comparison; distinguish list binding from scalar identity."""
from pathlib import Path
import json,hashlib,shutil,ast
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.withdrawal-record');a=u/'consumer-attempts/001-resolution-list-scalar-comparison';a.mkdir(parents=True);refs=[]
for n in ['inspect_carrier_consumers.py','carrier-inspection-command-result.json','carrier-inspection-stdout.txt','carrier-inspection-stderr.txt']:
 shutil.copyfile(u/n,a/n);refs.append({'path':str(a/n),'sha256':hashlib.sha256((a/n).read_bytes()).hexdigest()})
with (a/'attempt.json').open('x') as f:json.dump({'status':'retained-actual-consumer-comparison-failure','exit_code':json.loads((a/'carrier-inspection-command-result.json').read_text())['exit_code'],'reason':'Consumer reference list was chained to scalar resolution ID; correct as list equality plus separate scalar equality','files':refs,'frozen_typed_inputs_changed':False,'candidate_or_canonical_sources_changed':False,'report_created_in_failed_attempt':False},f,indent=2);f.write('\n')
for q in [u/'inspect_carrier_consumers.py',p/'prepare_consumers.py']:
 s=q.read_text().replace("dr['primary_consumer_refs']==[resolution['resolution_id']]=='CAL-DEFINITION-SPECIALIZATION-RESOLUTION-0014'","dr['primary_consumer_refs']==[resolution['resolution_id']] and resolution['resolution_id']=='CAL-DEFINITION-SPECIALIZATION-RESOLUTION-0014'").replace('import ast,copy,json,hashlib','import ast,copy,json,hashlib\nfrom jsonschema.exceptions import ValidationError').replace('except (ValueError,b.c.ValidationError)','except (ValueError,ValidationError)');ast.parse(s);q.write_text(s)
for n in ['carrier-inspection-command-result.json','carrier-inspection-stdout.txt','carrier-inspection-stderr.txt']:(u/n).unlink()
print('Retained failed binding comparison; exact list/scalar checks and read-only schema exception handling corrected.')
