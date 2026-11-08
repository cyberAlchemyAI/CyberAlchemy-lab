"""Closed owned transport, phase contract and failure CLI checks."""
from pathlib import Path
import copy
import json
import subprocess
import sys
from jsonschema import Draft202012Validator
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p07.api import OwnedQualifier
from v3.p07.runs import validate,inspect_record
sys.path.insert(0,str(BASE/'execution'));import support as s
controls=[]
def control(name,ok):s.require(ok,name);controls.append({'name':name,'result':'pass'})
def rejected(name,call):
    try:call()
    except Exception:control(name,True);return
    raise ValueError(name+' was accepted')
v=Draft202012Validator(s.read(HERE/'result.schema.json'))
report=s.read(HERE/'repeatability-controls.json')
for ref in report['runs']:v.validate(s.read(s.check(ref)))
control('all-final-owned-envelopes-match-distinct-closed-contract',all(s.read(s.check(ref))['schema']=='relational.owned-qualification/v3' for ref in report['runs']))
a=s.read(HERE/'first-result.json');record=s.read(s.check(a['owned_run']))
for name,change in [('no-owned-application-escalation',lambda q:q.update(application_authorized=True)),
                    ('no-owned-qualified-null-result',lambda q:q.update(qualified_result=None)),
                    ('no-supervisor-tag-on-owned-envelope',lambda q:q.update(schema='relational.supervised-qualification/v3')),
                    ('no-unbound-owned-envelope-field',lambda q:q.update(extra=True))]:
    q=copy.deepcopy(a);change(q);control(name,not v.is_valid(q))
bad=copy.deepcopy(record);bad['result']=None
rejected('completed-run-must-bind-exact-issued-result',lambda:validate('run-record',bad))
phase=s.read(s.check(record['phases'][0]));phase['fresh_qualification']=True
rejected('phase-record-cannot-authorize-fresh-qualification',lambda:validate('phase',phase))
policy=s.read(BASE/'p01/request-fixture.json')['resource_policy']
api=OwnedQualifier(HERE/'contract-runs',policy)
rejected('oversized-resume-selector-refused-before-dispatch',lambda:api.resume({'path':'a'*2049,'sha256':'0'*64},b'{}'))
s.write(HERE/'cli-policy.json',policy);s.write(HERE/'cli-invalid-input.json',{'unexpected':'field'})
r=subprocess.run([sys.executable,str(HERE/'cli.py'),'--policy',str(HERE/'cli-policy.json'),'--request',str(HERE/'cli-invalid-input.json')],capture_output=True,text=True,timeout=10)
answer=json.loads(r.stdout);v.validate(answer);s.write(HERE/'cli-invalid-result.json',answer)
control('owned-cli-uses-fixed-worker-and-finalizes-invalid-run',r.returncode==2 and answer['status']=='invalid' and inspect_record(answer['owned_run'])['phase']=='invalid')
control('owned-cli-does-not-issue-qualification-or-application',answer['qualified_result'] is None and not answer['claims'] and not answer['application_authorized'])
cold=s.read(BASE/'p03/cold-api-result.json');cold_payload=s.read(s.check(cold['payload']))
cold_refs=[cold['payload'],cold['manifest']['projection'],cold['manifest']['general'],cold['manifest']['dependencies']]
for module in cold['manifest']['witness']['modules']:cold_refs += [module['source'],module['olean']]
deps=s.read(s.check(cold['manifest']['dependencies']))
for module in deps['modules']:cold_refs += [module['source'],module['olean']]
for ref in cold_refs:s.check(ref)
control('warm-owned-runs-preserve-accepted-cold-proof-files',cold['status']=='qualified-candidate' and len(cold_refs)>70)
s.write(HERE/'cold-evidence-preservation.json',{'result':'pass','original_accepted_cold_result':s.binding(BASE/'p03/cold-api-result.json'),'checked_original_cold_bindings':cold_refs,'new_cold_qualification_claimed':False,'authority_effect':'none'})
s.write(HERE/'contract-controls.json',{'result':'pass','controls':controls,'authority_effect':'none'})
print('P07 contract controls passed: '+str(len(controls)))
