"""One concrete local install stream over an independently selected artifact.

Publish the owned layout before minting host-path bindings. A failed install
stays provisional and cannot activate the API; existing installations stay put.
"""
import argparse,hashlib,importlib.util,json,os,shutil,subprocess,sys,tempfile,uuid
sys.dont_write_bytecode=True
os.environ['PYTHONDONTWRITEBYTECODE']='1'
from pathlib import Path
HERE=Path(__file__).resolve().parent

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
A=module('_cal_transport_install',HERE/'archive.py');N=module('_cal_native_install',HERE/'native_install.py');C=module('_cal_configure_install',HERE/'configure_installation.py');R=module('_cal_constructor_observer',HERE/'construction_runner.py')

def install(archive,archive_pin,package_pin,destination):
 archive=Path(archive);destination=Path(destination)
 C.need(destination.is_absolute() and '..'not in destination.parts,'absolute fresh installation destination required')
 C.need(A.file_sha(archive)==archive_pin,'independently selected archive bytes differ')
 C.need(not destination.exists() and not destination.is_symlink(),'refuse existing installation target')
 parent=A.M.owned_directory(destination.parent);stage=parent/('.lab-install-'+uuid.uuid4().hex);stage.mkdir(mode=0o700)
 published=False
 try:
  transport=stage/'transport';transport.mkdir(mode=0o700);A.extract_archive(archive,transport,package_pin)
  manifest_raw=(transport/'PACKAGE-MANIFEST.json').read_bytes();manifest=json.loads(manifest_raw)
  runtime=stage/'runtime';runtime.mkdir(mode=0o700);private=runtime/'.cal-runtime';private.mkdir(mode=0o700)
  repository=runtime/'repository';N.publish(transport/'repository',repository)
  # Keep the original public host namespace untouched. Docker's isolated
  # namespace snapshot layer is a separate explicit packaging operation.
  for row in manifest['host_inputs']:A.M.exact(row['path'],row)
  A.M.write_new(repository/'.cal-package-manifest.json',manifest_raw,0o644)
  native=N.install(private,transport/'native-payload',manifest['native_payload']['members'],manifest['native_payload']['selection_binding']['sha256'])
  abi=N.cold_abi(private/'native')
  # This final path is selected before any role/Source/Context metadata is made.
  destination.mkdir(mode=0o700);N.publish(runtime,destination/'runtime');published=True
  root=destination/'runtime/repository';private=root.parent/'.cal-runtime'
  C.atomic_control(private/'provisional-installation.json',C.encoded({'schema_version':'lab-provisional-artifact-installation/v1','archive_sha256':archive_pin,'package_manifest_sha256':package_pin,'native_ABI_observation':abi,'phase':'unqualified','authority_effect':'none'}))
  configured=C.configure(root,package_pin,'construct-context')
  constructed=R.run(root,package_pin,configured['installation_receipt_sha256'])
  ready=C.configure(root,package_pin,'ready')
  launcher=root/'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python'
  probe=root/'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/qualify_installed_api.py'
  result=subprocess.run([str(launcher),'-B',str(probe)],env={'PATH':'/usr/bin:/bin','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1','HOME':str(private)},cwd=root,capture_output=True,timeout=1200,check=False)
  C.atomic_control(private/'API-cold-stdout.log',result.stdout);C.atomic_control(private/'API-cold-stderr.log',result.stderr)
  C.need(result.returncode==0,'actual installed cold API qualification failed; owned logs retained')
  observation=json.loads(result.stdout.splitlines()[-1]);C.need(observation['result']=='PASS-installed-cold-source-schemas-grant','actual API terminal result differs')
  outcome={'schema_version':'lab-local-artifact-installation/v1','result':'PASS-fresh-installed-API-cold','archive_sha256':archive_pin,'package_manifest_sha256':package_pin,'repository':str(root),'ready_installation_receipt_sha256':ready['installation_receipt_sha256'],'native_source_cold_replays':2,'fresh_Context_built':True,'API_observation':observation,'full_regression_qualified':False,'authority_effect':'none'}
  C.atomic_control(private/'INSTALLATION-RESULT.json',C.encoded(outcome));return outcome
 finally:
  # This directory was created exclusively by this call. Published failed
  # runtime is retained for diagnosis; never delete an existing user target.
  shutil.rmtree(stage)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('archive_sha256');p.add_argument('package_sha256');p.add_argument('destination',type=Path);a=p.parse_args();print(json.dumps(install(a.archive,a.archive_sha256,a.package_sha256,a.destination),sort_keys=True),flush=True)
