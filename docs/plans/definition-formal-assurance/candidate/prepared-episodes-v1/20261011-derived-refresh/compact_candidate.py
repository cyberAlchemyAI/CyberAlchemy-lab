"""Retain byte-limit failure and compact unchanged parsed interpretation values."""
from pathlib import Path
import json,hashlib,shutil
root=Path.cwd();p=Path(__file__).resolve().parent;u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.derived-refresh';a=u/'retained-attempts/attempt-002-contract-byte-limit';a.mkdir(parents=True)
for q in list(u.glob('fresh-types-*'))+[u/'model-controls.json']+[u/('model-'+s) for s in ['command-result.json','stdout.txt','stderr.txt']]:q.rename(a/q.name)
for q in p.glob('typed-stage-freeze-*'):q.rename(a/q.name)
shutil.copyfile(u/'t.json',a/'t-before-compaction.json');shutil.copyfile(u/'close_types_logic_stage.py',a/'close_types_logic_stage-before-recovery.py');shutil.copyfile(u/'REVIEW.md',a/'REVIEW-before-recovery.md')
raw=(u/'t.json').read_bytes();value=json.loads(raw);packed=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode();assert json.loads(packed)==value and len(raw)>1000000 and len(packed)<1000000
(u/'t.json').write_bytes(packed)
refs=[{'path':q.relative_to(root).as_posix(),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()} for q in sorted(a.rglob('*')) if q.is_file()]
report={'attempt':'002','actual_failed_check':'fresh-contract','actual_exit_code':2,'actual_error':'byte-limit','actual_failed_freeze_exit_code':1,'original_bytes':len(raw),'compact_bytes':len(packed),'parsed_JSON_values_preserved':True,'before_sha256':hashlib.sha256(raw).hexdigest(),'after_sha256':hashlib.sha256(packed).hexdigest(),'unchanged_MAX_BYTES':1000000,'retained_files':refs,'authority_effect':'none','semantic_ready':False}
with (a/'attempt.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
with (u/'serialization-recovery.json').open('x') as f:json.dump({**report,'attempt_ref':{'path':(a/'attempt.json').relative_to(root).as_posix(),'sha256':hashlib.sha256((a/'attempt.json').read_bytes()).hexdigest()},'packer_ref':{'path':Path(__file__).relative_to(root).as_posix(),'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}},f,indent=2);f.write('\n')
print(json.dumps({k:report[k] for k in ['actual_exit_code','actual_failed_freeze_exit_code','original_bytes','compact_bytes','parsed_JSON_values_preserved']},indent=2))
