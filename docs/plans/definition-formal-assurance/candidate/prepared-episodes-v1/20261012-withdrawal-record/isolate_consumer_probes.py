"""Retain the actual parallel scratch-file collision and prior successful observations."""
from pathlib import Path
import json,hashlib,shutil,ast
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.withdrawal-record');a=u/'consumer-attempts/002-parallel-shared-scratch-file';a.mkdir(parents=True);refs=[]
names=['inspect_carrier_consumers.py','carrier-consumer-inspection.json','carrier-inspection-command-result.json','carrier-inspection-stdout.txt','carrier-inspection-stderr.txt','authority-profile-checks.json','profile-command-result.json','profile-stdout.txt','profile-stderr.txt','fresh-first-four-results.json','fresh-profile-stdout.txt','fresh-profile-stderr.txt','fresh-carrier-inspection-command-result.json','fresh-carrier-inspection-stdout.txt','fresh-carrier-inspection-stderr.txt']
for n in names:
 shutil.copyfile(u/n,a/n);refs.append({'path':str(a/n),'sha256':hashlib.sha256((a/n).read_bytes()).hexdigest()})
with (a/'attempt.json').open('x') as f:json.dump({'status':'retained-actual-fresh-consumer-scratch-collision','exit_code':json.loads((a/'fresh-carrier-inspection-command-result.json').read_text())['exit_code'],'reason':'Two read-only consumer evaluations used the same hypothetical-input filename concurrently','files':refs,'frozen_typed_inputs_changed':False,'candidate_or_canonical_sources_changed':False,'prior_original_consumer_and_profile_exit_codes':[0,0],'correction':'Per-evaluation temporary directory plus normalized hypothetical allocation reference digest'},f,indent=2);f.write('\n')
q=u/'inspect_carrier_consumers.py';s=q.read_text().replace('from pathlib import Path','from pathlib import Path\nfrom tempfile import TemporaryDirectory')
s=s.replace("record_path=paths['candidate_fixture'];data=copy.deepcopy(allocation);temporary=b.UNIT/'hypothetical-withdrawal-record.json'","record_path=paths['candidate_fixture'];data=copy.deepcopy(allocation);scratch=TemporaryDirectory(prefix='hyp-withdrawal-',dir=b.UNIT) if record is not None else None;temporary=Path(scratch.name)/'record.json' if scratch is not None else None")
s=s.replace("'allocation_digest':b.ir.digest(data)","'allocation_digest':b.ir.digest({**data,'withdrawal_record':{'path':'hyp:controlled-record-input','sha256':data['withdrawal_record']['sha256']}} if record is not None else data)")
s=s.replace("if record is not None:temporary.unlink()","if scratch is not None:scratch.cleanup()")
ast.parse(s);q.write_text(s)
# Preserve valid contract/model/source fresh results; repeat only the affected profile.
rows=json.loads((u/'fresh-first-four-results.json').read_text());assert [x['check'] for x in rows]==['contract','model','source','profile']
with (u/'fresh-first-three-results.json').open('x') as f:json.dump(rows[:3],f,indent=2);f.write('\n')
for n in ['carrier-consumer-inspection.json','carrier-inspection-command-result.json','carrier-inspection-stdout.txt','carrier-inspection-stderr.txt','authority-profile-checks.json','profile-command-result.json','profile-stdout.txt','profile-stderr.txt','fresh-first-four-results.json','fresh-profile-stdout.txt','fresh-profile-stderr.txt','fresh-carrier-inspection-command-result.json','fresh-carrier-inspection-stdout.txt','fresh-carrier-inspection-stderr.txt']:(u/n).unlink()
assert not (u/'hypothetical-withdrawal-record.json').exists()
print('Retained failed concurrency observation and prior success;isolated temporary files;only affected consumer/profile observations need re-evaluation.')
