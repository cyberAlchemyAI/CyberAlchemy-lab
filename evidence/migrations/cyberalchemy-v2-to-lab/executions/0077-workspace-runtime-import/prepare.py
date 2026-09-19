"""Create explicit reference projections and an isolated successor registration. See README.md."""
import json,hashlib,shutil,tarfile,subprocess,os
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;W=R/'.local/workspace-runtime-package-0077';P='cyberAlchemy-v2/workspace';r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
shutil.copytree(R/'.local/workspace-successor-0076',W,dirs_exist_ok=True)
registry_path=W/'cyberAlchemy-v2/implementation/ontology-runtime/registry.json';registry=r(registry_path);entry=next(e for e in registry['entries'] if e['ontology_id']=='cav2.workspace.capability');h=hashlib.sha256()
for name in sorted(entry['material_files']):h.update(name.encode()+b'\0'+(W/P/name).read_bytes()+b'\0')
old=entry['expected_material_digest'];entry['expected_material_digest']=h.hexdigest();dump(registry_path,registry)
dump(H/'registration-change.json',{'ontology_id':entry['ontology_id'],'before':old,'after':entry['expected_material_digest'],'scope':'Isolated candidate entry only; other entries are preserved, not validated. Runtime verification uses existing Lab v4, not legacy Python runtime activation.','authority_effect':'none'})
defs='cyberAlchemy-v2/authority/definitions/DEFINITIONS.md';lines=(W/defs).read_bytes().splitlines(keepends=True);refs=[];mappings=[]
for item in r(W/P/'sources.json')['definition_selections']:
 if item['selection_id'] not in ['CAV2-D60','CAV2-D67']:continue
 start=next(i for i,l in enumerate(lines) if l.rstrip(b'\r\n')==item['selector'].encode());end=next((i for i in range(start+1,len(lines)) if lines[i].startswith(b'## ')),len(lines));data=b''.join(lines[start:end]);assert hashlib.sha256(data).hexdigest()==item['expected_digest']
 refs.append({'id':item['selection_id'],'kind':'external-definition-reference','label':item['selector'].split(': ',1)[1],'claim':'Exact historical source definition reference; no Lab definition adoption.','source_path':defs,'selector':item['selector'],'selected_sha256':item['expected_digest'],'selected_text':data.decode(),'owner_route':'CyberAlchemy v2 definitions-governance owner','authority_effect':'none'})
baseline='cyberAlchemy-v2/essays/implementation/semantic-explorer/REALIZATION-BASELINE.candidate.json';base=r(W/baseline);assert base['baseline_id']=='ESSAYS-REALIZATION-BASELINE-003'
refs.append({'id':base['baseline_id'],'kind':'external-design-evidence-reference','label':'Essays explorer baseline 003','claim':'Historical unaccepted design evidence; no implementation or acceptance inference.','source_path':baseline,'selector':'/','selected_sha256':sha(W/baseline),'source_record':base,'owner_route':'Essays Project owner','authority_effect':'none'})
dump(W/'adapters/workspace-external-references.json',{'ontology_id':'lab.workspace.external-reference-projections.0077','nodes':refs,'relations':[],'authority_effect':'none'})
edges=r(W/P/'relations.json');refids={x['id'] for x in refs}
for i,e in enumerate(edges['relations']):
 if e['target'] in refids:
  original=e['target'];e['target']='external::'+original;mappings.append({'source_path':P+'/relations.json','selector':'/relations/'+str(i),'relation_id':e['id'],'source_target':original,'runtime_target':e['target'],'conversion':'explicit cross-package endpoint qualification only'})
assert len(mappings)==3;dump(W/'adapters/workspace-relations.json',edges);dump(H/'endpoint-mappings.json',mappings)
root='workspace77'
def source(path):return {'root':root,'path':path,'sha256':sha(W/path)}
def reg(path,sel,typ,edge=False):return {'source':source(path),'selector':sel,'id_field':'id','type_field':typ,'source_field':'source' if edge else None,'target_field':'target' if edge else None,'direction_map':{'directed':'directed'} if edge else {}}
def key(path):return 'pkg-'+hashlib.sha256((root+':'+path).encode()).hexdigest()
refpath='adapters/workspace-external-references.json';docs=[source(str(f.relative_to(W))) for f in sorted(W.rglob('*')) if f.is_file() and 'adapters' not in f.relative_to(W).parts]
packages=[{'package_key':key(P+'/profile.json'),'ontology_id':'cav2.workspace.capability','profile':source(P+'/profile.json'),'owner':'CyberAlchemy Workspace owner','source_status':'candidate-unadmitted','nodes':reg(P+'/nodes.json','/nodes','kind'),'relations':reg('adapters/workspace-relations.json','/relations','type',True),'endpoint_aliases':{'external':key(refpath)},'documents':docs},{'package_key':key(refpath),'ontology_id':'lab.workspace.external-reference-projections.0077','profile':source(refpath),'owner':'Lab migration projection; source meaning owners retained per record','source_status':'reference-projections-only','nodes':reg(refpath,'/nodes','kind'),'relations':reg(refpath,'/relations','type',True),'endpoint_aliases':{},'documents':[]}]
dump(H/'runtime-manifest.json',{'schema_version':'cal-source-runtime-manifest/v1','authority_effect':'none','roots':{root:str(W)},'packages':packages})
c=subprocess.run(['python3',str(W/P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});dump(H/'source-validation.json',{'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr});assert c.returncode==0
files=sorted(f for f in W.rglob('*') if f.is_file());dump(H/'package-inputs.json',[{'path':str(f.relative_to(W)),'sha256':sha(f)} for f in files])
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for f in files:a.add(f,arcname=str(f.relative_to(W)),recursive=False)
print('Prepared',len(docs),'documents; 12 source nodes, 3 explicit references, 14 relationships.')
