"""Read-only exact API10 closure review; findings contain selectors, never values."""
import collections,datetime,hashlib,importlib.util,json,stat
from pathlib import Path
ROOT=Path.cwd(); RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'; D=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v10'
spec=importlib.util.spec_from_file_location('_R06_original_scanner',ROOT/'product/lab/release-candidates/v1/boundary-review/0002/review.py'); R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
def sha(b):return hashlib.sha256(b).hexdigest()
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}
controls={n:json.loads((D/n).read_bytes()) for n in ('source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json')}; bindings={n:binding(D/n) for n in controls}; sets={n:{x['path'] for x in o['files']} for n,o in controls.items()}; rows=[]; diffs=[]; total=0
for index,row in enumerate(controls['source-manifest.json']['files']):
 p=ROOT/row['path'];raw=R.read(p);total+=len(raw);digest=sha(raw)
 if digest!=row['sha256']:diffs.append({'path':row['path'],'expected_sha256':row['sha256'],'observed_sha256':digest})
 findings=[];reason=None
 try:findings=R.scan(raw,row['path'])
 except (ValueError,UnicodeError,RecursionError) as error:reason=type(error).__name__ # No value-bearing exception message.
 risky_path=p.suffix.lower() in {'.pem','.key','.pfx','.p12','.sqlite','.sqlite3','.db','.pyc'} or any(v in {'__pycache__','.env','secrets','credentials'} for v in p.parts)
 if findings or reason or risky_path:
  rows.append({'path':row['path'],'sha256':digest,'size_bytes':len(raw),'mode':oct(stat.S_IMODE(p.stat().st_mode)),'profile_member':row['path'] in sets['contract-profile.json'],'schema_runtime_member':row['path'] in sets['SCHEMA-EXECUTION-DEPENDENCIES.json'],'findings':findings,'inspection_refusal_class':reason,'risky_path':risky_path,'public_body_export_allowed':False})
 if index%3000==0:print(json.dumps({'scanned':index,'flagged':len(rows)}),flush=True)
assert all(binding(D/n)==bindings[n] for n in controls),'API10 controls changed during inspection'
known=json.loads((ROOT/'product/lab/release-candidates/v1/boundary-review/0003/inventory.json').read_bytes());knownrows=[x for x in known['rows'] if x['disposition']!='unselected-final-release-source' and x['path'] in sets['source-manifest.json']]
report={'schema_version':'lab-installation-release-R06-api10-read-only-audit/v1-candidate','checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selected_control_bindings':bindings,'counts':{n:len(o['files']) for n,o in controls.items()},'source_bytes_read':total,'fresh_source_hash_mismatches':diffs,'rows':rows,'flagged_source_items':len(rows),'flagged_profile_items':sum(x['profile_member'] for x in rows),'flagged_schema_runtime_items':sum(x['schema_runtime_member'] for x in rows),'finding_reason_counts':dict(collections.Counter(f['reason'] for x in rows for f in x['findings'])),'inspection_refusals':sum(x['inspection_refusal_class'] is not None for x in rows),'prior_context_flagged_rows_retained':len(knownrows),'prior_context_inventory_binding':binding(ROOT/'product/lab/release-candidates/v1/boundary-review/0003/inventory.json'),'claim_ceiling':'Original bounded heuristic JSON/embedded-byte/PEM scanner plus fresh exact API10 source hashes. No secret values disclosed. Not a comprehensive secret detector, privacy disposition, final source-family selection, qualification, public export or R06 closure.','private_values_disclosed':False,'originals_changed':False,'R06_complete':False,'actual_owner_outcome':None,'authority_effect':'none'}
out=RUN/'installation-release-R06-api10-audit-0148.json'
with out.open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'report_binding':binding(out),'flagged_source_items':len(rows),'flagged_profile_items':report['flagged_profile_items'],'flagged_schema_runtime_items':report['flagged_schema_runtime_items'],'inspection_refusals':report['inspection_refusals'],'fresh_source_hash_mismatches':len(diffs)}),flush=True)
