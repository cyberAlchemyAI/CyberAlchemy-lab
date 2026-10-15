"""Recover disappeared owned dependencies and byte-identical selected native code."""
import argparse,hashlib,json,os,shutil,subprocess,sys,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
ENV=Path('/tmp/cal-R02-environment-0001');BUILD=Path('/tmp/cal-R03-mapped-native-build-0002')
NATIVE_SHA='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');p.chmod(0o600)
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);a=p.parse_args();m=json.loads((HERE/'source-manifest.json').read_bytes());assert sha(HERE/'source-manifest.json')==a.source_sha256
 for row in m['files']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
 assert not ENV.exists() and not BUILD.exists(),'only absent owned roots may be recreated'
 out=HERE/'receipts/0001';out.mkdir(parents=True,exist_ok=False,mode=0o700)
 r={'result':'FAIL','authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'source_freeze_sha256':a.source_sha256}
 try:
  subprocess.run([sys.executable,'-m','venv','--without-pip',str(ENV)],check=True)
  site=next((ENV/'lib').glob('python*/site-packages'))
  for row in m['wheels']:
   file=ROOT/row['path'];assert sha(file)==row['sha256']
   with zipfile.ZipFile(file) as z:
    for name in z.namelist():
     dest=site/name;assert not Path(name).is_absolute() and '..' not in Path(name).parts and dest.is_relative_to(site)
     if name.endswith('/'):dest.mkdir(parents=True,exist_ok=True)
     else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(name))
  check=subprocess.run([str(ENV/'bin/python'),'-c',"import importlib.metadata,json,sys;print(json.dumps({'python':sys.version,'distributions':{k:importlib.metadata.version(k) for k in ['jsonschema','cryptography','referencing','attrs','cffi','rpds-py','pycparser','jsonschema-specifications']}}))"],capture_output=True,text=True,check=True)
  selected=json.loads(check.stdout);assert selected['distributions']==m['distributions'] and selected['python']==m['interpreter'];emit(out/'python-environment.json',selected)
  BUILD.mkdir(mode=0o700);native=json.loads((ROOT/m['native_source_binding']['path']).read_bytes())
  for row in native['copies']:
   p=BUILD/row['target'];p.parent.mkdir(parents=True,exist_ok=True);raw=(ROOT/row['binding']['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==row['binding']['sha256'];p.write_bytes(raw)
  for folder in ['reader','ontology']:
   shutil.copyfile(ROOT/'product/lab/release-candidates/v1/interface/mapped-native-v2/receipts'/(folder+'-resolved-lock.toml'),BUILD/folder/'Cargo.lock')
  env=dict(os.environ);env['CARGO_TARGET_DIR']=str(BUILD/'target');observations=[]
  for label,command in [('build',['cargo','build','--offline','--frozen','--manifest-path',str(BUILD/'reader/Cargo.toml')]),('tests',['cargo','test','--offline','--frozen','--manifest-path',str(BUILD/'ontology/Cargo.toml')])]:
   with open(out/(label+'.stdout'),'xb') as stdout,open(out/(label+'.stderr'),'xb') as stderr:
    completed=subprocess.run(command,stdout=stdout,stderr=stderr,env=env)
   observations.append({'producer':label,'exit_code':completed.returncode,'terminal_observed':True});assert completed.returncode==0,label
  exe=BUILD/'target/debug/lab-context-native-reader';actual=sha(exe);assert actual==NATIVE_SHA,'rebuilt executable differs; successor binding needed, no substitution permitted'
  r.update(result='PASS',selected_native_sha256=actual,native_byte_identity=True,observations=observations,owned_environment=str(ENV),owned_compile_root=str(BUILD))
 except BaseException as error:r['failure']=str(error)
 emit(out/'result.json',r);print(json.dumps(r),flush=True);return 0 if r['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
