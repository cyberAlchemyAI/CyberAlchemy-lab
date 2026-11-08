"""Build a fresh real-clock3600 local fixture on the selected build station.

This creates a new family and signing key. It never extends an existing Source,
Assignment or Session. Source phases and logs remain immutable on failure.
"""
import argparse,hashlib,importlib.util,json,os,re,stat,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
PORT=ROOT/'implementation/lab-runtime/local-host/t25-portable-family-0001'
INSTALL=Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001'
def need(value,message):
 if not value:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
def bind(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}
def write(path,value):
 raw=value if type(value)is bytes else encoded(value)
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
 return {'path':str(path),'sha256':sha(raw)}
def native_command(script,*args):
 return [str(INSTALL/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(INSTALL/'lib/abi'),str(INSTALL/'bin/python'),'-I','-B','-S',str(script),*args]
def execute(command,out,label,timeout=2400):
 stdout=out/(label+'.stdout.log');stderr=out/(label+'.stderr.log');started=datetime.now(timezone.utc).isoformat();at=time.monotonic()
 for path in (stdout,stderr):
  fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600);os.close(fd)
 with stdout.open('wb') as a,stderr.open('wb') as b:
  result=subprocess.run(command,stdout=a,stderr=b,env={'PATH':'/usr/bin:/bin','HOME':str(Path.home()),'LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1'},cwd=ROOT,timeout=timeout,check=False)
 observation={'phase':label,'started_at':started,'ended_at':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':round(time.monotonic()-at,3),'returncode':result.returncode,'stdout_sha256':sha(stdout.read_bytes()),'stderr_sha256':sha(stderr.read_bytes())}
 write(out/(label+'-PROCESS.json'),observation);need(result.returncode==0,'actual '+label+' failed; original logs and staged family retained')
 lines=stdout.read_bytes().splitlines();need(bool(lines),'actual constructor observation missing');return json.loads(lines[-1])
def freeze_dataset(family,out):
 spec=importlib.util.spec_from_file_location('_fresh_renew_metadata',PORT/'metadata_0008.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
 name=family.relative_to(ROOT).as_posix();index=json.loads((family/'source/packages/0001/record-index.json').read_bytes());need(len(index)==26,'new signed Source must contain26 originals')
 for row in index:need(bind(ROOT/row['original_binding']['path'])==row['original_binding'],'new signed original byte binding differs')
 metadata=M.emit_templates(ROOT,out/'templates',family=name);need(len(metadata)==55,'fresh Context metadata inventory differs')
 suffix={'source':'source/source-manifest.json','source_package':'source/packages/0001/manifest.json','reader_source':'reader/source-manifest.json','reader_package':'source/packages/0001/manifest.json','mapper_source':'mapped/source-manifest.json','mapper_package':'mapped/packages/0001/manifest.json','mapping':'mapped/packages/0001/mapping.json','context_source':'context/source-manifest.json','context_package':'context/packages/0001/manifest.json','delivery':'context/packages/0001/delivery.json','period':'source/packages/0001/period.json','record_index':'source/packages/0001/record-index.json','archive_handle':'source/packages/0001/archive-handle.json','context_native_role':'source/context-native-role.json'}
 bindings={'family.'+slot:bind(family/path) for slot,path in suffix.items()}
 for slot,path in {'profile':'runtime/profile.json','manifest':'engine-manifest.json','loader':'loader.py','pins':'pins.json'}.items():bindings['engine.'+slot]=bind(HERE/'engine-v3'/path)
 prior=json.loads((PORT/'PROJECTED-CODE-0006.json').read_bytes());prior_family='implementation/lab-runtime/local-host/t03-long-local-fixture-0001/instances/legacy-local-5bd4f03a7076695c'
 projection=json.loads(json.dumps(prior));projection['source_family']=name;projection['new_family_runtime_qualified']=False
 for row in projection['projected_code']:
  need(bind(ROOT/row['source_binding']['path'])==row['source_binding'],'independently selected generic source code differs')
  if row['path'].startswith(prior_family+'/'):row['path']=name+row['path'][len(prior_family):]
 projection_path=family/'portable-projection.json';write(projection_path,projection)
 period=json.loads((family/'source/packages/0001/period.json').read_bytes());now=datetime.now(timezone.utc)
 need(datetime.fromisoformat(period['not_before'])<=now<datetime.fromisoformat(period['expires_at']),'fresh source actually expired during construction')
 fixture_records={}
 for kind in ('work','challenge-contract','operational-lesson'):
  rows=[row for row in index if row['kind']==kind];need(len(rows)==1,'unique fresh '+kind+' required');fixture_records[kind]={**rows[0]['original_binding'],'version_ref':rows[0]['version_ref']}
 handle=json.loads((family/'source/packages/0001/archive-handle.json').read_bytes());need(sha(Path(handle['path']).read_bytes())==handle['sha256'],'actual fresh signed private archive differs')
 result={'schema_version':'lab-fresh-qualified-dataset-inputs/v1','dataset':{'family':family.name,'store':'completion-'+family.name,'scope':'project:cyberalchemy-v2-to-lab-migration','session_seconds':3600},'family':name,'bindings':bindings,'fixture_records':fixture_records,'original_source_artifacts':[row['original_binding'] for row in index],'fixture_seed':handle,'projection_binding':bind(projection_path),'metadata_templates':metadata,'Source_Reader_Mapper_Context_actual_PASS':True,'API_or_Session_qualified':False,'authority_effect':'none'}
 target=family/'portable-dataset.json';write(target,result);return bind(target)
def run(output):
 output=Path(output)
 need(output.is_absolute() and '..'not in output.parts and not output.exists() and not output.is_symlink() and not output.resolve().is_relative_to(ROOT),'fresh external renewal run directory required')
 need(output.parent.is_dir() and not any(path.is_symlink() for path in output.parents),'existing unlinked renewal parent required')
 output.mkdir(mode=0o700)
 need(INSTALL.is_dir() and not INSTALL.is_symlink() and INSTALL.stat().st_uid==os.getuid() and stat.S_IMODE(INSTALL.stat().st_mode)==0o700,'explicit durable build ABI installation required')
 selected=[HERE/'stage_long.py',HERE/'construct_long_0003.py',HERE/'construct_long_0005.py',PORT/'metadata_0008.py',PORT/'PROJECTED-CODE-0006.json']
 selection=[bind(path) for path in selected];write(output/'BUILD-SELECTION.json',{'selected_inputs':selection,'build_native_root':str(INSTALL),'claim_ceiling':'Local authoring build station only; this is not an installed API runtime or a clock override.','authority_effect':'none'})
 staged=execute(native_command(HERE/'stage_long.py'),output,'stage');instance=staged['instance']
 need(re.fullmatch('legacy-local-[0-9a-f]{16}',instance),'fresh staged identity differs');family=HERE/'instances'/instance
 need(Path(staged['family'])==family and not (family/'source/packages/0001').exists(),'unconsumed new Source construction required')
 # This prospective fixture declares its own actual permission period before
 # Source capture. It does not touch any current runtime grant or lease.
 context=family/'context/build.py';raw=context.read_text();needle='time+timedelta(minutes=20)'
 need(raw.count(needle)==1,'closed new Context construction grant seam required')
 raw=raw.replace(needle,'time+timedelta(minutes=90)')
 need(raw.count("'max_session_seconds':900")==1,'closed new Context Session cap seam required');raw=raw.replace("'max_session_seconds':900","'max_session_seconds':3600")
 compile(raw,str(context),'exec');context.write_text(raw)
 for phase in ('source','cold','reader','mapped','context'):
  script=HERE/('construct_long_0005.py' if phase=='cold' else 'construct_long_0003.py')
  value=execute(native_command(script,'--instance',instance,'--phase',phase),output,phase)
  need(value.get('result')=='PASS','actual fresh '+phase+' terminal observation differs')
  print(json.dumps({'phase':phase,'result':'PASS','instance':instance}),flush=True)
 dataset=freeze_dataset(family,output)
 source_result=json.loads((family/'source/packages/0001/build-result.json').read_bytes())
 context_result=json.loads((family/'context/packages/0001/build-result.json').read_bytes())
 need(source_result['owned_store_and_key_removed'] is True and context_result['owned_host_policy_and_transport_key_removed'] is True,'actual owned signer/policy disposal evidence required')
 need(all(bind(ROOT/row['path'])==row for row in selection),'renewal selected build input changed during execution')
 result={'result':'PASS-real-clock-fresh-Source-Reader-Mapper-Context','instance':instance,'dataset_binding':dataset,'new_period':json.loads((family/'source/packages/0001/period.json').read_bytes()),'new_signing_key_removed':True,'old_Source_or_active_lease_extended':False,'API_or_Session_qualified':False,'build_station_only':True,'authority_effect':'none'}
 write(output/'RESULT.json',result);return result
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--run-root',required=True);args=parser.parse_args();print(json.dumps(run(args.run_root),sort_keys=True),flush=True)
