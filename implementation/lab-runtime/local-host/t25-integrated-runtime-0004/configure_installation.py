"""Private per-install selection construction after exact public materialization."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile

sha=lambda raw:hashlib.sha256(raw).hexdigest()
encoded=lambda value:(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
def need(value,reason):
 if not value:raise ValueError(reason)
def atomic_control(path,raw):
 path=Path(path);path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 fd,name=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())
  os.chmod(name,0o600);os.replace(name,path)
  fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:Path(name).unlink(missing_ok=True)
def code(root,manifest):
 path='implementation/lab-runtime/local-host/t25-portable-family-0001/metadata.py'
 rows={r['path']:r for r in manifest['members']};raw=(root/path).read_bytes()
 need(sha(raw)==rows[path]['sha256'],'installed metadata constructor differs from public package')
 spec=importlib.util.spec_from_file_location('_cal_installer_family_metadata',root/path);module=importlib.util.module_from_spec(spec);exec(compile(raw,str(root/path),'exec'),module.__dict__);return module

def provision_retained_fixture(root,manifest,metadata):
 selected=manifest.get('retained_origin_fixture')
 if selected is None:return None
 need(type(selected)is dict and set(selected)=={'seed_binding','inputs_binding','data_audit_binding','classification'} and selected['classification']=='SYNTHETIC-retained-native-origin-fixture-public-seed-eligible','closed explicitly audited synthetic retained fixture required')
 members={row['path']:row for row in manifest['members']};bodies={}
 for slot in ('seed_binding','inputs_binding','data_audit_binding'):
  binding=selected[slot];need(type(binding)is dict and set(binding)=={'path','sha256'},'closed retained fixture file binding required');metadata.relative(binding['path']);need(members.get(binding['path'],{}).get('sha256')==binding['sha256'],'retained fixture must be independently selected public package member');bodies[slot]=metadata.capture(root/binding['path'],binding['sha256'])
 path=root/selected['inputs_binding']['path'];spec=importlib.util.spec_from_file_location('_cal_installer_synthetic_origin',path);module=importlib.util.module_from_spec(spec);exec(compile(bodies['inputs_binding'],str(path),'exec'),module.__dict__)
 qualification=root.parent/'.cal-runtime/qualification';qualification.mkdir(mode=0o700,parents=True,exist_ok=True);need(metadata.identity(qualification)[2:]==[os.getuid(),0o700],'owned private fixture qualification directory required')
 result=module.provision(root/selected['seed_binding']['path'],qualification/'t22-origin71')
 atomic_control(root.parent/'.cal-runtime/qualification/t22-origin71-PROVISION.json',encoded(result))
 return result

def configure(root,package_pin,phase):
 root=Path(root).resolve();private=root.parent/'.cal-runtime'
 raw=(root/'.cal-package-manifest.json').read_bytes();need(sha(raw)==package_pin,'selected stable package differs')
 manifest=json.loads(raw);M=code(root,manifest)
 need(M.identity(private)[2:]==[os.getuid(),0o700],'owned private runtime root required')
 if phase=='construct-context':
  need(not (private/'installation.json').exists(),'refuse reprovision already selected installation')
  seed=manifest['fixture_seed'];seed_raw=M.capture(root/seed['path'],seed['sha256'])
  target=private/'fixture-archives/branch.snapshot';target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
  if target.exists():M.capture(target,seed['sha256'],mode=0o600)
  else:atomic_control(target,seed_raw)
  result=M.Constructor(root,package_pin).initial()
  provision_retained_fixture(root,manifest,M)
  atomic_control(private/'construction-selection.json',encoded(result))
 else:
  need(phase=='ready','closed installer phase required')
  prior=json.loads(M.capture(private/'construction-selection.json',mode=0o600))
  observed=json.loads(M.capture(private/'construction-outcome.json',mode=0o600))
  current_receipt=M.capture(private/'installation.json',mode=0o600)
  need(observed['schema_version']=='lab-observed-native-construction/v1'
       and observed['package_manifest_sha256']==package_pin
       and observed['construct_receipt_sha256']==sha(current_receipt)
       and observed['returncode']==0
       and observed['final_observation']['result']=='PASS-construction-native-cold-and-fresh-Context',
       'actual selected construction terminal proof required before runtime readiness')
  context_result=manifest['binding_paths']['family.context_package'].rsplit('/',1)[0]+'/build-result.json'
  actual_context=json.loads(M.capture(root/context_result))
  need(actual_context['result']=='PASS' and actual_context['actual_Context_Delivery_posture']=='ready'
       and actual_context['owned_host_policy_and_transport_key_removed'] is True,
       'actual generated Context result required before runtime readiness')
  constructor=M.Constructor(root,package_pin)
  need(hasattr(constructor,'finalize'),'actual Context finalizer is required before runtime readiness')
  constructor.finalize()
  result={'values':prior['values'],'bindings':constructor.export_bindings(ready=True),'phase':'ready'}
 selection={'schema_version':'lab-private-host-selection/v1','package_manifest_sha256':package_pin,
            'repository_root':str(root),'bindings':result['bindings'],'values':result['values'],
            'authority_effect':'none','fixture_only':True}
 selection_raw=encoded(selection);atomic_control(private/'bindings/host-selection.json',selection_raw)
 receipt={'schema_version':'lab-private-installation-receipt/v1','package_manifest_sha256':package_pin,
          'host_selection_sha256':sha(selection_raw),'private_root_identity':M.identity(private),
          'authority_effect':'none','fixture_only':True,'phase':phase}
 receipt_raw=encoded(receipt);atomic_control(private/'installation.json',receipt_raw)
 launcher={'schema_version':'lab-installed-launcher-selection/v1','installation_receipt_sha256':sha(receipt_raw)}
 atomic_control(private/'launcher.json',encoded(launcher))
 return {'result':'PASS-private-installation-metadata','phase':phase,'repository':str(root),
         'package_manifest_sha256':package_pin,'installation_receipt_sha256':sha(receipt_raw),
         'API_qualified':False,'authority_effect':'none'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('repository',type=Path);p.add_argument('package_sha256');p.add_argument('phase',choices=('construct-context','ready'));a=p.parse_args();print(json.dumps(configure(a.repository,a.package_sha256,a.phase),sort_keys=True),flush=True)
