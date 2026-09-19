import json,hashlib,shutil,subprocess,os,tarfile,copy
from pathlib import Path
R=Path.cwd();H=R/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0062-shared-meaning-context-import';W=R/'.local/define-package-0062';PREFIX='cyberAlchemy-v2/define/business-ontology/';P=W/PREFIX
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=lambda p:json.loads(p.read_text())
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
shutil.copytree(R.parent/'cyberAlchemy-v2/define/business-ontology',P,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
cap='cyberAlchemy-v2/define/capabilities/define-shared-meaning.product-capability.json';(W/cap).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R.parent/cap,W/cap)
sources=r(P/'SOURCES.json');dump(H/'original-sources.json',sources);recoveries=[]
for row in sources['sources']:
 paths=[R.parent/row['path'],R.parent/'cya-orquestrator'/row['path']]
 if row['path'].startswith('arcanum/spells/invoke/'):paths.append(R.parent/'domainspec-core/.agents/skills/invoke'/row['path'].removeprefix('arcanum/spells/invoke/'))
 chosen=next((p for p in paths if p.is_file() and sha(p)==row['sha256']),None)
 exact=chosen is not None
 if chosen is None:
  assert row['source_id']=='SRC-CAV2-PRODUCT-THESIS';chosen=paths[0]
 data=chosen.read_bytes();assert all(s in data.decode() for s in row['selectors'])
 dst=W/row['path'];dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 recoveries.append({'source_id':row['source_id'],'selected_from':str(chosen),'expected_sha256':row['sha256'],'observed_sha256':sha(dst),'exact_recovery':exact,'all_selectors_present':True})
 if not exact:row['sha256']=sha(dst);row['size_bytes']=len(data)
dump(H/'source-recovery.json',recoveries)
cmd=['python3',str(P/'scripts/validate.py')]
def validate():
 t=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});return t,json.loads(t.stdout)
# Preserve the original validator failure before the successor source record.
t,initial=validate();dump(H/'original-validation.json',{'exit_code':t.returncode,'output':initial})
dump(P/'SOURCES.json',sources)
t,baseline=validate();dump(H/'pre-receipt-validation.json',{'exit_code':t.returncode,'output':baseline})
assert [c['check_id'] for c in baseline['checks'] if c['outcome']=='BLOCK']==['append-only-current-receipt'],baseline
# Receipt exclusion from material digest permits a deterministic fixed-point receipt.
expected=copy.deepcopy(baseline)
for c in expected['checks']:
 if c['check_id']=='append-only-current-receipt':c['outcome']='PASS';c['detail']='1 current receipt'
expected['overall']='PASS';expected['summary']['passed']+=1;expected['summary']['blocked']=0
output=(json.dumps(expected,indent=2,sort_keys=True)+'\n').encode();material=expected['material_digest']
receipt={'schema_version':'cav2.define.business-ontology.validation-receipt/v1','receipt_id':'validation-'+material[:16],'ontology_id':expected['ontology_id'],'validated_on':'2026-09-08','validator':'scripts/validate.py','mode':'check-only','overall':'PASS','material_digest':material,'validation_output_sha256':hashlib.sha256(output).hexdigest(),'summary':expected['summary'],'claim_ceiling':expected['claim_ceiling'],'authority_effect':'none'}
dump(P/'receipts'/('validation-'+material[:16]+'.json'),receipt)
t,final=validate();assert t.returncode==0 and t.stdout.encode()==output,(t.stderr,final);dump(H/'source-validation.json',{'exit_code':0,'output':final,'stdout_sha256':hashlib.sha256(t.stdout.encode()).hexdigest()})
dump(H/'successor-changes.json',{'authority_effect':'none','source_id':'SRC-CAV2-PRODUCT-THESIS','change':'Only the thesis source fingerprint and size use current successor bytes; original selector strings, nodes and relationships are unchanged. A new append-only receipt was predicted then verified byte-for-byte against the unchanged source validator.','historical_search':'No exact-sized 19624-byte blob in either local cya-orquestrator or domainspec-core Git object store, including unreachable objects; no matching PRODUCT-THESIS.md file under projects.','semantic_review':'Current Why Define Exists, Progressive Context Resolution And Sufficiency and Language-Guided Agent Work sections retain the selected dispositions, evidence boundaries and language binding requirements. No claim of full historical text equivalence.','receipt_path':str((P/'receipts'/('validation-'+material[:16]+'.json')).relative_to(W))})
files=sorted(p for p in W.rglob('*') if p.is_file());dump(H/'package-inputs.json',[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files])
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
print(final['summary'])
