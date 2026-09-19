"""Apply the user's removal of obsolete Invoke Define coverage to a separate candidate."""
import hashlib,json,shutil,subprocess,os,tarfile
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;OLD=R/'.local/durable-state-successor-0078';W=R/'.local/durable-state-package-0079';P='cyberAlchemy-v2/durable-storage'
r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
shutil.copytree(OLD,W,dirs_exist_ok=True)
p=W/P/'storage-requirements.json';d=r(p);removed=next(x for x in d['requirements'] if x['subject_ref']=='CA2-REF-ARC-INVOKE-DEFINE');d['requirements'].remove(removed);d['coverage_basis']['external_agent_capability_reference_count']=0;d['requirements'][0]['claim_limit']='Does not adopt Define or implement saved sessions.';dump(p,d)
p=W/P/'schemas/durable-storage.schema.json';d=r(p);d['$defs']['coverageBasis']['properties']['external_agent_capability_reference_count']['const']=0
# Receipt counts must describe the revised inventory too.
def update(obj):
 if isinstance(obj,dict):
  for k,v in obj.items():
   if k=='requirements' and v=={'const':13}:obj[k]={'const':12}
   elif k=='external_agent_capability_references' and v=={'const':1}:obj[k]={'const':0}
   else:update(v)
 elif isinstance(obj,list):
  for v in obj:update(v)
update(d);dump(p,d)
p=W/P/'scripts/validate.py';s=p.read_text().replace('    "CA2-REF-ARC-INVOKE-DEFINE",\n','').replace('EXTERNAL_SUBJECT = "CA2-REF-ARC-INVOKE-DEFINE"\n','');start=s.index('        if subject_ref == EXTERNAL_SUBJECT:');end=s.index('        if requirement.get("authority_effect")',start);branch=s[s.index('        else:\n',start)+len('        else:\n'):end];s=s[:start]+''.join(line[4:] if line.startswith('    ') else line for line in branch.splitlines(keepends=True))+s[end:];p.write_text(s)
p=W/P/'tests/test_negative_mutations.py';s=p.read_text();start=s.index('    def test_external_capability_assignment_blocks');end=s.index('    def test_path_capture_blocks',start);s=s[:start]+'''    def test_obsolete_external_capability_reintroduction_blocks(self) -> None:
        def mutate() -> None:
            value = self.load("storage-requirements.json")
            obsolete = copy.deepcopy(value["requirements"][0])
            obsolete["requirement_id"] = "DS-REQ-EXTERNAL-INVOKE-DEFINE"
            obsolete["subject_ref"] = "CA2-REF-ARC-INVOKE-DEFINE"
            value["requirements"].append(obsolete)
            self.save("storage-requirements.json", value)
        self.assert_blocked(mutate)

'''+s[end:];p.write_text(s)
historical=W/'historical/durable-storage-receipts';historical.mkdir(parents=True,exist_ok=True)
for receipt in (W/P/'receipts').glob('*.json'):shutil.move(str(receipt),str(historical/receipt.name))
changes=[{'path':str(p.relative_to(W)),'before':sha(OLD/p.relative_to(W)),'after':sha(p)} for p in sorted(W.rglob('*')) if p.is_file() and (OLD/p.relative_to(W)).exists() and sha(p)!=sha(OLD/p.relative_to(W))]
dump(H/'scope-change.json',{'authority_effect':'none','decision_basis':'User: we dont need this, define is already reworked without it','removed_requirement':removed,'changes':changes,'preserved':'Twelve Product Capability requirements, including Define shared meaning. Original source checkout and execution 0078 unchanged. Historical receipts retained as historical evidence.'})
for filename,args in [('source-validation.json',['scripts/validate.py']),('negative-tests.json',['tests/test_negative_mutations.py'])]:
 c=subprocess.run(['python3',str(W/P/args[0])],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});dump(H/filename,{'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr});print(filename,c.returncode,c.stdout,c.stderr);assert c.returncode==0
inputs=[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in sorted(W.rglob('*')) if p.is_file()];dump(H/'package-inputs.json',inputs)
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for x in inputs:a.add(W/x['path'],arcname=x['path'],recursive=False)
manifest=r(H.parent/'0075-shared-capability-runtime-import/runtime-manifest.json');pkg=manifest['packages'][0];alias='durable79'
def ref(path):return {'root':alias,'path':path,'sha256':sha(W/path)}
pkg['profile']=ref(P+'/profile.json');pkg['package_key']='pkg-'+hashlib.sha256((alias+':'+P+'/profile.json').encode()).hexdigest();pkg['ontology_id']=r(W/P/'profile.json')['ontology_id'];pkg['owner']=r(W/P/'profile.json')['package_owner'];pkg['documents']=[ref(x['path']) for x in inputs]
for field in ['nodes','relations']:pkg[field]['source']=ref(P+'/'+field+'.json')
pkg['nodes']['type_field']='kind' if 'kind' in r(W/P/'nodes.json')['nodes'][0] else 'role'
manifest['roots']={alias:str(W)};dump(H/'runtime-manifest.json',manifest)
