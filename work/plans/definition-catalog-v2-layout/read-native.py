from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'implementation/lab-runtime/alchlang/ports'))
from creation import Store,current_contract,selected_sources
selected_sources()
data=Store(R/'.local/lab-runtime/shared/current-store',R).replay(require_current=False)
contract=current_contract(data['projection'],'cal.artifact-type.definition/v2')
subjects=data['projection']['subjects']
r=json.loads((R/'authority/admissions/shared-definitions-records-0076/registry.json').read_text())
checks=[]
for row in r['entries']:
 key=row['definition_id']+'@'+row['version']
 if r['current_lookup'].get(row['definition_id'])!=key:continue
 source=R/row['body']['path'];body=json.loads(source.read_text())
 assert hashlib.sha256(source.read_bytes()).hexdigest()==row['body']['sha256']
 observed=subjects.get(key)
 if observed is None:checks.append({'ref':key,'native_subject':False,'original_registry_body_verified':True});continue
 actual=observed.get('record');assert actual==body,(key,list(observed))
 checks.append({'ref':key,'native_subject':True,'original_registry_body_verified':True})
result={'status':'HISTORICAL-VERIFIED-CURRENTNESS-BLOCKED','source_cut':data['baseline']['snapshot_digest'],'native_head':data['head'],'freshness':data['freshness'],'carrier':contract['artifact_type_ref'] if 'artifact_type_ref' in contract else contract['artifact'].get('artifact_type_ref'),'schema_sha256':contract['schema_sha256'],'checks':checks,'authority_effect':'none','scope':'Read-only original native replay and current admitted carrier resolution; no wrapper selection or semantic admission'}
Path(__file__).with_name('NATIVE-OBSERVATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'historical_verification':'PASS','currentness':data['freshness']['status'],'current_bodies':len(checks),'native_subjects':sum(x['native_subject']for x in checks),'carrier_schema':contract['schema_sha256']}))
