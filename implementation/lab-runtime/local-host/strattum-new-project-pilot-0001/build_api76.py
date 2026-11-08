"""One isolated API76 build stream for the local Project pilot.

An existing installation is never replaced. A completed Source generation may
be resumed using an explicitly selected dataset contract and exact digest.
"""
import argparse,hashlib,importlib.util,json,os,resource,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=ROOT/'implementation/lab-runtime/local-host/t03-long-local-fixture-0001'
TOOLS=ROOT/'implementation/lab-runtime/local-host/t25-integrated-runtime-0004'
spec=importlib.util.spec_from_file_location('_renew_build_station',HERE/'renew_local.py');R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
def descriptor_profile():
 soft,hard=resource.getrlimit(resource.RLIMIT_NOFILE);required=65536
 R.need(hard==resource.RLIM_INFINITY or hard>=required,'local runtime build requires a process hard RLIMIT_NOFILE of at least65536 before generation')
 if soft!=resource.RLIM_INFINITY and soft<required:resource.setrlimit(resource.RLIMIT_NOFILE,(required,hard))
 actual=resource.getrlimit(resource.RLIMIT_NOFILE)
 R.need(actual[0]==resource.RLIM_INFINITY or actual[0]>=required,'local runtime process descriptor profile could not be established')
 return {'soft':actual[0],'hard':actual[1],'required_minimum':required,'host_global_setting_changed':False}
def run(output,dataset_path=None,dataset_pin=None):
 limits=descriptor_profile()
 free=os.statvfs('/mnt/d').f_bavail*os.statvfs('/mnt/d').f_frsize
 R.need(free>=11*1024**3,'D: backing-drive free space below 11 GiB prewrite threshold')
 output=Path(output)
 R.need(output.is_absolute() and not output.exists() and not output.is_symlink() and '..'not in output.parts and not output.resolve().is_relative_to(ROOT),'fresh external pipeline output required')
 R.need(output.parent.is_dir() and not any(path.is_symlink() for path in output.parents),'existing unlinked pipeline parent required');output.mkdir(mode=0o700)
 selected=[R.bind(path) for path in (Path(__file__).resolve(),HERE/'renew_local.py',TOOLS/'package_view_api76.py',TOOLS/'archive.py',TOOLS/'install_from_archive.py')]
 R.write(output/'PIPELINE-SELECTION.json',{'selected_entrypoints':selected,'authoring_native_installation':str(R.INSTALL),'process_descriptor_profile':limits,'backing_drive':'D:','backing_drive_available_bytes_prewrite':free,'API_or_Session_qualified':False,'authority_effect':'none'})
 def command(script,*args,label,timeout=3600):
  return R.execute([sys.executable,'-B',str(script),*map(str,args)],output,label,timeout=timeout)
 try:
  if dataset_path is None:
   R.need(dataset_pin is None,'exact dataset path and digest must be supplied together')
   generated=command(HERE/'renew_local.py','--run-root',output/'generation',label='generate',timeout=7200)
   R.need(generated['result']=='PASS-real-clock-fresh-Source-Reader-Mapper-Context','actual fresh generation did not complete');binding=generated['dataset_binding'];dataset=ROOT/binding['path'];pin=binding['sha256']
  else:
   R.need(type(dataset_pin)is str and len(dataset_pin)==64,'explicit previously generated dataset digest required');dataset=Path(dataset_path).absolute();pin=dataset_pin
  raw=dataset.read_bytes();R.need(hashlib.sha256(raw).hexdigest()==pin,'selected generated dataset bytes differ');body=json.loads(raw)
  R.need(body['schema_version']=='lab-fresh-qualified-dataset-inputs/v1' and body['Source_Reader_Mapper_Context_actual_PASS'] is True and body['authority_effect']=='none','completed local Source generation required')
  R.write(output/'GENERATED-DATASET-SELECTION.json',{'path':str(dataset),'sha256':pin,'family':body['family'],'authority_effect':'none'})
  view=output/'view';command(TOOLS/'package_view_api76.py',view,'--api','api76','--dataset-contract',dataset,'--dataset-contract-sha256',pin,label='package-view')
  package_pin=hashlib.sha256((view/'PACKAGE-MANIFEST.json').read_bytes()).hexdigest()
  artifact=output/'lab-runtime.tar.gz';archive=command(TOOLS/'archive.py','write',view,artifact,label='artifact-write')
  R.need(archive['result']=='PASS-exact-public-archive-written' and archive['package_manifest_sha256']==package_pin,'actual selected archive observation differs')
  destination=output/'installation';installed=command(TOOLS/'install_from_archive.py',artifact,archive['archive_sha256'],package_pin,destination,label='fresh-installation',timeout=7200)
  R.need(installed['result']=='PASS-fresh-installed-API-cold' and installed['archive_sha256']==archive['archive_sha256'] and installed['package_manifest_sha256']==package_pin,'actual renewed installed API observation differs')
  R.need(all(R.bind(ROOT/row['path'])==row for row in selected),'selected build entrypoint changed during execution')
  result={'result':'PASS-real-clock-renewed-fresh-installed-API76','dataset_binding':{'path':str(dataset),'sha256':pin},'installation':installed,'artifact':{'path':str(artifact),'sha256':archive['archive_sha256']},'old_active_installation_replaced':False,'old_Source_or_Session_lease_extended':False,'full_regression_qualified':False,'inside_Docker_generation_qualified':False,'authority_effect':'none'}
  R.write(output/'RESULT.json',result);return result
 except BaseException as error:
  R.write(output/'FAILED-RETAINED.json',{'exception_class':type(error).__name__,'message':str(error),'owned_output':str(output),'existing_installation_modified':False,'authority_effect':'none'});raise
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--run-root',required=True);parser.add_argument('--reuse-dataset',type=Path);parser.add_argument('--dataset-sha256');args=parser.parse_args();print(json.dumps(run(args.run_root,args.reuse_dataset,args.dataset_sha256),sort_keys=True),flush=True)
