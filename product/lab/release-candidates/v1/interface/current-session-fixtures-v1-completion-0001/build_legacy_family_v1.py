"""Exclusive distinct legacy fixture authoring; original source and periods stay frozen."""
import argparse,ast,hashlib,json,re
from pathlib import Path
from datetime import datetime,timedelta,timezone
HERE=Path(__file__).resolve().parent;I=HERE.parent;ROOT=HERE.parents[5]
TEMPLATES={'source':'legacy-session-fixture-source-v1-action-0148','reader':'legacy-session-fixture-reader-v1-action-0148','mapped':'legacy-session-fixture-mapped-v2-action-0148','context':'legacy-session-fixture-context-v1-action-0148'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def write(p,value):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:f.write(value if isinstance(value,str) else json.dumps(value,indent=2,sort_keys=True)+'\n')
def stage(instance):
 if re.fullmatch(r'legacy-[a-z0-9-]{1,40}',instance) is None:raise ValueError('closed separate legacy instance name required')
 out=HERE/'instances'/instance
 if out.exists():raise ValueError('exclusive new legacy family required')
 prefix='completion-'+instance;start=datetime.now(timezone.utc);rows=[]
 for role,name in TEMPLATES.items():
  folder=out/role;folder.mkdir(parents=True)
  for original in sorted((I/name).glob('*.py')):
   if original.name in ('run.py','freeze.py','produce.py','qualify.py','run_checks.py'):continue
   text=original.read_text().replace('HERE.parents[5]','HERE.parents[8]').replace('R03-legacy-session-fixture-0257',prefix)
   text=text.replace('_cal_legacy_', '_cal_'+instance.replace('-','_')+'_legacy_')
   text=text.replace('/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader',str(I/'runtime-dependencies-v1-completion-0001/installations/0001/bin/lab-context-native-reader'))
   for external in ['custody-correction-v4','current-participation-v5','api-v25','fact-read-scope-v1']:
    text=text.replace("HERE.parent/'"+external,"(ROOT/'product/lab/release-candidates/v1/interface')/'"+external)
    text=text.replace('HERE.parent/"'+external,'(ROOT/"product/lab/release-candidates/v1/interface")/"'+external)
   for selected_role,oldname in TEMPLATES.items():
    text=text.replace("HERE.parent/'"+oldname,"HERE.parent/'"+selected_role)
    text=text.replace("ADAPTER_ROOT.parent/'"+oldname,"ADAPTER_ROOT.parent/'"+selected_role)
   # The actual new Implementation names the actual independently captured reader.
   text=text.replace('product/lab/release-candidates/v1/interface/legacy-session-fixture-reader-v1-action-0148/reader.py#SelectedReader.open_signed',(out/'reader/reader.py').relative_to(ROOT).as_posix()+'#SelectedReader.open_signed')
   ast.parse(text);target=folder/original.name;write(target,text);rows.append({'original':binding(original),'new':binding(target),'changed':original.read_text()!=text,'role':role})
  resources=[]
  if role=='mapped':resources=[I/name/'policy.json']
  if role=='context':resources=[I/name/'lifetime-policy.json']+sorted((I/name/'protocols').glob('*.json'))
  for original in resources:
   target=folder/original.relative_to(I/name);write(target,original.read_text());rows.append({'original':binding(original),'new':binding(target),'changed':False,'role':role})
 declaration=json.loads((I/TEMPLATES['source']/'episode-contract.json').read_bytes())
 declaration={k:(v.replace('R03-legacy-session-fixture-0257',prefix) if isinstance(v,str) else v) for k,v in declaration.items()}
 declaration.update(not_before=start.isoformat(),expires_at=(start+timedelta(hours=24)).isoformat(),purpose='Distinct independently signed legacy diagnostic family; no old identity, Assignment or grant renewal.')
 write(out/'source/episode-contract.json',declaration)
 selection={'schema_version':'lab-T02-new-legacy-family-selection/v1-candidate','instance':instance,'prefix':prefix,'public_source_name':'completion-legacy:'+instance,'generator_binding':binding(Path(__file__).resolve()),'episode_binding':binding(out/'source/episode-contract.json'),'original_legacy_source_binding':binding(I/TEMPLATES['source']/'source-manifest.json'),'original_legacy_package_binding':binding(I/TEMPLATES['source']/'packages/0001/manifest.json'),'original_legacy_period_binding':binding(I/TEMPLATES['source']/'packages/0001/period.json'),'original5_period_binding':declaration['old_episode_period_binding'],'template_rows':rows,'original_Assignment_renewed':False,'original_keys_reused':False,'original_permissions_transferred':False,'authority_effect':'none','actual_owner_outcome':None,'status':'staged-unqualified'}
 write(out/'construction-selection.json',selection);return selection
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--instance',required=True);a=p.parse_args();s=stage(a.instance);print(json.dumps({'result':'STAGED-new-legacy-family-UNQUALIFIED','instance':a.instance,'template_rows':len(s['template_rows'])}))
