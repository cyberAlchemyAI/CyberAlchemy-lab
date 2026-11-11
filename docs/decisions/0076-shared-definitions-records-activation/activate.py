"""Select only the verified, already published 0076 bundle; no native retry."""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text())
def put(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_name(p.name+'.pending')
 temp.write_text(json.dumps(v,indent=2)+'\n');temp.replace(p)
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
subprocess.run(['python3','-B',str(HERE/'validate.py')],check=True)
decision=load(HERE/'decision.json');assert decision['status']=='owner-admitted-and-activated'
bundle=ROOT/'authority/admissions/shared-definitions-records-0076'
receipt=load(HERE/'receipts/publication.json')
assert receipt['selected']['revision']==1
selection={'schema_version':'lab-definition-registry-selection/v1','status':'owner-admitted-current','decision':binding(HERE/'decision.json'),'registry':binding(bundle/'registry.json'),'bundle':binding(bundle/'bundle.json'),'selector':receipt['selected'],'reader_protocol':'snapshot-selector/v1','legacy_registry':binding(ROOT/'authority/definitions/registry.json'),'compatibility':'Legacy v1 is an immutable native compatibility baseline; canonical shared readers select this v2 snapshot.'}
selection['index']='authority/admissions/shared-definitions-records-0076/DEFINITIONS-INDEX.md'
put(ROOT/'authority/definitions/current.json',selection)
put(ROOT/'authority/artifact-types/definition-registry/current.json',{'status':'owner-admitted-current','artifact_type_ref':'cal.artifact-type.definition-registry/v2','decision':binding(HERE/'registry-admission.json'),'descriptor':binding(HERE/'registry-descriptor.json')})
reg=load(bundle/'registry.json')
lines=['<!-- GENERATED: selected Registry/v2; authority/definitions/current.json -->','','# Canonical Definitions index','','194 admitted versions; 188 current identities. Registry/v1 remains a frozen compatibility baseline.','','| Definition | Current version |','| --- | --- |']
lines += ['| '+k+' | '+v+' |' for k,v in sorted(reg['current_lookup'].items())]
(bundle/'DEFINITIONS-INDEX.md').write_text('\n'.join(lines)+'\n')
catalog=ROOT/'implementation/lab-workspaces/v2/catalog.json';c=load(catalog)
c['runtimes']['lab:shared-runtime']['entrypoint']='implementation/lab-runtime/lab.mjs'
put(catalog,c)
config={'schema_version':'lab-shared-workflow-activation/v1','status':'active','workspace':'workspace:cyberalchemy-lab:lab','decision_ref':decision['decision_ref'],'decision':binding(HERE/'decision.json'),'registry_selection':'authority/definitions/current.json','database':'.local/lab-runtime/shared/snapshots.sqlite','journal':'.local/lab-runtime/shared/journal.sqlite','native_store':'.local/lab-runtime/shared/native-store','trust':str((HERE/'trust.json').relative_to(ROOT)),'private_key_policy':'Operator key remains outside repository in ~/.config/cyberalchemy-lab/shared-records/operator.pem','selector':receipt['selected'],'legacy_native_profile':'implementation/lab-runtime/v2/profile.json','runtime_policy':'one-central-runtime-no-product-copies'}
transition=HERE/'receipts/source-transition.json'
if transition.exists():
 t=load(transition);config['native_store']='.local/lab-runtime/shared/current-store'
 config['native_source_cut']=t['current_source_cut'];config['historical_publication_store']='.local/lab-runtime/shared/native-store'
put(ROOT/'implementation/lab-runtime/shared-workflow.json',config)
print(json.dumps({'status':'active','versions':194,'current':188,'shared_runtime_targets':1,'runtime_copies':0}))
