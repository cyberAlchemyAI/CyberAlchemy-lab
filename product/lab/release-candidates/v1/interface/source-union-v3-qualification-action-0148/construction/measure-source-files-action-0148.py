"""Read-only original-vs-bulk source verification measurements, no callbacks replaced."""
import hashlib,importlib.util,json,sys,time
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');BASE=ROOT/'product/lab/release-candidates/v1/interface';OUT=Path('/tmp/cal-session-diagnostic-action-0148')
n='_cal_original_source5_file_cost_action_0148';p=BASE/'current-participation-v5';s=importlib.util.spec_from_file_location(n,p/'__init__.py',submodule_search_locations=[str(p)]);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);original=__import__(n+'.base',fromlist=['verify_source'])
spec=importlib.util.spec_from_file_location('_cal_anchored_bulk_file_cost_action_0148',BASE/'api-integration-v7/guard.py');bulk=importlib.util.module_from_spec(spec);spec.loader.exec_module(bulk)
rows=[]
for name in ['current-participation-v5','current-source-adapter-v4','current-mapped-context-v4']:
 path=BASE/name/'source-manifest.json';raw=path.read_bytes();source=json.loads(raw);files=source['files'];unique={r['path']:r for r in files}
 for method in ['original-per-file','anchored-bulk']:
  started=time.monotonic()
  if method=='original-per-file':
   for row in files:original.original(row)
  else:bulk._verify_files(ROOT,files)
  elapsed=time.monotonic()-started
  result={'source':name,'method':method,'rows':len(files),'unique_paths':len(unique),'bytes':sum((ROOT/r['path']).stat().st_size for r in unique.values()),'elapsed_seconds':elapsed,'source_manifest_sha256':hashlib.sha256(raw).hexdigest(),'all_original_bytes_rechecked':True,'no_permission_or_clock_cached':True};rows.append(result);print(json.dumps(result),flush=True)
(OUT/'source-file-costs.json').write_text(json.dumps({'measurements':rows,'authority_effect':'none','actual_owner_outcome':None,'scope':'File verification only; excludes signed projection digest, callback amplification, permission checks and source construction.'},indent=2,sort_keys=True)+'\n')
