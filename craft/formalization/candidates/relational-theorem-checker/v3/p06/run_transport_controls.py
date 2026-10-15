"""Closed supervisor transport and raw CLI controls, without new proof claims."""
from pathlib import Path
import copy
import json
import subprocess
import sys
import threading
from jsonschema import Draft202012Validator
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p06.api import SupervisedQualifier
sys.path.insert(0,str(BASE/'execution'));import support as s
controls=[];bindings=[]
def control(name,ok):s.require(ok,name);controls.append({'name':name,'result':'pass'})
schema=s.read(HERE/'supervised-result.schema.json');Draft202012Validator.check_schema(schema);validator=Draft202012Validator(schema)
report=s.read(HERE/'bridge-controls.json')
for ref in report['runs']:
    path=s.check(ref);value=s.read(path)
    if value['schema']=='relational.supervised-qualification/v3':validator.validate(value);bindings.append(ref)
control('all-actual-supervisor-envelopes-match-closed-schema',len(bindings)==9)
qualified=s.read(HERE/'supervised-rich-result.json')
for name,edit in [('no-application-escalation',lambda a:a.update(application_authorized=True)),
                  ('no-qualified-null-result',lambda a:a.update(qualified_result=None)),
                  ('no-incomplete-supervisor-qualification',lambda a:a['supervised_run'].update(complete=False)),
                  ('no-unknown-envelope-field',lambda a:a.update(unbound_field=True))]:
    changed=copy.deepcopy(qualified);edit(changed)
    control(name,not validator.is_valid(changed))
request=s.read(BASE/'p01/request-fixture.json');policy=request['resource_policy']
s.write(HERE/'cli-policy.json',policy);s.write(HERE/'cli-invalid-input.json',{'unexpected':'field'})
run=subprocess.run([sys.executable,str(HERE/'cli.py'),'--policy',str(HERE/'cli-policy.json'),'--request',str(HERE/'cli-invalid-input.json')],capture_output=True,text=True,timeout=10)
answer=json.loads(run.stdout);validator.validate(answer);s.write(HERE/'cli-invalid-result.json',answer)
control('raw-cli-uses-supervised-fixed-worker',run.returncode==2 and answer['status']=='invalid' and 'job' in answer['supervised_run'] and answer['qualified_result'] is None)
cancel=threading.Event();cancel.set()
answer=SupervisedQualifier(HERE/'pre-cancel-runs',policy).qualify(json.dumps(request).encode(),cancel=cancel)
validator.validate(answer);s.write(HERE/'pre-cancel-result.json',answer)
control('cancel-before-launch-does-not-create-worker',answer['status']=='cancelled' and 'job' not in answer['supervised_run'])
control('policy-schema-is-exact-accepted-copy',s.digest(HERE/'resource-policy.schema.json')==s.digest(BASE/'p01/contracts/resource-policy.schema.json'))
s.write(HERE/'transport-controls.json',{'result':'pass','controls':controls,'actual_envelopes':bindings,'authority_effect':'none'})
print('P06 transport controls passed: '+str(len(controls)))
