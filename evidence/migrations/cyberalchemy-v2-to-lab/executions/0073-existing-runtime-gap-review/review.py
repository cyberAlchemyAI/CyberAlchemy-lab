"""Compare existing surfaces and prepare a read-only v4 plan. Open questions: README.md."""
import json,hashlib,shutil
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=lambda p:json.loads(p.read_text())
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
paths={'legacy/runtime.py':R.parent/'cyberAlchemy-v2/implementation/ontology-runtime/runtime.py','legacy/registry.json':R.parent/'cyberAlchemy-v2/implementation/ontology-runtime/registry.json','legacy/README.md':R.parent/'cyberAlchemy-v2/implementation/ontology-runtime/README.md','lab/v4/manifest.json':R/'implementation/bindings/ontology-product-event-runtime/v4/source-manifest.json','lab/v4/main.rs':R/'implementation/bindings/ontology-product-event-runtime/v4/src/main.rs','lab/v4/lib.rs':R/'implementation/bindings/ontology-product-event-runtime/v4/src/lib.rs','lab/v4/README.md':R/'implementation/bindings/ontology-product-event-runtime/v4/README.md','lab/graph/lib.rs':R/'ontology-lifecycle/runtime-candidates/cal-ontology-graph-read-model/v1/src/lib.rs','lab/context/lib.rs':R/'ontology-lifecycle/runtime-candidates/cal-ontology-context-adapters-v2/v1/src/lib.rs'}
for name,p in paths.items():dst=H/'source'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
dump(H/'source-bindings.json',[{'source_path':str(p),'snapshot_path':'source/'+name,'sha256':sha(p)} for name,p in paths.items()])
legacy=r(H/'source/legacy/registry.json');v4=r(H/'source/lab/v4/manifest.json');coverage=[]
for e in legacy['entries']:
 matches=[p for p in v4['packages'] if p['ontology_id']==e['ontology_id']]
 coverage.append({'ontology_id':e['ontology_id'],'legacy_package_root':e['package_root'],'v4_package_keys':[p['package_key'] for p in matches],'status':'identity-present-version-not-proven' if matches else 'absent-from-v4-manifest'})
dump(H/'package-coverage.json',{'legacy_registration_count':len(legacy['entries']),'v4_manifest_package_count':len(v4['packages']),'rows':coverage,'scope':'Exact inspected registry and v4 manifest only; not all Lab stores or packages.','authority_effect':'none'})
root=R/'.local/ontology-context-import-0072/package';prefix='cyberAlchemy-v2/people-and-teams';profile=prefix+'/profile.json'
def source(name):return {'root':'people72','path':prefix+'/'+name,'sha256':sha(root/prefix/name)}
def registry(name,key,typ,edges=False):return {'source':source(name),'selector':'/'+key,'id_field':'id','type_field':typ,'source_field':'source' if edges else None,'target_field':'target' if edges else None,'direction_map':{'directed':'directed'} if edges else {}}
pkg={'package_key':'pkg-'+hashlib.sha256(('people72:'+profile).encode()).hexdigest(),'ontology_id':'cav2.people-and-teams.business','profile':source('profile.json'),'owner':'CyberAlchemy v2 People and Teams product owner','source_status':'candidate-unadmitted','nodes':registry('nodes.json','nodes','role'),'relations':registry('relations.json','relations','type',True),'endpoint_aliases':{},'documents':[{'root':'people72','path':str(p.relative_to(root)),'sha256':sha(p)} for p in sorted(root.rglob('*')) if p.is_file()]}
dump(H/'people-teams-plan.json',{'schema_version':'cal-source-runtime-manifest/v1','authority_effect':'none','roots':{'people72':str(root)},'packages':[pkg]})
print('Compared six registrations; prepared one package for existing v4 plan.')
